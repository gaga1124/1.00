import requests
import json

# 测试登录
def test_login():
    print("=== 测试登录 ===")
    login_url = "http://localhost:8000/api/users/login/"
    
    # 尝试不同的默认账号
    test_accounts = [
        ("admin", "123456"),
        ("admin", "admin123"),
        ("test", "123456"),
        ("test", "test123"),
        ("user", "123456"),
    ]
    
    for username, password in test_accounts:
        payload = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(login_url, data=json.dumps(payload), headers=headers, timeout=5)
            print(f"登录测试: {username}/{password}")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            print("---")
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"登录测试: {username}/{password} -> 错误: {str(e)}")
            print("---")
    
    return None

# 测试部门API
def test_departments(token):
    print("\n=== 测试部门API ===")
    departments_url = "http://localhost:8000/api/rbac/departments/"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(departments_url, headers=headers, timeout=5)
        print(f"部门API测试")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.json()
    except Exception as e:
        print(f"部门API测试 -> 错误: {str(e)}")
        return None

# 主函数
if __name__ == "__main__":
    # 测试登录
    login_result = test_login()
    
    if login_result:
        access_token = login_result.get("access")
        if access_token:
            # 测试部门API
            test_departments(access_token)
        else:
            print("登录成功但没有获取到token")
    else:
        print("所有登录测试都失败了")
        print("请检查是否有正确的测试账号")
        print("或者尝试创建一个新的超级用户")