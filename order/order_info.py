import pandas as pd
from typing import Dict, List, Any
import numpy as np
from decimal import Decimal
# 客户信息类
class Customer:
    def __init__(self, customer_name,customer_address, customer_phone, customer_fax):
        self.customer_name = customer_name    # 客户公司名称
        self.customer_address = customer_address              # 客户地址
        self.customer_phone = customer_phone                  # 客户电话
        self.customer_fax = customer_fax                      # 客户传真
    
    def __str__(self):
        attrs = []
        for attr, value in self.__dict__.items():
            attrs.append(f"{attr}: {value}")
        return "\n".join(attrs)


# 供应商信息类
class Supplier:
    def __init__(self, supplier_code, supplier_name, supplier_address, supplier_phone, supplier_contact_person):
        self.supplier_code = supplier_code                        # 供应厂商代号
        self.supplier_name = supplier_name                        # 供应厂商名称
        self.supplier_address = supplier_address                  # 供应厂商地址
        self.supplier_phone = supplier_phone                      # 供应商电话
        self.supplier_contact_person = supplier_contact_person    # 供应商联系人
    
    def __str__(self):
        attrs = []
        for attr, value in self.__dict__.items():
            attrs.append(f"{attr}: {value}")
        return "\n".join(attrs)


# 商品信息类
class Commodity:
    def __init__(self, item_no, material_no, product_name, specification, 
                 pricing_unit, pricing_quantity, price_before_tax, amount_before_tax,
                 delivery_date, requisition_no, purchase_quantity, price_with_tax,
                 amount_with_tax, purchase_unit):
        self.item_no = item_no                          # 项次
        self.material_no = material_no                  # 料件编号
        self.product_name = product_name                # 品名(MPN)
        self.specification = specification              # 规格
        self.pricing_unit = pricing_unit                # 计价单位
        self.pricing_quantity = pricing_quantity        # 计价数量
        self.price_before_tax = price_before_tax        # 税前单价
        self.amount_before_tax = amount_before_tax      # 税前金额
        self.delivery_date = delivery_date              # 交货日
        self.requisition_no = requisition_no            # 请购单号
        self.purchase_quantity = purchase_quantity      # 采购数量
        self.price_with_tax = price_with_tax            # 含税单价
        self.amount_with_tax = amount_with_tax          # 含税金额
        self.purchase_unit = purchase_unit              # 采购单位
    
    def __str__(self):
        attrs = []
        for attr, value in self.__dict__.items():
            attrs.append(f"{attr}: {value}")
        return "\n".join(attrs)


# 订单信息类
class Order:
    def __init__(self, purchase_order_no, purchase_date, payment_terms, tax_type, currency,
                 customer, supplier, total_before_tax=0, total_after_tax=0, total_vat=0):
        self.purchase_order_no = purchase_order_no  # 采购单号
        self.purchase_date = purchase_date          # 采购日期
        self.payment_terms = payment_terms          # 付款条件
        self.tax_type = tax_type                    # 税种
        self.currency = currency                    # 币种
        self.customer = customer                    # 客户信息
        self.supplier = supplier                    # 供应商信息
        self.total_before_tax = total_before_tax    # 税前金额合计
        self.total_after_tax = total_after_tax      # 税后金额合计
        self.total_vat = total_vat                  # 增值税税额合计
        self.items = []                             # 订单项目列表
    
    def add_item(self, commodity):
        """添加商品到订单项目列表中"""
        self.items.append(commodity)
    
    def __str__(self):
        attrs = []
        for attr, value in self.__dict__.items():
            attrs.append(f"{attr}: {value}")
        return "\n".join(attrs)

