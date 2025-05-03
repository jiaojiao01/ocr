from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import asyncio
from typing import Dict
from pathlib import Path
import logging
import time
from datetime import datetime, timedelta
import aiofiles
from starlette.middleware.base import BaseHTTPMiddleware
from ocr.work import TableExtractor 
app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 自定义请求日志中间件
class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 记录请求详情
        client_host = "未知"
        if request.client:
            client_host = f"{request.client.host}:{request.client.port}"
            
        logger.info(f"[{request_id}] 收到请求: {request.method} {request.url}")
        logger.info(f"[{request_id}] 请求路径: {request.url.path}")
        logger.info(f"[{request_id}] 原始路径: {request.scope.get('raw_path', b'').decode('utf-8', errors='replace')}")
        logger.info(f"[{request_id}] 客户端: {client_host}")
        logger.info(f"[{request_id}] 请求头: {dict(request.headers)}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应时间
        process_time = time.time() - start_time
        logger.info(f"[{request_id}] 响应状态: {response.status_code}")
        logger.info(f"[{request_id}] 处理时间: {process_time:.3f}秒")
        
        return response

# 添加中间件
app.add_middleware(RequestLoggerMiddleware)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储上传任务的状态
upload_tasks: Dict[str, Dict] = {}

# 上传文件保存路径
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
# UPLOAD_DIR.mkdir(exist_ok=True,parents=True)
try:
    UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
    logger.info(f"上传目录已创建或已存在: {UPLOAD_DIR.absolute()}")
except Exception as e:
    logger.error(f"无法创建上传目录: {str(e)}")
# 分块大小（8MB）
CHUNK_SIZE = 8*1024*1024


async def process_file_upload(file_content: bytes, task_id: str, file_path: Path):
    """后台处理文件上传"""
    try:
        upload_tasks[task_id].update({
            "status": "uploading",
            "progress": 0
        })
        
        # 获取文件大小
        file_size = len(file_content)
        
        # 分块写入文件
        async with aiofiles.open(file_path, "wb") as buffer:
            uploaded_size = 0
            chunk_size = CHUNK_SIZE  # 使用定义的块大小
            
            for i in range(0, file_size, chunk_size):
                chunk = file_content[i:i+chunk_size]
                await buffer.write(chunk)
                
                # 更新上传进度
                uploaded_size += len(chunk)
                progress = min(100, int((uploaded_size / file_size) * 100))
                # logger.info(progress)
                upload_tasks[task_id].update({
                    "progress": progress,
                    "uploaded_size": uploaded_size
                })
                
                # 让出控制权,避免阻塞
                await asyncio.sleep(0)
        
        # 文件写入完成后，更新状态为completed
        upload_tasks[task_id].update({
            "status": "completed",
            "completed_at": datetime.now(),
            "progress": 100
        })
        
        logger.info(f"文件上传完成: {file_path}")
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}")
        try:
            if file_path.exists():
                await asyncio.to_thread(file_path.unlink)
                logger.info(f"已删除不完整文件: {file_path}")
        except Exception as cleanup_error:
            logger.error(f"清理文件失败: {str(cleanup_error)}")


