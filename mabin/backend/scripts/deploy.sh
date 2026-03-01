#!/bin/bash
# 部署脚本

echo "开始部署学院OA系统..."

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 数据库迁移
echo "执行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 初始化数据
echo "初始化数据..."
python scripts/init_data.py

# 重启服务（如果使用systemd）
# sudo systemctl restart college-oa

echo "部署完成！"