def extract_supplier_info(excel_file_path: str) -> Supplier:
    """
    从Excel文件中提取供应商信息
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        Supplier对象
    """
    # 读取Excel文件
    df = pd.read_excel(excel_file_path, header=None)
    
    # 检查数据是否至少有两行（表头行和数据行）
    if len(df) < 2:
        raise ValueError("Excel文件至少需要包含表头行和一行数据")
    
    # 获取表头行和数据行
    header_row = df.iloc[0]
    data_row = df.iloc[1]
    
    # 供应商字段映射
    supplier_fields = {
        "供应厂商代号": "supplier_code",
        "供应厂商公司名称": "supplier_name",
        "供应厂商地址": "supplier_address",
        "供应商电话": "supplier_phone",
        "供应商联系人": "supplier_contact_person"
    }
    
    # 提取供应商信息
    supplier_data = {
        "supplier_code": "未知代号",
        "supplier_name": "未知供应商",
        "supplier_address": "未知地址",
        "supplier_phone": "未知电话",
        "supplier_contact_person": "未知联系人"
    }
    
    # 查找并提取供应商信息
    for i, header in enumerate(header_row):
        if isinstance(header, str) and header in supplier_fields:
            value = data_row[i]
            if pd.notna(value):  # 检查值是否为NaN
                field_name = supplier_fields[header]
                supplier_data[field_name] = value
    
    # 创建并返回供应商对象
    return Supplier(**supplier_data)

def extract_customer_info(excel_file_path: str) -> Customer:
    """
    从Excel文件中提取客户信息
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        Customer对象
    """
    # 读取Excel文件
    df = pd.read_excel(excel_file_path, header=None)
    
    # 检查数据是否至少有两行（表头行和数据行）
    if len(df) < 2:
        raise ValueError("Excel文件至少需要包含表头行和一行数据")
    
    # 获取表头行和数据行
    header_row = df.iloc[0]
    data_row = df.iloc[1]
    
    # 客户字段映射
    customer_fields = {
        "客户公司名称": "customer_name",
        "客户地址": "customer_address",
        "客户电话": "customer_phone",
        "客户传真": "customer_fax"
    }
    
    # 提取客户信息
    customer_data = {
        "customer_name": "未知公司",
        "customer_address": "未知地址",
        "customer_phone": "未知电话",
        "customer_fax": "未知传真"
    }
    
    # 查找并提取客户信息
    for i, header in enumerate(header_row):
        if isinstance(header, str) and header in customer_fields:
            value = data_row[i]
            if pd.notna(value):  # 检查值是否为NaN
                field_name = customer_fields[header]
                customer_data[field_name] = value
    
    # 创建并返回客户对象
    return Customer(**customer_data)

