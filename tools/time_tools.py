from datetime import datetime, date
from pytz import timezone

def to_china_time(dt: datetime) -> datetime:
    """将 UTC 时间转换为北京时间"""
    print(dt.tzinfo)
    if dt.tzinfo is None:
        # 如果没有时区信息，假设它是 UTC
        dt = timezone('UTC').localize(dt)
    return dt.astimezone(timezone('Asia/Shanghai'))

def convert_date_format(date_str: str) -> date:
    """
    将日期字符串转换为 date 对象，只保留日期部分
    
    Args:
        date_str (str): 输入的日期字符串，格式为 "DD/MM/YY"
        
    Returns:
        date: 转换后的日期对象（不包含时间）
    """
    try:
        # 解析输入日期并只返回日期部分
        return datetime.strptime(date_str, "%d/%m/%y").date()
    except ValueError as e:
        print(f"日期格式错误: {e}")
        # 如果解析失败，返回当前日期
        return datetime.now().date()
