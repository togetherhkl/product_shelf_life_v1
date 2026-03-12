from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.db_depend import get_db
from dependencies.admin_auth_depend import get_current_admin
import crud.product_crud as product_crud
import crud.category_crud as category_crud
from schemas.orm_schema import ProductCreate, ProductRead, ProductUpdate, ProductListResponse, ProductReadWithRelations, OpenFoodFactsResponse

router = APIRouter(prefix="/product", tags=["product"])

@router.post("/", response_model=ProductRead)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """创建新产品（需要管理员权限）"""
    # 检查条形码或二维码是否已存在
    existing = product_crud.get_product_by_barcode(db, product_in.barcode_or_qr)
    if existing:
        raise HTTPException(status_code=400, detail="条形码或二维码已存在")
    
    # 检查分类是否存在
    category = category_crud.get_category_by_id(db, product_in.category_id)
    if not category:
        raise HTTPException(status_code=400, detail="分类不存在")
    
    # 设置创建者为当前管理员
    product_in.created_by_admin_id = current_admin.admin_id
    
    try:
        product = product_crud.create_product(db, product_in)
        return ProductRead.model_validate(product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """根据 product_id 查询产品（公开接口）"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品未找到")
    return ProductRead.model_validate(product)

@router.get("/barcode/{barcode_or_qr}", response_model=ProductRead)
def get_product_by_barcode(barcode_or_qr: str, db: Session = Depends(get_db)):
    """根据条形码或二维码查询产品（公开接口）"""
    product = product_crud.get_product_by_barcode(db, barcode_or_qr)
    if not product:
        raise HTTPException(status_code=404, detail="产品未找到")
    return ProductRead.model_validate(product)

@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    name: Optional[str] = Query(None, description="按产品名称模糊搜索"),
    category_id: Optional[str] = Query(None, description="按分类ID精确匹配"),
    created_by_admin_id: Optional[str] = Query(None, description="按创建管理员ID精确匹配"),
    barcode_or_qr: Optional[str] = Query(None, description="按条形码或二维码模糊搜索"),
    db: Session = Depends(get_db)
):
    """分页列出产品（公开接口），支持多条件搜索"""
    # 获取产品列表
    products = product_crud.list_products(
        db, skip=skip, limit=limit,
        name=name, category_id=category_id, 
        created_by_admin_id=created_by_admin_id, barcode_or_qr=barcode_or_qr
    )
    
    # 获取总数
    total = product_crud.count_products(
        db, name=name, category_id=category_id,
        created_by_admin_id=created_by_admin_id, barcode_or_qr=barcode_or_qr
    )
    
    return ProductListResponse(
        products=[ProductReadWithRelations.model_validate(p) for p in products],
        total=total
    )

@router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: str, product_in: ProductUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """更新产品（需要管理员权限）"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品未找到")
    
    # 如果要更新条形码，检查新条形码是否已存在
    if product_in.barcode_or_qr:
        existing = product_crud.get_product_by_barcode(db, product_in.barcode_or_qr)
        if existing and existing.product_id != product_id:
            raise HTTPException(status_code=400, detail="条形码或二维码已存在")
    
    # 如果要更新分类，检查分类是否存在
    if product_in.category_id:
        category = category_crud.get_category_by_id(db, product_in.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="分类不存在")
    
    try:
        product = product_crud.update_product(db, product, product_in)
        return ProductRead.model_validate(product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}")
