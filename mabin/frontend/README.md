# 学院OA系统 - 前端

## 技术栈

- Vue 3 (Composition API)
- Element Plus
- Vue Router
- Pinia (状态管理)
- Axios
- Vite
- Day.js

## 项目结构

```
src/
├── views/           # 页面组件
│   ├── Login.vue   # 登录页
│   ├── Dashboard.vue  # 工作台
│   ├── students/   # 学生管理
│   ├── workflow/   # 流程管理
│   ├── resources/  # 资源预约
│   └── approval/   # 审批管理
├── layouts/        # 布局组件
│   └── MainLayout.vue
├── components/     # 通用组件
├── stores/         # 状态管理
│   └── user.js
├── router/         # 路由配置
│   └── index.js
├── utils/          # 工具函数
│   └── api.js
└── App.vue         # 根组件
```

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

## 功能模块

### 1. 用户认证
- JWT Token认证
- Token自动刷新
- 登录/登出

### 2. 学生管理
- 学生列表（搜索、筛选）
- 学生详情（基本信息、政治面貌历史、档案记录）
- 学生档案管理

### 3. 流程管理
- 流程配置
- 节点管理
- 流程实例
- 待办任务

### 4. 资源预约
- 资源列表
- 资源预约
- 预约日历（待开发）

### 5. 审批管理
- 请假申请
- 财务报销
- 审批处理

## API调用

所有API调用通过 `@/utils/api` 封装，自动处理：
- Token添加
- 请求拦截
- 响应拦截
- Token刷新
- 错误处理

## 路由守卫

- 未登录用户自动跳转到登录页
- 已登录用户访问登录页自动跳转到首页

## 状态管理

使用Pinia进行状态管理：
- `user` store: 用户信息、登录状态

## 注意事项

1. 所有API请求需要后端服务运行在 `http://localhost:8000`
2. 开发环境使用Vite代理转发API请求
3. 生产环境需要配置Nginx反向代理
