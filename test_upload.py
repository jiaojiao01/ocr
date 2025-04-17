import requests
import time
import os
import asyncio
import aiofiles
from pathlib import Path

def create_test_file(size_mb=100):
    """创建指定大小的测试文件"""
    file_path = Path("test_upload.pdf")
    with open(file_path, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))
    return file_path

async def test_write_speed(file_path, chunk_size=8*1024*1024):
    """测试文件写入速度"""
    test_file = Path("test_write.pdf")
    total_size = os.path.getsize(file_path)
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"\n开始测试文件写入速度:")
    print(f"文件大小: {total_size_mb:.2f} MB")
    print(f"分块大小: {chunk_size/1024/1024:.2f} MB")
    
    start_time = time.time()
    total_written = 0
    
    try:
        async with aiofiles.open(test_file, "wb") as buffer:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    await buffer.write(chunk)
                    total_written += len(chunk)
                    progress = (total_written / total_size) * 100
                    print(f"写入进度: {progress:.1f}% ({total_written/1024/1024:.1f} MB / {total_size_mb:.1f} MB)")
                    # 让出控制权，模拟实际写入场景
                    await asyncio.sleep(0)
    except Exception as e:
        print(f"写入测试出错: {str(e)}")
        return 0
    finally:
        end_time = time.time()
        duration = end_time - start_time
        speed = total_size / duration / 1024 / 1024  # MB/s
        
        print(f"\n写入测试结果:")
        print(f"总写入大小: {total_size_mb:.2f} MB")
        print(f"写入时间: {duration:.2f} 秒")
        print(f"写入速度: {speed:.2f} MB/s")
        
        # 清理测试文件
        if test_file.exists():
            os.remove(test_file)
        return speed

def test_upload_speed(file_path):
    """测试上传速度"""
    # 1. 创建任务
    create_task_url = "http://localhost:8000/api/upload/create_task"
    response = requests.post(create_task_url)
    if not response.ok:
        print("创建任务失败")
        return
    
    task_id = response.json()["task_id"]
    print(f"创建任务成功，task_id: {task_id}")
    
    # 2. 上传文件
    upload_url = "http://localhost:8000/api/upload/pdf"
    files = {
        "file": ("test.pdf", open(file_path, "rb"), "application/pdf"),
        "task_id": (None, task_id)
    }
    
    start_time = time.time()
    response = requests.post(upload_url, files=files)
    end_time = time.time()
    
    if response.ok:
        print("上传请求成功")
        file_size = os.path.getsize(file_path)
        duration = end_time - start_time
        speed = file_size / duration / 1024 / 1024  # MB/s
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"上传时间: {duration:.2f} 秒")
        print(f"上传速度: {speed:.2f} MB/s")
    else:
        print(f"上传失败: {response.text}")
    
    # 3. 检查状态
    status_url = f"http://localhost:8000/api/upload/{task_id}/status"
    while True:
        response = requests.get(status_url)
        if response.ok:
            status = response.json()["status"]
            print(f"当前状态: {status['status']}, 进度: {status.get('progress', 0)}%")
            if status["status"] in ["completed", "failed", "cancelled"]:
                break
        time.sleep(1)

async def main():
    # 创建100MB的测试文件
    test_file = create_test_file(100)
    print(f"创建测试文件: {test_file}")
    
    # 测试上传速度
    print("\n=== 测试上传速度 ===")
    test_upload_speed(test_file)
    
    # 测试写入速度
    print("\n=== 测试写入速度 ===")
    write_speed = await test_write_speed(test_file)
    
    # 清理测试文件
    os.remove(test_file)
    print("\n测试完成，已清理测试文件")

if __name__ == "__main__":
    asyncio.run(main()) 