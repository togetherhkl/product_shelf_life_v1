"""
测试 JOIN 查询功能的脚本
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_list_products_with_relations():
    """测试带关联数据的产品列表接口"""
    print("=== 测试产品列表接口（JOIN 查询）===")
    
    # 测试获取产品列表
    response = requests.get(f"{BASE_URL}/product/")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回数据结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 检查是否包含嵌套的分类和管理员信息
        if data.get("products"):
            product = data["products"][0]
            has_category = "category" in product and product["category"] is not None
            has_admin = "created_by_admin" in product and product["created_by_admin"] is not None
            
            print(f"\n=== 关联数据检查 ===")
            print(f"产品总数: {data.get('total', 0)}")
            print(f"是否包含分类信息: {has_category}")
            print(f"是否包含创建管理员信息: {has_admin}")
            
            if has_category:
                print(f"分类信息示例: {product['category']}")
            if has_admin:
                print(f"管理员信息示例: {product['created_by_admin']}")
        else:
            print("没有产品数据")
    else:
        print(f"请求失败: {response.text}")

def test_admin_login():
    """测试管理员登录获取 token"""
    print("\n=== 测试管理员登录 ===")
    
    # 注意：需要先有管理员账户数据
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
    print(f"登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("登录成功!")
        print(f"Token: {data.get('access_token', 'N/A')}")
        return data.get("access_token")
    else:
        print(f"登录失败: {response.text}")
        return None

def test_create_category_and_product(token):
    """测试创建分类和产品（需要管理员权限）"""
    if not token:
        print("没有有效的 token，跳过创建测试")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试创建分类 ===")
    category_data = {
        "category_name": "测试分类"
    }
    
    response = requests.post(f"{BASE_URL}/category/", json=category_data, headers=headers)
    print(f"创建分类状态码: {response.status_code}")
    
    if response.status_code == 200:
        category = response.json()
        category_id = category["category_id"]
        print(f"分类创建成功: {category}")
        
        print("\n=== 测试创建产品 ===")
        product_data = {
            "barcode_or_qr": "123456789",
            "name": "测试产品",
            "category_id": category_id,
            "description": "这是一个测试产品"
        }
        
        response = requests.post(f"{BASE_URL}/product/", json=product_data, headers=headers)
        print(f"创建产品状态码: {response.status_code}")
        
        if response.status_code == 200:
            product = response.json()
            print(f"产品创建成功: {product}")
        else:
            print(f"创建产品失败: {response.text}")
    else:
        print(f"创建分类失败: {response.text}")

if __name__ == "__main__":
    # 测试产品列表接口
    test_list_products_with_relations()
    
    # 测试管理员登录
    token = test_admin_login()
    
    # 测试创建数据
    test_create_category_and_product(token)
    
    # 再次测试产品列表（应该能看到新创建的数据）
    print("\n=== 重新测试产品列表接口 ===")
    test_list_products_with_relations()