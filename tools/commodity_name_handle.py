import re
def split_instrument_name(name):
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


def extract_purchase_order_no(text):
    """
    从字符串中提取采购单号
    例如: "231-2408000555国内采购单" -> "231-2408000555"
    """
    # 使用正则表达式匹配采购单号格式
    import re
    pattern = r'(\d+-\d+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None


def extract_basic_unit(unit_str):
    """
    从单位字符串中提取基本单位
    例如: "PCS(个、台、块、辆)" -> "PCS"
    """
    # 使用正则表达式匹配基本单位
    import re
    pattern = r'^([A-Za-z]+)'
    match = re.search(pattern, unit_str)
    if match:
        return match.group(1)
    return unit_str  