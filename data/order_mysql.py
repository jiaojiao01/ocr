from tortoise import Tortoise, fields
from tortoise.models import Model
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from order.order_info import extract_supplier_info,extract_customer_info,extract_commodities,extract_order_info
from datetime import datetime
from tools.time_tools import to_china_time

class Order(Model):
    purchase_order_no = fields.CharField(max_length=50, unique=True)  # 采购单号
    purchase_date = fields.CharField(max_length=50)  # 采购日期
    payment_terms = fields.CharField(max_length=100)  # 付款条件
    tax_type = fields.CharField(max_length=50)  # 税种
    currency = fields.CharField(max_length=20)  # 币种
    total_before_tax = fields.DecimalField(max_digits=18, decimal_places=6, default=0)  # 税前金额合计
    total_after_tax = fields.DecimalField(max_digits=18, decimal_places=6, default=0)  # 税后金额合计
    total_vat = fields.DecimalField(max_digits=18, decimal_places=6, default=0)  # 增值税税额合计

    class Meta:
        table = "order"  # 可以自定义表名，默认情况下使用类名作为表名
    
    @property
    def created_at_local(self) -> datetime:
        print(123456)
        return to_china_time(self.created_at)

    @property
    def updated_at_local(self) -> datetime:
        return to_china_time(self.updated_at)
    

    def __str__(self):
        return f"订单号: {self.purchase_order_no}, 日期: {self.purchase_date}"

async def main():
    # 初始化连接
    await Tortoise.init(
        db_url = "mysql://root:12345678@localhost:10001/statement?charset=utf8mb4",
        modules={'models': ['__main__']}
    )
    xlsl_url = "../output/table_data_formatted.xlsx"
    await Tortoise.generate_schemas()
    commodity_list = extract_commodities(xlsl_url)
    customer_info = extract_customer_info(xlsl_url) 
    supplier_info = extract_supplier_info(xlsl_url)
    order_info = extract_order_info(xlsl_url,customer_info,supplier_info,commodity_list)
    order_info_pr = order_info.pr_attributes(["customer","supplier","items"])
    
    order = await Order.create(
        **order_info_pr.__dict__
    )
    print(order)
asyncio.run(main())
