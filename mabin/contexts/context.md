# 学院1.0 项目上下文

## 1. 项目概览
这是一个全栈**教育/学院管理系统**，采用前后端分离架构。
- **前端**: Vue 3 + Element Plus，提供现代化的 Web 交互界面。
- **后端**: Django + Django REST Framework (DRF)，提供强大的 RESTful API 和业务逻辑支撑。

## 2. 技术架构

### 前端技术栈 (`frontend`)
- **核心框架**: Vue 3 (Composition API)
- **UI 组件库**: Element Plus
- **状态管理**: Pinia (如 `useUserStore`)
- **路由管理**: Vue Router
- **HTTP 客户端**: Axios
- **工具库**: 
  - `xlsx`: Excel 数据导出
  - `dayjs`: 日期时间处理
  - `sass`: CSS 预处理器

### 后端技术栈 (`backend`)
- **Web 框架**: Django
- **API 框架**: Django REST Framework (DRF)
- **身份认证**: SimpleJWT (JWT Authentication)
- **API 文档**: drf-yasg
- **工具库**:
  - `pandas/numpy` (推测): 数据分析支持
  - `celery` (推测): 异步任务处理

## 3. 核心功能模块
系统包含 14+ 个核心业务模块，前后端结构高度对应：

| 模块分类 | 功能描述 | 前端路由 | 后端 App |
| :--- | :--- | :--- | :--- |
| **综合办公** | **工作流**: 待办事项、流程审批<br>**审批**: 请假、报销<br>**报修**: 故障报修管理<br>**通知**: 系统消息通知 | `/workflow`<br>`/approval`<br>`/repair`<br>`/notifications` | `workflow`<br>`approval`<br>`repair`<br>`notifications` |
| **教务管理** | **课程**: 课程信息管理<br>**成绩**: 学生成绩录入与查询<br>**考勤**: 上课考勤记录 | `/academic/courses`<br>`/academic/grades`<br>`/academic/attendance` | `academic` |
| **学生管理** | **档案**: 学生基础信息与学籍<br>**日常**: 学生列表维护 | `/students` | `students` |
| **科研发展** | **项目**: 科研项目申报与管理<br>**成果**: 论文/专利等成果登记<br>**团队**: 科研团队建设 | `/research` | `research` |
| **评奖评优** | 奖学金评定、荣誉称号管理 | `/awards` | `awards` |
| **就业服务** | **招聘**: 职位信息、招聘会<br>**申请**: 学生投递记录<br>**统计**: 就业率与去向分析 | `/career` | `career` |
| **党团建设** | 党员/团员管理、组织生活会/活动 | `/party` | `party` |
| **活动实践** | 社会实践、学科竞赛、第二课堂 | `/activities` | `activities` |
| **系统基础** | **分析**: 数据仪表盘<br>**资源**: 教室/会议室资源与日历<br>**权限**: RBAC 用户与角色管理 | `/analysis`<br>`/resources`<br>`/rbac` | `analysis`<br>`resources`<br>`rbac` |

## 4. 目录结构说明

### 前端 (`frontend/src`)
- `views/`: 页面视图，按模块划分目录 (e.g., `academic/`, `research/`)
- `router/`: 路由配置 (`index.js` 定义了所有页面路径)
- `stores/`: Pinia 状态管理
- `utils/`: 通用工具函数 (重点关注 `export.js`)
- `layouts/`: 页面布局组件

### 后端 (`backend`)
- `apps/`: 业务应用模块，每个文件夹对应一个功能域
- `requirements.txt`: Python 依赖列表

## 5. 当前开发重点
1. **通用工具优化**: 完善 `frontend/src/utils/export.js`，增强 Excel/CSV 导出功能的通用性。
2. **通知系统体验**: 优化 `frontend/src/views/system/NotificationList.vue` 的交互体验。
3. **系统健壮性**: 确保各业务模块的数据一致性与权限控制。
