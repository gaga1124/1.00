# 部署文档

## 宝塔面板部署指南

### 1. 环境准备

在Debian 13系统上安装宝塔面板后，需要安装以下软件：

- Python 3.11+
- MySQL 8.0
- Redis 7.0
- Nginx

### 2. 数据库配置

1. 在宝塔面板中创建MySQL数据库 `college_oa`
2. 创建数据库用户并授权

### 3. 后端部署

1. 上传后端代码到服务器
2. 创建Python虚拟环境：
```bash
cd /www/wwwroot/college_oa/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. 配置环境变量（创建 `.env` 文件）：
```
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=college_oa
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
REDIS_URL=redis://127.0.0.1:6379/1
```

4. 执行数据库迁移：
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

5. 在宝塔面板中配置Python项目：
   - 项目路径：`/www/wwwroot/college_oa/backend`
   - 启动文件：`manage.py`
   - 启动方式：`gunicorn`
   - 端口：8000

### 4. 前端部署

1. 上传前端代码到服务器
2. 安装依赖并构建：
```bash
cd /www/wwwroot/college_oa/frontend
npm install
npm run build
```

3. 在宝塔面板中配置网站：
   - 网站目录：`/www/wwwroot/college_oa/frontend/dist`
   - 运行目录：`/www/wwwroot/college_oa/frontend/dist`

### 5. Nginx配置

在宝塔面板的网站设置中添加以下Nginx配置：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /media/ {
    alias /www/wwwroot/college_oa/backend/media/;
}

location /static/ {
    alias /www/wwwroot/college_oa/backend/staticfiles/;
}
```

### 6. 安全配置

1. 在宝塔面板中配置防火墙，开放80、443端口
2. 配置SSL证书（推荐使用Let's Encrypt免费证书）
3. 设置文件权限：
```bash
chmod 755 /www/wwwroot/college_oa
chown -R www:www /www/wwwroot/college_oa
```

### 7. 定时任务

在宝塔面板中添加定时任务，定期清理日志和缓存。

## Docker部署

使用Docker Compose一键部署：

```bash
cd docker
docker-compose up -d
```

## 性能优化

1. 启用Redis缓存
2. 配置Nginx缓存静态资源
3. 使用Gunicorn + Nginx部署后端
4. 配置数据库连接池
5. 启用CDN加速静态资源
