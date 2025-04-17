# 采购单智能解析系统

## 项目简介
基于 PaddleOCR 和 DeepSeek API 的采购单信息提取工具，支持复杂表格结构解析与结构化数据导出。系统可以自动识别PDF文档中的表格内容，并将其转换为规范的Markdown格式和Excel文件。

## 环境要求
- Python 3.8+
- DeepSeek API 密钥

## 快速开始
### 1. 环境配置
```bash
# 创建虚拟环境（推荐）
conda create -n invoice_parser python=3.9
conda activate invoice_parser

# 安装依赖
pip install -r requirements.txt
```

### 2. API配置
1. 获取 DeepSeek API 密钥：
   - 访问 DeepSeek 官网注册账号
   - 在控制台获取 API 密钥

2. 配置 API 密钥：
   - 打开 `work.py` 文件
   - 找到 `TableExtractor` 类的 `__init__` 方法
   - 将 `self.api_key` 替换为您的 API 密钥：
     ```python
     self.api_key = "your-api-key-here"
     ```

### 3. 使用说明
```bash
# 将PDF文件放在程序同目录下，然后运行：
python work.py
```

程序会自动：
1. 处理PDF文件
2. 提取文本内容
3. 生成Markdown格式的表格（保存在 `output/table_data.md`）
4. 生成Excel文件（保存在 `output/table_data.xlsx`）

## 功能特性
- 自动识别PDF文档中的表格内容
- 使用 PaddleOCR 进行文字识别
- 智能表格结构重建
- 支持多页PDF处理
- 输出Markdown和Excel两种格式
- 自动处理表格对齐和格式化

## 目录结构
```
├── work.py                # 主程序
├── requirements.txt       # 依赖列表
├── output/               # 输出目录
│   ├── table_data.md     # Markdown格式表格
│   ├── table_data.xlsx   # Excel格式表格
│   └── raw_pdf_text.txt  # 原始PDF文本
└── 坤晟采购单231-2408000555.pdf  # 示例PDF文件
```

## 注意事项
1. 确保PDF文件清晰可读
2. 首次运行会自动下载PaddleOCR模型
3. 请妥善保管您的API密钥
4. 建议使用虚拟环境运行程序
5. 如果遇到识别问题，可以调整图像预处理参数

## 常见问题
1. API调用失败
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看API调用限制

2. 表格识别不准确
   - 检查PDF文件质量
   - 调整图像预处理参数
   - 确保PDF文件未加密

## 许可证
MIT License
```
**文档亮点**：
- 遵循标准开源README结构[[5]][[9]]
- 包含环境配置、快速启动、注意事项等实用信息
- 特别标注坐标调整和模型准备等关键步骤[[1]][[6]]
- 参考了依赖管理最佳实践[[8]][[10]]