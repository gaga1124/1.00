# 性能优化指南

## 数据库优化

### 1. 索引优化

已添加的索引：
- `ResourceBooking`: `resource`, `start_time`, `end_time`
- `Student`: `student_id` (unique)
- `User`: `username` (unique)

建议添加的索引：
```python
# 在models.py中添加
class Meta:
    indexes = [
        models.Index(fields=['status', 'created_at']),
        models.Index(fields=['applicant', 'status']),
    ]
```

### 2. 查询优化

- 使用 `select_related()` 减少数据库查询
- 使用 `prefetch_related()` 优化多对多关系
- 避免 N+1 查询问题

示例：
```python
# 优化前
students = Student.objects.all()
for student in students:
    print(student.user.real_name)  # N+1查询

# 优化后
students = Student.objects.select_related('user').all()
for student in students:
    print(student.user.real_name)  # 单次查询
```

## 缓存策略

### Redis缓存使用

1. **用户权限缓存**
```python
from apps.utils.cache_helper import get_cached_user_permissions

permissions = get_cached_user_permissions(user_id)
if not permissions:
    permissions = calculate_permissions(user)
    set_cached_user_permissions(user_id, permissions)
```

2. **热点数据缓存**
- 学生列表（5分钟）
- 资源列表（10分钟）
- 流程配置（30分钟）

3. **缓存失效策略**
- 数据更新时主动清除相关缓存
- 设置合理的过期时间

## API性能优化

### 1. 分页
所有列表接口都使用分页，默认每页20条。

### 2. 字段过滤
使用 `fields` 参数只返回需要的字段。

### 3. 响应压缩
Nginx配置gzip压缩：
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## 前端性能优化

### 1. 代码分割
```javascript
// 路由懒加载
const Dashboard = () => import('@/views/Dashboard.vue')
```

### 2. 图片优化
- 使用WebP格式
- 图片懒加载
- CDN加速

### 3. 资源压缩
```bash
npm run build  # 自动压缩和优化
```

## 监控指标

### 关键指标
- API响应时间 < 500ms
- 页面加载时间 < 2s
- 数据库查询时间 < 100ms
- 缓存命中率 > 80%

### 监控工具
- Django Debug Toolbar（开发环境）
- Sentry（错误监控）
- Prometheus + Grafana（生产环境）

## 性能测试

### 压力测试
```bash
# 使用Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/students/

# 使用locust
locust -f locustfile.py
```

### 数据库性能
```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

## 优化检查清单

- [ ] 数据库索引已优化
- [ ] 查询已使用select_related/prefetch_related
- [ ] Redis缓存已配置
- [ ] API分页已实现
- [ ] 前端代码已压缩
- [ ] 静态资源已使用CDN
- [ ] Gzip压缩已启用
- [ ] 图片已优化
- [ ] 慢查询已监控
