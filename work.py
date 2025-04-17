import os
import fitz  # PyMuPDF
import requests
import json
import pandas as pd
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import io
from paddleocr import PaddleOCR
import re

class TableExtractor:
    def __init__(self):
        """初始化API配置"""
        self.api_key = "sk-gnrmcptblepcptqeigymctpsahtvonsjhlwvtvvvvezzcdpu"
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        # 初始化PaddleOCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch",use_gpu=True)  # 中文模型
        
    def extract_text_from_pdf(self, pdf_path):
        """从PDF中提取文本内容，使用PaddleOCR识别"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            # 获取PDF页数
            total_pages = len(doc)
            # print(f"PDF总页数: {total_pages}")
            
            for page_num, page in enumerate(doc, 1):
                # print(f"正在处理第 {page_num}/{total_pages} 页...")
                
                # 将PDF页面转换为图片
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # 转换为OpenCV格式
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # 图像预处理
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                
                # 使用PaddleOCR进行识别
                result = self.ocr.ocr(thresh, cls=True)
                
                # 添加页面标记和内容
                text += f"\n{'='*50}\n"
                text += f"第 {page_num} 页内容:\n"
                text += f"{'='*50}\n\n"
                
                # 处理识别结果
                if result:
                    for line in result[0]:
                        if line[1][0]:  # 确保有识别结果
                            text += line[1][0] + '\n'
                
                text += '\n'
            
            doc.close()
            
            # 打印提取的文本预览
            # print("\n提取的文本预览:")
            # print(text[:500] + "..." if len(text) > 500 else text)
            
            return text
        except Exception as e:
            raise Exception(f"PDF文件处理失败: {str(e)}")
        
    def call_deepseek_api(self, content,prompt):
        """调用DeepSeek API进行表格提取和排版"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        


        data = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {"role": "system", "content": "你是一个专业的表格提取和排版助手，负责从PDF文本中提取表格内容并转换为规范的Markdown格式。需要注意的是，文本中的表格并不一定是传统意义上的有框表格，也可能是几段规律的文字排版，请根据数据内容重新对齐标签名，并整理成规范的Markdown表格格式。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"调用DeepSeek API时出错: {str(e)}")
            return content  # 如果API调用失败，返回原始内容

    def md_to_excel(self, md_content, excel_path):
        """将Markdown表格转换为Excel文件"""
        try:
            # 移除可能的markdown标记
            content = md_content.strip()
            if content.startswith('```markdown'):
                content = content[10:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 移除文件开头的多余字符
            lines = content.split('\n')
            while lines and not lines[0].strip().startswith('|'):
                lines.pop(0)
            content = '\n'.join(lines)
            
            print("\n处理前的表格内容:")
            print(content)
            
            # 分割行
            lines = content.split('\n')
            
            # 移除空行
            lines = [line for line in lines if line.strip()]
            
            print("\n处理后的行数:", len(lines))
            
            # 提取表头
            header = lines[0].strip('|').split('|')
            header = [h.strip() for h in header]
            header = [h for h in header if h]  # 移除空列
            print("\n表头:", header)
            
            # 提取数据行
            data = []
            for line in lines[2:]:  # 跳过表头和分隔行
                if line.strip('|').strip():  # 确保不是空行
                    row = line.strip('|').split('|')
                    row = [cell.strip() for cell in row]
                    row = [cell for cell in row if cell]  # 移除空列
                    print("\n处理的行:", row)
                    if len(row) == len(header):  # 确保行数据与表头列数匹配
                        data.append(row)
            
            print("\n提取的数据行数:", len(data))
            
            if not data:
                print("警告：没有提取到有效的数据行！")
                return False
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=header)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(excel_path), exist_ok=True)
            
            # 保存为Excel文件
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"\nExcel文件已保存到: {excel_path}")
            
            # 验证文件是否成功创建
            if os.path.exists(excel_path):
                print(f"Excel文件大小: {os.path.getsize(excel_path)} 字节")
                return True
            else:
                print("Excel文件未能成功创建")
                return False
                
        except Exception as e:
            print(f"转换过程中出现错误: {str(e)}")
            print("表格内容预览:")
            print(content[:500] + "..." if len(content) > 500 else content)
            return False

    def process_document(self, pdf_path, output_path):
        """处理文档并保存结果"""
        print(f"\n开始处理PDF文件: {pdf_path}")
        
        # 从PDF中提取文本
        pdf_text = self.extract_text_from_pdf(pdf_path)
        
        # 保存原始PDF文本到文件
        raw_text_path = os.path.join(os.path.dirname(output_path), 'raw_pdf_text.txt')
        with open(raw_text_path, 'w', encoding='utf-8') as f:
            f.write(pdf_text)
        print(f"\n原始PDF文本已保存到: {raw_text_path}")
        
        # 调用DeepSeek API进行表格提取和排版
        print("\n正在调用API处理文本...")
        formatted_table = self.call_deepseek_api(pdf_text)
        print(formatted_table)
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 处理API返回的内容，移除markdown标记
        formatted_table = formatted_table.strip()
        if formatted_table.startswith('```markdown'):
            formatted_table = formatted_table[10:]
        if formatted_table.endswith('```'):
            formatted_table = formatted_table[:-3]
        formatted_table = formatted_table.strip()
        
        # 替换"备注"为"采购单位"
        formatted_table = formatted_table.replace("备注", "采购单位")
        
        # 保存排版后的内容到Markdown文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_table)
            
        # 转换为Excel文件
        excel_path = os.path.join(output_dir, 'table_data.xlsx')
        print(f"\n正在将Markdown表格转换为Excel文件...")
        print(f"Excel文件将保存到: {excel_path}")
        
        if self.md_to_excel(formatted_table, excel_path):
            self.process_excel_file(file_path = "./output/table_data.xlsx")
            print("Excel转换完成！")
        else:
            print("Excel转换失败！")
            
        return formatted_table
    
    def format_datetime(self,datetime_str):
        if re.search(r'\d{2}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}', datetime_str):
            return datetime_str
        
        # 使用正则表达式匹配并添加空格
        return re.sub(r'(\d{2}/\d{2}/\d{2})(\d{2}:\d{2}:\d{2})', r'\1 \2', datetime_str)

    def split_instrument_name(self, name):
        """
        将仪器名称分割成两部分：主要名称和编号
        例如：'F1064003-3弧臂5成品组合检具S1' -> ('F1064003-3弧臂5成品组合检具', 'S1')
        
        Args:
            name (str): 要分割的仪器名称
            
        Returns:
            tuple: (主要名称, 编号) 如果匹配成功，否则返回 (原字符串, '')
        """
        # 使用正则表达式匹配最后一部分的字母数字组合
        pattern = r'^(.*?)([A-Za-z]\d*)$'
        match = re.match(pattern, name)
        
        if match:
            return match.group(1).strip(), match.group(2)
        else:
            return name, ''

    def process_excel_file(self,file_path, output_path=None):
        """
        处理Excel文件中的采购日期列
        
        Args:
            file_path (str): 输入Excel文件路径
            output_path (str, optional): 输出Excel文件路径，默认为在原文件名后添加"_formatted"
        """
        print(f"filepath {file_path}")
        # 如果未指定输出路径，则创建默认输出路径
        if output_path is None:
            file_name, file_ext = os.path.splitext(file_path)
            # print
            output_path = f"{file_name}_formatted{file_ext}"
        
        try:
            # 读取Excel文件
            print(f"正在读取文件: {file_path}")
            df = pd.read_excel(file_path)
            
            # 检查是否存在"采购日期"列
            if "采购日期" not in df.columns:
                print("错误: 未找到'采购日期'列")
                return False
            
            # 记录原始值和转换后的值，用于显示变化
            changes = []
            
            # 转换"采购日期"列中的每个值
            print("正在处理'采购日期'列...")
            for i in range(len(df)):
                original_value = df.at[i, "采购日期"]
                formatted_value = self.format_datetime(original_value)
                
                # 如果值发生了变化，记录下来
                if original_value != formatted_value:
                    changes.append((i+2, original_value, formatted_value))  # i+2 是Excel行号（考虑标题行和从1开始计数）
                
                # 更新DataFrame中的值
                df.at[i, "采购日期"] = formatted_value
            
            # 保存处理后的Excel文件
            print(f"正在保存处理后的文件: {output_path}")
            df.to_excel(output_path, index=False)
            
            # 显示变化的统计信息
            print(f"\n处理完成! 共修改了 {len(changes)} 个日期时间格式")
            
            # 显示前10个变化的详细信息
            if changes:
                print("\n前10个修改的详细信息:")
                for i, (row, old, new) in enumerate(changes[:10]):
                    print(f"行 {row}: '{old}' -> '{new}'")
            
            return True
            
        except Exception as e:
            print(f"处理文件时发生错误: {str(e)}")
            return False
def main():
    # 创建输出目录
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 初始化提取器
    extractor = TableExtractor()
    
    # 处理PDF文件
    pdf_path = 'jiaojiao.pdf'
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

if __name__ == "__main__":
    main()
