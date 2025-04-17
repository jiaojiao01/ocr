from tortoise import Tortoise, fields
from tortoise.models import Model
import asyncio
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from order.order_info import extract_commodities
from datetime import datetime
from tools.time_tools import to_china_time

class Commodity(Model):
    item_no = fields.IntField()  # 项次
    material_no = fields.CharField(max_length=50, null=True)  # 料件编号
    product_name = fields.CharField(max_length=100)  # 品名(MPN)
    specification = fields.CharField(max_length=100, null=True)  # 规格
    pricing_unit = fields.CharField(max_length=20)  # 计价单位
    pricing_quantity = fields.FloatField()  # 计价数量
    price_before_tax = fields.DecimalField(max_digits=10, decimal_places=6)  # 税前单价
    amount_before_tax = fields.DecimalField(max_digits=15, decimal_places=6)  # 税前金额
    delivery_date = fields.CharField(max_length=20)  # 交货日
    requisition_no = fields.CharField(max_length=50)  # 请购单号
    purchase_quantity = fields.FloatField()  # 采购数量
    price_with_tax = fields.DecimalField(max_digits=10, decimal_places=6)  # 含税单价
    amount_with_tax = fields.DecimalField(max_digits=15, decimal_places=6)  # 含税金额
    purchase_unit = fields.CharField(max_length=20)  # 采购单位
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    class Meta:
        table = "commodity"
    @property
    def created_at_local(self) -> datetime:
        return to_china_time(self.created_at)
    @property
    def updated_at_local(self) -> datetime:
        return to_china_time(self.updated_at)
        
    def __str__(self):
        return (f"商品信息:\n"
                f"    项次: {self.item_no}\n"
                f"    料件编号: {self.material_no}\n"
                f"    品名(MPN): {self.product_name}\n"
                f"    规格: {self.specification}\n"
                f"    计价单位: {self.pricing_unit}\n"
                f"    计价数量: {self.pricing_quantity}\n"
                f"    税前单价: {self.price_before_tax}\n"
                f"    税前金额: {self.amount_before_tax}\n"
                f"    交货日: {self.delivery_date}\n"
                f"    请购单号: {self.requisition_no}\n"
                f"    采购数量: {self.purchase_quantity}\n"
                f"    含税单价: {self.price_with_tax}\n"
                f"    含税金额: {self.amount_with_tax}\n"
        )


async def main():
    # 初始化连接
    await Tortoise.init(
        db_url = "mysql://root:12345678@localhost:10001/statement?charset=utf8mb4",
        modules={'models': ['__main__']}
    )

    await Tortoise.generate_schemas()
    commodity_list = extract_commodities("../output/table_data_formatted.xlsx")
    print(type(commodity_list))
    for commodity in commodity_list:
        print (commodity)
        commodity = await Commodity.create(
        ** commodity.__dict__
    )

asyncio.run(main())