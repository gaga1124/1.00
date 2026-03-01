# 报修模块使用说明

## 功能概述

报修服务模块提供完整的报修申请、处理、跟踪和评价功能。

## 主要功能

### 1. 报修申请
- 选择报修分类（水电、网络、设备等）
- 填写报修信息（标题、地点、描述）
- 设置优先级（低、中、高、紧急）
- 上传现场图片
- 填写联系方式

### 2. 报修管理
- 查看报修列表（支持筛选和搜索）
- 查看报修详情
- 跟踪处理进度
- 查看处理记录

### 3. 报修处理（管理员/处理人）
- 受理报修
- 开始处理
- 完成报修
- 添加处理记录和图片

### 4. 评价功能
- 对已完成的报修进行评价
- 评分（1-5分）
- 填写评价意见

## 报修流程

1. **申请阶段**
   - 用户提交报修申请
   - 状态：待受理

2. **受理阶段**
   - 管理员/处理人受理报修
   - 状态：已受理

3. **处理阶段**
   - 处理人开始处理
   - 状态：处理中
   - 可添加处理记录

4. **完成阶段**
   - 处理人完成报修
   - 状态：已完成
   - 申请人可进行评价

## API接口

### 报修分类
- `GET /api/repair/categories/` - 获取分类列表

### 报修申请
- `GET /api/repair/applications/` - 获取报修列表
- `POST /api/repair/applications/` - 创建报修申请
- `GET /api/repair/applications/{id}/` - 获取报修详情
- `GET /api/repair/applications/statistics/` - 获取统计数据

### 报修操作
- `POST /api/repair/applications/{id}/accept/` - 受理报修
- `POST /api/repair/applications/{id}/start_processing/` - 开始处理
- `POST /api/repair/applications/{id}/complete/` - 完成报修
- `POST /api/repair/applications/{id}/cancel/` - 取消报修
- `POST /api/repair/applications/{id}/rate/` - 评价报修

## 数据模型

### RepairCategory（报修分类）
- name: 分类名称
- icon: 图标
- description: 描述
- order: 排序

### RepairApplication（报修申请）
- applicant: 申请人
- category: 分类
- title: 标题
- description: 描述
- location: 地点
- priority: 优先级
- status: 状态
- images: 图片列表
- handler: 处理人
- rating: 评分

### RepairRecord（处理记录）
- application: 报修申请
- operator: 操作人
- action: 操作
- comment: 备注
- images: 图片

## 权限说明

- **普通用户**：可以创建报修、查看自己的报修、评价已完成的报修
- **管理员/处理人**：可以查看所有报修、受理、处理、完成报修

## 使用示例

### 创建报修
```javascript
const data = {
  category: 1,
  title: '教室灯管不亮',
  location: '教学楼A101',
  description: '教室前排灯管不亮，影响上课',
  priority: 'high',
  contact_name: '张三',
  contact_phone: '13800138000',
  images: [...]
}

await api.post('/repair/applications/', data)
```

### 受理报修
```javascript
await api.post(`/repair/applications/${id}/accept/`, {
  comment: '已受理，将安排维修人员处理'
})
```

### 评价报修
```javascript
await api.post(`/repair/applications/${id}/rate/`, {
  rating: 5,
  comment: '处理及时，服务态度好'
})
```
