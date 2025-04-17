from tortoise import Tortoise, fields
from tortoise.models import Model
import asyncio
import sys
import os
# import pytz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))
from order.order_info import extract_supplier_info
from datetime import datetime
from tools.time_tools import to_china_time



class Supplier(Model):
    supplier_name = fields.CharField(max_length=100)
    supplier_address = fields.CharField(max_length=255, null=True)
    supplier_phone = fields.CharField(max_length=20, null=True)
    supplier_contact_person = fields.CharField(max_length=50, null=True)
    supplier_code = fields.CharField(max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    @property
    def created_at_local(self) -> datetime:
        print(123456)
        return to_china_time(self.created_at)

    @property
    def updated_at_local(self) -> datetime:
        return to_china_time(self.updated_at)
    
    class Meta:
        table = "supplier"




async def main():
    # 初始化连接
    await Tortoise.init(
        db_url = "mysql://root:12345678@localhost:10001/statement?charset=utf8mb4",
        modules={'models': ['__main__']}
    )
    # 创建表
    await Tortoise.generate_schemas()
    supplier_info = extract_supplier_info("../output/table_data_formatted.xlsx")
    # 创建客户
    supplier = await Supplier.create(
        **supplier_info.__dict__
    )
    print(supplier)

    # print("sys.path =", sys.path)
    # # # 查询客户
    # suppliers = await Supplier.filter(company_name__contains='公司')
    # for supplier in suppliers:
    #     print(f"{supplier.company_name}: {supplier.phone}")
    
    # # 更新客户
    # await Supplier.filter(id=1).update(phone="0755-99999999")
    
    # # 删除客户
    # await Supplier.filter(id=1).delete()
    
    # # 关闭连接
    # await Tortoise.close_connections()

# 运行异步函数
asyncio.run(main())
