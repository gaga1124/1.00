from django.contrib.auth import get_user_model
import requests
import json

User = get_user_model()

# 检查用户
print("=== 用户检查 ===")
print(f"用户总数: {User.objects.count()}")

# 检查超级用户
print("\n=== 超级用户 ===")
superusers = User.objects.filter(is_superuser=True)
print(f"超级用户数量: {superusers.count()}")
for user in superusers[:5]:  # 只显示前5个
    print(f"用户名: {user.username}, 姓名: {user.real_name if hasattr(user, 'real_name') else 'N/A'}")

# 检查普通用户
print("\n=== 普通用户 ===")
regular_users = User.objects.filter(is_superuser=False)[:5]
print(f"普通用户示例 (前5个):")
for user in regular_users:
    print(f"用户名: {user.username}, 姓名: {user.real_name if hasattr(user, 'real_name') else 'N/A'}")

# 测试登录
print("\n=== 测试登录 ===")
login_url = "http://localhost:8000/api/users/login/"

test_users = [
    ("admin", "admin123"),
    ("admin", "123456"),
    ("test", "test123"),
]

for username, password in test_users:
    payload = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(login_url, data=json.dumps(payload), headers=headers, timeout=5)
        print(f"登录测试: {username}/{password} -> 状态码: {response.status_code}, 响应: {response.text}")
    except Exception as e:
        print(f"登录测试: {username}/{password} -> 错误: {str(e)}")

# 测试部门API
print("\n=== 测试部门API ===")
departments_url = "http://localhost:8000/api/rbac/departments/"
try:
    response = requests.get(departments_url, timeout=5)
    print(f"部门API测试 -> 状态码: {response.status_code}, 响应: {response.text}")
except Exception as e:
    print(f"部门API测试 -> 错误: {str(e)}")