def extract_commodities(excel_file_path: str) -> List[Commodity]:
    """
    从Excel文件中提取商品信息（可能有多行）
    
    Args:
        excel_file_path: Excel文件路径
        
    Returns:
        Commodity对象列表
    """
    # 读取Excel文件
    df = pd.read_excel(excel_file_path, header=None)
    
    # 检查数据是否至少有两行（表头行和至少一行数据）
    if len(df) < 2:
        raise ValueError("Excel文件至少需要包含表头行和一行数据")
    
    # 获取表头行
    header_row = df.iloc[0]
    
    # 商品字段映射
    commodity_fields = {
        "项次": "item_no",
        "料件编号": "material_no",
        "品名(MPN)": "product_name",
        "规格": "specification",
        "计价单位": "pricing_unit",
        "计价数量": "pricing_quantity",
        "税前单价": "price_before_tax",
        "税前金额": "amount_before_tax",
        "交货日": "delivery_date",
        "请购单号": "requisition_no",
        "采购数量": "purchase_quantity",
        "含税单价": "price_with_tax",
        "含税金额": "amount_with_tax",
        "采购单位": "purchase_unit"
    }
    
    # 创建表头索引映射
    header_indices = {}
    for i, header in enumerate(header_row):
        if isinstance(header, str) and header in commodity_fields:
            header_indices[commodity_fields[header]] = i
    
    # 从第二行开始提取商品信息
    commodities = []
    for row_idx in range(1, len(df)):
        data_row = df.iloc[row_idx]
        
        # 检查这一行是否包含商品信息（通常检查关键字段是否有值）
        # 这里我们检查料件编号或品名是否有值
        material_no_idx = header_indices.get("material_no", -1)
        product_name_idx = header_indices.get("product_name", -1)
        
        has_material_no = material_no_idx >= 0 and pd.notna(data_row[material_no_idx])
        has_product_name = product_name_idx >= 0 and pd.notna(data_row[product_name_idx])
        
        if not (has_material_no or has_product_name):
            # 如果既没有料件编号也没有品名，则跳过这一行
            continue
        
        # 提取商品信息
        commodity_data = {
            "item_no": "",
            "material_no": "",
            "product_name": "",
            "specification": "",
            "pricing_unit": "",
            "pricing_quantity": 0,
            "price_before_tax": 0,
            "amount_before_tax": 0,
            "delivery_date": None,
            "requisition_no": "",
            "purchase_quantity": 0,
            "price_with_tax": 0,
            "amount_with_tax": 0,
            "purchase_unit": ""
        }
        
        # 从数据行中提取值
        for field, idx in header_indices.items():
            value = data_row[idx]
            if pd.notna(value):
                # 根据字段类型进行转换
                if field in ["pricing_quantity", "price_before_tax", "amount_before_tax", 
                             "purchase_quantity", "price_with_tax", "amount_with_tax"]:
                    try:
                        # print(f"Converting field {field} with value: {value} (type: {type(value)})")
                        if isinstance(value, str):
                            value = value.strip().replace(',', '')
                        commodity_data[field] = Decimal(str(value))
                    except (ValueError, TypeError, decimal.InvalidOperation):
                        print(f"Failed to convert value for field {field}")     
                        commodity_data[field] = Decimal('0')
                else:
                    commodity_data[field] = str(value)
        
        # 创建商品对象并添加到列表
        commodity = Commodity(**commodity_data)
        commodities.append(commodity)
    
    return commodities

def extract_order_info(excel_file_path: str, customer: Customer, supplier: Supplier, commodities: List[Commodity]) -> Order:
    """
    从Excel文件中提取订单信息，并关联客户、供应商和商品信息
    
    Args:
        excel_file_path: Excel文件路径
        customer: 客户对象
        supplier: 供应商对象
        commodities: 商品对象列表
        
    Returns:
        Order对象
    """
    # 读取Excel文件
    df = pd.read_excel(excel_file_path, header=None)
    
    # 检查数据是否至少有两行（表头行和数据行）
    if len(df) < 2:
        raise ValueError("Excel文件至少需要包含表头行和一行数据")
    
    # 获取表头行和数据行
    header_row = df.iloc[0]
    data_row = df.iloc[1]
    
    # 订单字段映射
    order_fields = {
        "采购单号": "purchase_order_no",
        "采购日期": "purchase_date",
        "付款条件": "payment_terms",
        "税种": "tax_type",
        "币种": "currency",
        "税前金额合计": "total_before_tax",
        "税后金额合计": "total_after_tax",
        "增值税税额合计": "total_vat"
    }
    
    # 提取订单信息
    order_data = {
        "purchase_order_no": "未知单号",
        "purchase_date": "未知日期",
        "payment_terms": "未知付款条件",
        "tax_type": "未知税种",
        "currency": "未知币种",
        "customer": customer,
        "supplier": supplier
    }
    
    # 查找并提取订单信息
    for i, header in enumerate(header_row):
        if isinstance(header, str) and header in order_fields:
            value = data_row[i]
            field_name = order_fields[header]
            if pd.notna(value):  # 检查值是否为NaN
                order_data[field_name] = value
    
    # 创建订单对象
    order = Order(**order_data)
    
    # 将商品添加到订单中
    for commodity in commodities:
        order.add_item(commodity)
    
    return order


def extract_all_info(excel_file_path: str) -> Order:
    customer = extract_customer_info(excel_file_path)
    supplier = extract_supplier_info(excel_file_path)
    commodities = extract_commodities(excel_file_path)
    order = extract_order_info(excel_file_path, customer, supplier, commodities)
    return order

