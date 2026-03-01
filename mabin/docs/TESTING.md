# 测试文档

## 测试环境配置

### 运行测试

```bash
# 使用Django测试框架
python manage.py test

# 使用pytest（推荐）
pip install pytest pytest-django
pytest

# 运行特定测试
pytest apps/users/tests.py
pytest apps/students/tests.py::StudentAPITestCase::test_get_student_list
```

## 测试覆盖范围

### 单元测试
- [x] 用户认证测试
- [x] 学生管理API测试
- [ ] 流程引擎测试
- [ ] 资源预约测试
- [ ] 审批流程测试

### 集成测试
- [ ] 完整审批流程测试
- [ ] 资源预约冲突检测测试
- [ ] 权限控制测试

### 性能测试
- [ ] API响应时间测试
- [ ] 并发请求测试
- [ ] 数据库查询优化测试

## 测试最佳实践

1. **测试隔离**：每个测试用例应该独立，不依赖其他测试
2. **测试数据**：使用fixtures或factory创建测试数据
3. **断言清晰**：使用明确的断言消息
4. **测试命名**：使用描述性的测试方法名

## 持续集成

建议配置CI/CD流程：
- GitHub Actions
- GitLab CI
- Jenkins

每次代码提交自动运行测试套件。