@app.post("/api/upload/pdf")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), task_id: str = Form(...)):
    logger.info(f"收到上传请求，task_id: {task_id}, 文件大小: {file.size} bytes")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    if not task_id or task_id not in upload_tasks:
        raise HTTPException(status_code=400, detail="无效的任务ID")
    
    try:
        # 先读取整个文件内容到内存
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"成功读取文件内容，大小: {file_size} bytes")
        
        file_path = UPLOAD_DIR / f"{task_id}.pdf"
        upload_tasks[task_id].update({
            "file_path": str(file_path),
            "status": "uploading",
            "total_size": file_size,
            "uploaded_size": 0
        })
        
        # 将文件内容传递给后台任务
        await process_file_upload(file_content, task_id, file_path)

        # return {"success": True, "message": "文件上传已开始处理"}
    except Exception as e:
        logger.error(f"准备上传文件失败: {str(e)}")
        upload_tasks[task_id].update({
            "status": "failed",
            "last_error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"文件上传准备失败: {str(e)}")
    #接下来处理PO单的核心逻辑
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 初始化提取器
    extractor = TableExtractor()
    
    # 处理PDF文件
    pdf_path = file_path
    output_path = os.path.join(output_dir, 'table_data.md')
    
    try:
        # 处理文档
        formatted_table = extractor.process_document(pdf_path, output_path)
       
        print(f"\nMarkdown格式的表格数据已保存到: {output_path}")
        print("\nMarkdown格式的表格内容预览:")
        print(formatted_table)
    except FileNotFoundError as e:
        print(f"错误: {str(e)}")
        print("请确保PDF文件存在于正确的路径中。")
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")

@app.post("/api/upload/zip")
async def upload_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...), task_id = Form(...)):
    allowed_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    if not task_id or task_id not in upload_tasks:
        raise HTTPException(status_code=400, detail="无效的任务ID")
    
    try:
        # 先读取整个文件内容到内存
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"成功读取文件内容，大小: {file_size} bytes")
        
        file_path = UPLOAD_DIR / f"{task_id}{file_ext}"
        upload_tasks[task_id].update({
            "file_path": str(file_path),
            "status": "uploading",
            "total_size": file_size,
            "uploaded_size": 0
        })
        
        # 将文件内容传递给后台任务
        background_tasks.add_task(process_file_upload, file_content, task_id, file_path)
        return {"success": True, "message": "文件上传已开始处理"}
    except Exception as e:
        logger.error(f"准备上传文件失败: {str(e)}")
        upload_tasks[task_id].update({
            "status": "failed",
            "last_error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"文件上传准备失败: {str(e)}")



@app.post("/api/upload/create_task")
async def create_task():
    task_id = str(uuid.uuid4())
    upload_tasks[task_id] = {
        "status": "created",
        "progress": 0,
        "file_path": None,
        "created_at": datetime.now(),
        "total_size": 0,
        "uploaded_size": 0
    }
    logger.info(f"创建新任务: {task_id}")
    return {"success": True, "task_id": task_id}


    logger.info(f"收到上传请求，task_id: {task_id}, 文件大小: {file.size} bytes")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    if not task_id or task_id not in upload_tasks:
        raise HTTPException(status_code=400, detail="无效的任务ID")
    
    try:
        # 先读取整个文件内容到内存
        file_content = await file.read()
        file_size = len(file_content)
        logger.info(f"成功读取文件内容，大小: {file_size} bytes")
        
        file_path = UPLOAD_DIR / f"{task_id}.pdf"
        upload_tasks[task_id].update({
            "file_path": str(file_path),
            "status": "uploading",
            "total_size": file_size,
            "uploaded_size": 0
        })
        
        # 将文件内容传递给后台任务
        background_tasks.add_task(process_file_upload, file_content, task_id, file_path)
        return {"success": True, "message": "文件上传已开始处理"}
    except Exception as e:
        logger.error(f"准备上传文件失败: {str(e)}")
        upload_tasks[task_id].update({
            "status": "failed",
            "last_error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"文件上传准备失败: {str(e)}")

@app.post("/api/upload/zip")
async def upload_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...), task_id = Form(...)):
    allowed_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    if not task_id or task_id not in upload_tasks:
        raise HTTPException(status_code=400, detail="无效的任务ID")
    
    file_path = UPLOAD_DIR / f"{task_id}{file_ext}"
    upload_tasks[task_id].update({
        "file_path": str(file_path),
        "status": "uploading",
        "total_size": file.size,
        "uploaded_size": 0
    })
    
    # 将文件处理放到后台任务中
    background_tasks.add_task(process_file_upload, file, task_id, file_path)
    
    # 立即返回成功响应
    return {"success": True, "message": "文件上传已开始处理"}

@app.get("/api/upload/{task_id}/status")
async def get_upload_status(task_id: str):
    request_start_time = time.time()
    logger.info(f"收到状态检查请求 - 任务ID: {task_id}, 时间: {datetime.now().isoformat()}")
    
    if task_id not in upload_tasks:
        logger.error(f"状态检查失败 - 任务ID不存在: {task_id}")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = upload_tasks[task_id]
    logger.info(f"任务状态: {task['status']}, 进度: {task.get('progress', 0)}%, 创建时间: {task.get('created_at', '未知')}")
    
    process_time = time.time() - request_start_time
    logger.info(f"状态检查处理完成 - 任务ID: {task_id}, 耗时: {process_time:.3f}秒")
    
    return {
        "success": True,
        "status": task
    }

@app.post("/api/upload/{task_id}/pause")
async def pause_upload(task_id: str):
    logger.info(f"收到暂停请求，task_id: {task_id}")
    
    if task_id not in upload_tasks:
        logger.error(f"任务 {task_id} 不存在")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    current_status = upload_tasks[task_id]["status"]
    logger.info(f"任务当前状态: {current_status}")
    
    if current_status != "uploading":
        logger.warning(f"任务状态 {current_status} 无法暂停")
        raise HTTPException(status_code=400, detail="任务当前状态无法暂停")
    
    upload_tasks[task_id]["status"] = "paused"
    logger.info(f"任务已暂停，新状态: {upload_tasks[task_id]['status']}")
    return {"success": True}

@app.post("/api/upload/{task_id}/resume")
async def resume_upload(task_id: str):
    if task_id not in upload_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if upload_tasks[task_id]["status"] != "paused":
        raise HTTPException(status_code=400, detail="任务当前状态无法恢复")
    
    upload_tasks[task_id]["status"] = "uploading"
    return {"success": True}

@app.post("/api/upload/{task_id}/cancel")
async def cancel_upload(task_id: str):
    request_start_time = time.time()
    logger.info(f"收到取消请求 - 任务ID: {task_id}, 时间: {datetime.now().isoformat()}")
    
    if task_id not in upload_tasks:
        logger.error(f"取消请求失败 - 任务ID不存在: {task_id}")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = upload_tasks[task_id]
    logger.info(f"任务当前状态: {task['status']}")
    
    if task["status"] in ["completed", "failed", "cancelled"]:
        logger.warning(f"取消请求失败 - 任务状态无法取消: {task['status']}")
        raise HTTPException(status_code=400, detail="任务当前状态无法取消")
    
    try:
        file_path = Path(task["file_path"])
        if file_path.exists():
            logger.info(f"删除文件: {file_path}")
            await asyncio.to_thread(file_path.unlink)
            logger.info(f"文件删除成功: {file_path}")
        else:
            logger.warning(f"文件不存在，无需删除: {file_path}")
    except Exception as e:
        logger.error(f"删除文件失败: {e}")
    
    upload_tasks[task_id].update({
        "status": "cancelled",
        "completed_at": datetime.now().isoformat(),
        "progress": 0
    })
    
    process_time = time.time() - request_start_time
    logger.info(f"取消请求处理完成 - 任务ID: {task_id}, 耗时: {process_time:.3f}秒")
    
    return {"success": True}


async def cleanup_expired_tasks():
    logger.info("启动过期任务清理服务")
    while True:
        try:
            current_time = datetime.now()
            tasks_to_remove = []
            
            for task_id, task_data in upload_tasks.items():
                created_at = task_data.get("created_at")
                if created_at and current_time - created_at > timedelta(minutes=30):
                    status = task_data.get("status")
                    if status in ["created", "uploading"]:
                        logger.warning(f"任务 {task_id} 已超时 (状态: {status})")
                        
                        file_path = task_data.get("file_path")
                        if file_path:
                            path = Path(file_path)
                            if path.exists():
                                try:
                                    await asyncio.to_thread(path.unlink)
                                    logger.info(f"已删除超时任务文件: {file_path}")
                                except Exception as e:
                                    logger.error(f"删除文件失败: {e}")
                        
                        upload_tasks[task_id].update({
                            "status": "cancelled",
                            "cancel_reason": "timeout",
                            "progress": 0
                        })
                
                if task_data.get("status") in ["completed", "cancelled", "failed"]:
                    completed_at = task_data.get("completed_at", created_at)
                    if completed_at and current_time - completed_at > timedelta(days=1):
                        tasks_to_remove.append(task_id)
            
            for task_id in tasks_to_remove:
                upload_tasks.pop(task_id, None)
                logger.info(f"已移除过期任务: {task_id}")
            
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"清理任务出错: {e}")
            await asyncio.sleep(60)


    """调试路由，返回请求的详细信息"""
    logger.info("调试路由被访问")
    
    # 获取请求体
    body = None
    try:
        body = await request.body()
        if body:
            body = body.decode('utf-8')
    except Exception as e:
        body = f"无法读取请求体: {str(e)}"
    
    # 收集请求信息
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "client": {
            "host": request.client.host if request.client else None,
            "port": request.client.port if request.client else None
        },
        "cookies": request.cookies,
        "body": body
    }
    
    logger.info(f"调试路由返回信息: {request_info}")
    
    return {
        "request_info": request_info,
        "server_time": datetime.now().isoformat(),
        "app_root_path": app.root_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)