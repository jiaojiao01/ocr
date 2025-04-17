import pandas as pd
import os
import re

def md_to_excel(md_file_path, excel_file_path):
    """将Markdown表格转换为Excel文件"""
    try:
        # 读取Markdown文件
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除可能的markdown标记
        content = content.strip()
        if content.startswith('```markdown'):
            content = content[10:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # 分割行
        lines = content.split('\n')
        
        # 移除空行
        lines = [line for line in lines if line.strip()]
        
        # 提取表头
        header = lines[0].strip('|').split('|')
        header = [h.strip() for h in header]
        
        # 提取数据行
        data = []
        for line in lines[2:]:  # 跳过表头和分隔行
            if line.strip('|').strip():  # 确保不是空行
                row = line.strip('|').split('|')
                row = [cell.strip() for cell in row]
                data.append(row)
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=header)
        
        # 保存为Excel文件
        df.to_excel(excel_file_path, index=False, engine='openpyxl')
        print(f"\nExcel文件已保存到: {excel_file_path}")
        
        return True
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return False

def main():
    # 设置输入输出路径
    input_dir = 'output'
    md_file = 'table_data.md'
    excel_file = 'table_data.xlsx'
    
    md_path = os.path.join(input_dir, md_file)
    excel_path = os.path.join(input_dir, excel_file)
    
    # 检查输入文件是否存在
    if not os.path.exists(md_path):
        print(f"错误: Markdown文件不存在: {md_path}")
        return
    
    # 转换文件
    if md_to_excel(md_path, excel_path):
        print("转换完成！")
    else:
        print("转换失败！")

if __name__ == "__main__":
    main() 