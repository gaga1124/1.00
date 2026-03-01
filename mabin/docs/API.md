# API文档

## 认证

### 登录
```
POST /api/users/login/
Body: {
  "username": "string",
  "password": "string"
}
Response: {
  "access": "token",
  "refresh": "token",
  "user": {...}
}
```

### 刷新Token
```
POST /api/auth/refresh/
Body: {
  "refresh": "refresh_token"
}
Response: {
  "access": "new_token"
}
```

## 用户管理

### 获取当前用户信息
```
GET /api/users/me/
Headers: Authorization: Bearer {token}
```

### 获取用户列表
```
GET /api/users/
```

## 学生管理

### 获取学生列表
```
GET /api/students/?major=计算机&class_name=2021级1班
```

### 获取学生详情
```
GET /api/students/{id}/
```

### 获取学生档案记录
```
GET /api/students/{id}/records/
```

### 更新政治面貌
```
POST /api/students/{id}/update_political_status/
Body: {
  "to_status": "member",
  "application_date": "2024-01-01",
  "application_file": file
}
```

## 教务管理

### 获取可选课程
```
GET /api/academic/courses/available/?semester=2024-2025-1
```

### 选课
```
POST /api/academic/selections/
Body: {
  "course": 1,
  "student": 1
}
```

### 成绩查询
```
GET /api/academic/grades/
```

### 课堂签到
```
GET /api/academic/attendances/?course=1&date=2024-01-01
POST /api/academic/attendances/batch_record/
Body: {
  "course_id": 1,
  "date": "2024-01-01",
  "records": [
    {"student_id": 1, "status": "present"}
  ]
}
```

## 评奖评优

### 获取奖项类型
```
GET /api/awards/types/
```

### 申请奖项
```
POST /api/awards/applications/
Body: {
  "award_type": 1,
  "reason": "..."
}
```

## 科研管理

### 获取项目列表
```
GET /api/research/projects/
```

### 更新经费使用
```
POST /api/research/projects/{id}/update_budget/
Body: {
  "category": "差旅费",
  "amount": 1000
}
```

## 就业服务

### 招聘信息列表
```
GET /api/career/jobs/
```

### 投递简历
```
POST /api/career/applications/
Body: {
  "job": 1,
  "resume": 1
}
```

## 党建团建

### 成员发展记录
```
GET /api/party/members/
```

### 活动签到
```
POST /api/party/activities/{id}/sign_in/
```

## 社会实践与竞赛

### 实践申报
```
POST /api/activities/practices/
```

### 竞赛报名
```
POST /api/activities/competitions/{id}/register/
```

### 竞赛评审
```
POST /api/activities/competition-teams/{id}/submit_work/
```

## 自定义活动系统

### 获取活动类型
```
GET /api/activities/types/
```

### 活动实例管理
```
GET /api/activities/instances/?activity_type=1
POST /api/activities/instances/
Body: {
  "activity_type": 1,
  "data": {"location": "A101", "budget": 500}
}
```

## 数据分析与预警

### 核心指标统计
```
GET /api/analysis/stats/
```

### 系统预警列表
```
GET /api/analysis/warnings/
```

### 决策建议分析
```
GET /api/analysis/decision/
```

## 流程管理

### 获取工作流列表
```
GET /api/workflow/
```

### 创建工作流实例
```
POST /api/workflow/{id}/create_instance/
Body: {
  "title": "奖学金申请",
  "description": "...",
  "attachments": []
}
```

### 获取待办任务
```
GET /api/workflow/instances/my_todos/
```

### 审批流程
```
POST /api/workflow/instances/{id}/approve/
Body: {
  "action": "approve|reject|reject_to_previous",
  "comment": "审批意见"
}
```

## 资源预约

### 获取资源列表
```
GET /api/resources/
```

### 检查资源可用性
```
GET /api/resources/{id}/availability/?start_time=2024-01-01T10:00&end_time=2024-01-01T12:00
```

### 创建预约
```
POST /api/resources/bookings/
Body: {
  "resource": 1,
  "title": "会议预约",
  "start_time": "2024-01-01T10:00",
  "end_time": "2024-01-01T12:00",
  "description": "..."
}
```

## 权限管理

### 获取角色列表
```
GET /api/rbac/roles/
```

### 获取部门树
```
GET /api/rbac/departments/tree/
```