def delete_product(product_id: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """删除产品（需要管理员权限）"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品未找到")
    
    # 检查是否有扫码记录
    if product.scan_histories:
        raise HTTPException(status_code=400, detail="无法删除产品：该产品已有扫码记录")
    
    ok = product_crud.delete_product(db, product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="产品未找到")
    return {"deleted": True}

@router.get("/category/{category_id}", response_model=ProductListResponse)
def get_products_by_category(
    category_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """根据分类ID获取产品列表（公开接口）"""
    # 检查分类是否存在
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类未找到")
    
    products = product_crud.get_products_by_category(db, category_id, skip=skip, limit=limit)
    total = product_crud.count_products(db, category_id=category_id)
    
    return ProductListResponse(
        products=[ProductRead.model_validate(p) for p in products],
        total=total
    )

@router.get("/admin/{admin_id}", response_model=ProductListResponse)
def get_products_by_admin(
    admin_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """根据管理员ID获取该管理员创建的产品列表（需要管理员权限）"""
    products = product_crud.get_products_by_admin(db, admin_id, skip=skip, limit=limit)
    total = product_crud.count_products(db, created_by_admin_id=admin_id)
    
    return ProductListResponse(
        products=[ProductRead.model_validate(p) for p in products],
        total=total
    )

@router.get("/search/name/{name}", response_model=ProductListResponse)
def search_products_by_name(
    name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """根据产品名称模糊搜索产品（公开接口）"""
    products = product_crud.search_products_by_name(db, name, skip=skip, limit=limit)
    total = product_crud.count_products(db, name=name)
    
    return ProductListResponse(
        products=[ProductRead.model_validate(p) for p in products],
        total=total
    )

@router.get("/expired/list", response_model=ProductListResponse)
def get_expired_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """获取已过期的产品列表（公开接口）"""
    products = product_crud.get_expired_products(db, skip=skip, limit=limit)
    # 统计已过期产品总数（需要在 crud 中添加对应的统计方法）
    from datetime import date
    today = date.today()
    from models.orm_models import Product
    total = db.query(Product).filter(Product.expiration_date < today).count()
    
    return ProductListResponse(
        products=[ProductRead.model_validate(p) for p in products],
        total=total
    )

@router.get("/expiring-soon/list", response_model=ProductListResponse)
def get_expiring_soon_products(
    days: int = Query(7, ge=1, le=365, description="多少天内过期"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """获取即将过期的产品列表（公开接口）"""
    products = product_crud.get_expiring_soon_products(db, days=days, skip=skip, limit=limit)
    # 统计即将过期产品总数
    from datetime import date, timedelta
    from models.orm_models import Product
    today = date.today()
    expiry_date = today + timedelta(days=days)
    total = db.query(Product).filter(Product.expiration_date.between(today, expiry_date)).count()
    
    return ProductListResponse(
        products=[ProductRead.model_validate(p) for p in products],
        total=total
    )


@router.get("/openfoodfacts/{barcode_or_qr}", response_model=OpenFoodFactsResponse)
def get_info_by_openfoodfacts(
    barcode_or_qr: str
):
    """通过 OpenFoodFacts API 获取产品信息"""
    import requests
    import time
    
    try:
        # 使用 requests 库获取产品信息
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode_or_qr}"
        params = {
            "fields": "code,product_name_zh,product_name,image_front_url,brands"
        }
        
        headers = {
            "User-Agent": "HaMu-Food-App/1.0"
        }
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=10,  # 10秒超时
                    verify=False  # 暂时跳过 SSL 验证
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status") == 1:  # 产品找到
                        product_info = data.get("product", {})
                        
                        # 重新命名关键字使其与 Product 模型一致
                        return {
                            "barcode_or_qr": product_info.get('code', barcode_or_qr),
                            "name": product_info.get('product_name_zh') or product_info.get('product_name', '未知产品'),
                            "image_url": product_info.get('image_front_url', None),
                            "description": f"品牌: {product_info.get('brands', '未知品牌')}",
                            "category_id": None,  # 需要手动选择分类
                            "created_by_admin_id": None,  # 需要管理员创建时设置
                            "production_date": None,  # OpenFoodFacts 通常没有生产日期
                            "expiration_date": None,  # OpenFoodFacts 通常没有到期日期
                            "batch_number": None,  # OpenFoodFacts 通常没有批次号
                            "status": "success",
                            "message": "成功获取产品信息"
                        }
                    else:
                        return {
                            "barcode_or_qr": barcode_or_qr,
                            "name": "未找到产品信息",
                            "image_url": None,
                            "description": None,
                            "category_id": None,
                            "created_by_admin_id": None,
                            "production_date": None,
                            "expiration_date": None,
                            "batch_number": None,
                            "status": "not_found",
                            "message": "在 OpenFoodFacts 数据库中未找到该产品"
                        }
                else:
                    if attempt == max_retries - 1:  # 最后一次尝试
                        raise HTTPException(
                            status_code=503, 
                            detail=f"OpenFoodFacts API 返回错误: {response.status_code}"
                        )
                    
            except requests.exceptions.SSLError as e:
                if attempt == max_retries - 1:  # 最后一次尝试
                    return {
                        "barcode_or_qr": barcode_or_qr,
                        "name": "SSL连接错误，无法获取产品信息",
                        "image_url": None,
                        "description": None,
                        "category_id": None,
                        "created_by_admin_id": None,
                        "production_date": None,
                        "expiration_date": None,
                        "batch_number": None,
                        "status": "ssl_error",
                        "message": f"SSL连接错误: {str(e)}"
                    }
                time.sleep(1)  # 等待1秒后重试
                
            except requests.exceptions.Timeout as e:
                if attempt == max_retries - 1:  # 最后一次尝试
                    return {
                        "barcode_or_qr": barcode_or_qr,
                        "name": "请求超时，无法获取产品信息",
                        "image_url": None,
                        "description": None,
                        "category_id": None,
                        "created_by_admin_id": None,
                        "production_date": None,
                        "expiration_date": None,
                        "batch_number": None,
                        "status": "timeout",
                        "message": f"请求超时: {str(e)}"
                    }
                time.sleep(1)  # 等待1秒后重试
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:  # 最后一次尝试
                    return {
                        "barcode_or_qr": barcode_or_qr,
                        "name": "网络错误，无法获取产品信息",
                        "image_url": None,
                        "description": None,
                        "category_id": None,
                        "created_by_admin_id": None,
                        "production_date": None,
                        "expiration_date": None,
                        "batch_number": None,
                        "status": "network_error",
                        "message": f"网络错误: {str(e)}"
                    }
                time.sleep(1)  # 等待1秒后重试
                
    except Exception as e:
        return {
            "barcode_or_qr": barcode_or_qr,
            "name": "未知错误，无法获取产品信息",
            "image_url": None,
            "description": None,
            "category_id": None,
            "created_by_admin_id": None,
            "production_date": None,
            "expiration_date": None,
            "batch_number": None,
            "status": "unknown_error",
            "message": f"未知错误: {str(e)}"
        }