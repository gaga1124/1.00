# 快速启动指南

## 项目结构

```
学院1.0/
├── backend/              # Django后端
│   ├── apps/            # 应用模块
│   │   ├── users/       # 用户管理
│   │   ├── rbac/        # 权限管理
│   │   ├── students/    # 学生管理
│   │   ├── workflow/    # 流程引擎
│   │   ├── resources/   # 资源预约
│   │   ├── approval/    # 审批管理
│   │   └── utils/       # 工具类
│   ├── college_oa/      # 项目配置
│   └── scripts/         # 脚本
├── frontend/            # Vue3前端
│   └── src/
│       ├── views/       # 页面组件
│       ├── stores/      # 状态管理
│       ├── router/      # 路由配置
│       └── utils/       # 工具函数
├── docker/              # Docker配置
└── docs/                # 文档

```

## 后端启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

创建MySQL数据库：
```sql
CREATE DATABASE college_oa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

配置环境变量（创建 `.env` 文件）：
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=college_oa
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
REDIS_URL=redis://127.0.0.1:6379/1
```

### 3. 数据库迁移

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. 初始化数据

```bash
python scripts/init_data.py
```

### 5. 启动服务

```bash
python manage.py runserver
```

后端服务将在 http://localhost:8000 启动

## 前端启动

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 功能模块说明

### 1. 用户与权限系统 (RBAC)
- ✅ 用户管理（扩展User模型）
- ✅ 角色管理（6种预设角色）
- ✅ 权限管理（菜单级、按钮级）
- ✅ 部门管理（树形结构）
- ✅ JWT认证

### 2. 学生全信息管理系统
- ✅ 学生基础档案
- ✅ 政治面貌流转追踪
- ✅ 动态扩展字段（JSON存储）
- ✅ 档案记录管理（获奖、惩处、科研等）

### 3. 动态流程引擎
- ✅ 工作流定义
- ✅ 节点配置（审批人、会签、条件分支）
- ✅ 流程实例管理
- ✅ 待办任务中心

### 4. 资源预约
- ✅ 资源管理（会议室、报告厅等）
- ✅ 预约功能
- ✅ 冲突检测
- ✅ 审批流程

### 5. 综合审批
- ✅ 请假审批（学生/教职工）
- ✅ 财务报销（多类别、发票管理）
- ✅ 入党/入团审批

## API文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 下一步开发

1. **前端页面开发**
   - 登录页面
   - 主布局（侧边栏、顶部导航）
   - 学生管理页面
   - 流程配置页面
   - 资源预约日历视图
   - 审批列表页面

2. **功能完善**
   - 文件上传组件
   - 权限中间件
   - 操作日志记录
   - 消息通知系统

3. **性能优化**
   - Redis缓存
   - 数据库索引优化
   - 前端路由懒加载
   - 图片压缩

4. **部署上线**
   - 宝塔面板配置
   - Nginx反向代理
   - SSL证书配置
   - 备份策略

## 常见问题

### Q: 数据库连接失败？
A: 检查 `.env` 文件中的数据库配置，确保MySQL服务已启动。

### Q: Redis连接失败？
A: 确保Redis服务已启动，或修改 `REDIS_URL` 配置。

### Q: 前端无法访问后端API？
A: 检查 `vite.config.js` 中的代理配置，确保后端服务正在运行。

### Q: 文件上传失败？
A: 检查 `MEDIA_ROOT` 目录权限，确保有写入权限。

## 技术支持

如有问题，请查看：
- API文档：`docs/API.md`
- 部署文档：`docs/DEPLOYMENT.md`
- 项目README：`README.md`
