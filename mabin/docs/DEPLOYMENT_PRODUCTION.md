# 生产环境部署指南

## 服务器要求

- 操作系统：Debian 13 (Trixie)
- Python：3.11+
- MySQL：8.0+
- Redis：7.0+
- Nginx：最新版
- 内存：至少2GB
- 硬盘：至少20GB

## 部署步骤

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install -y python3-pip python3-venv nginx mysql-server redis-server
```

### 2. 数据库配置

```bash
# 登录MySQL
sudo mysql -u root -p

# 创建数据库和用户
CREATE DATABASE college_oa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'college_oa'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON college_oa.* TO 'college_oa'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 项目部署

```bash
# 创建项目目录
sudo mkdir -p /var/www/college_oa
sudo chown $USER:$USER /var/www/college_oa

# 上传项目代码
cd /var/www/college_oa

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements-prod.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

### 4. Django配置

```bash
# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 初始化数据
python scripts/init_data.py

# 收集静态文件
python manage.py collectstatic --noinput
```

### 5. Gunicorn配置

```bash
# 测试Gunicorn
gunicorn -c gunicorn_config.py college_oa.wsgi:application

# 创建systemd服务
sudo nano /etc/systemd/system/college-oa.service
```

服务文件内容：
```ini
[Unit]
Description=College OA Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/college_oa/backend
ExecStart=/var/www/college_oa/backend/venv/bin/gunicorn \
    --config /var/www/college_oa/backend/gunicorn_config.py \
    college_oa.wsgi:application

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable college-oa
sudo systemctl start college-oa
sudo systemctl status college-oa
```

### 6. Nginx配置

```bash
sudo nano /etc/nginx/sites-available/college_oa
```

配置文件：
```nginx
upstream college_oa {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your_domain.com;

    client_max_body_size 100M;

    # 静态文件
    location /static/ {
        alias /var/www/college_oa/backend/staticfiles/;
        expires 30d;
    }

    # 媒体文件
    location /media/ {
        alias /var/www/college_oa/backend/media/;
        expires 7d;
    }

    # API代理
    location /api/ {
        proxy_pass http://college_oa;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端
    location / {
        root /var/www/college_oa/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/college_oa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL证书（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

### 8. 防火墙配置

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 安全加固

### 1. Django安全设置

在 `settings.py` 中：
```python
DEBUG = False
ALLOWED_HOSTS = ['your_domain.com', 'www.your_domain.com']

# 安全设置
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 2. 数据库安全

- 使用强密码
- 限制数据库用户权限
- 定期备份

### 3. 文件权限

```bash
sudo chown -R www-data:www-data /var/www/college_oa
sudo chmod -R 755 /var/www/college_oa
sudo chmod -R 775 /var/www/college_oa/backend/media
```

## 监控和维护

### 1. 日志查看

```bash
# Gunicorn日志
sudo tail -f /var/www/college_oa/backend/logs/gunicorn_error.log

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django日志
sudo tail -f /var/www/college_oa/backend/logs/django.log
```

### 2. 定期备份

设置定时任务：
```bash
crontab -e

# 每天凌晨2点备份
0 2 * * * /var/www/college_oa/backend/scripts/backup.sh
```

### 3. 性能监控

- 使用 `htop` 监控系统资源
- 使用 `mysqladmin` 监控数据库
- 配置Sentry错误监控

## 更新部署

```bash
cd /var/www/college_oa
source venv/bin/activate
git pull  # 或从代码仓库拉取
pip install -r requirements-prod.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart college-oa
```

## 故障排查

### 服务无法启动
```bash
sudo systemctl status college-oa
sudo journalctl -u college-oa -n 50
```

### 数据库连接失败
- 检查 `.env` 配置
- 检查MySQL服务状态
- 检查防火墙设置

### 静态文件404
- 检查 `collectstatic` 是否执行
- 检查Nginx配置路径
- 检查文件权限

## 性能优化

参考 [PERFORMANCE.md](PERFORMANCE.md) 进行性能优化。
