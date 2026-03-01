"""
初始化报修分类数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_oa.settings')
django.setup()

from apps.repair.models import RepairCategory

def create_repair_categories():
    """创建报修分类"""
    categories = [
        {'name': '水电维修', 'icon': 'Lightning', 'order': 1},
        {'name': '网络故障', 'icon': 'Connection', 'order': 2},
        {'name': '设备故障', 'icon': 'Monitor', 'order': 3},
        {'name': '门窗维修', 'icon': 'Door', 'order': 4},
        {'name': '空调维修', 'icon': 'Sunny', 'order': 5},
        {'name': '其他', 'icon': 'More', 'order': 6},
    ]
    
    for cat_data in categories:
        category, created = RepairCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"创建报修分类: {category.name}")
        else:
            print(f"报修分类已存在: {category.name}")

if __name__ == '__main__':
    print("开始初始化报修分类数据...")
    create_repair_categories()
    print("数据初始化完成！")
