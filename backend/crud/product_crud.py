from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm_models import Product
from schemas.orm_schema import ProductCreate, ProductUpdate


def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
    """根据 product_id 查询产品"""
    return db.query(Product).filter(Product.product_id == product_id).first()


def get_product_by_barcode(db: Session, barcode_or_qr: str) -> Optional[Product]:
    """根据条形码或二维码查询产品"""
    return db.query(Product).filter(Product.barcode_or_qr == barcode_or_qr).first()


def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    category_id: Optional[str] = None,
    created_by_admin_id: Optional[str] = None,
    barcode_or_qr: Optional[str] = None
) -> List[Product]:
    """分页列出产品，支持多条件搜索"""
    from models.orm_models import Category, Admin
    from sqlalchemy.orm import joinedload
    
    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.created_by_admin)
    )
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if created_by_admin_id:
        query = query.filter(Product.created_by_admin_id == created_by_admin_id)
    if barcode_or_qr:
        query = query.filter(Product.barcode_or_qr.ilike(f"%{barcode_or_qr}%"))
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product_in: ProductCreate) -> Product:
    """创建新产品；product_in 为 Pydantic 的 ProductCreate 或等价 dict-like 对象"""
    product = Product(
        barcode_or_qr=product_in.barcode_or_qr,
        name=product_in.name,
        category_id=product_in.category_id,
        created_by_admin_id=getattr(product_in, 'created_by_admin_id', None),
        production_date=getattr(product_in, 'production_date', None),
        expiration_date=getattr(product_in, 'expiration_date', None),
        batch_number=getattr(product_in, 'batch_number', None),
        description=getattr(product_in, 'description', None),
        image_url=getattr(product_in, 'image_url', None),
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # 触发唯一性约束（如 barcode_or_qr 重复）时抛出异常，调用方可捕获并返回友好提示
        raise
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, product_in: ProductUpdate) -> Product:
    """更新产品字段（部分更新），传入已加载的 product 实例和 ProductUpdate schema"""
    data = product_in.__dict__ if hasattr(product_in, '__dict__') else dict(product_in)
    for field, value in data.items():
        if value is None:
            continue
        # 只更新模型中存在的属性
        if hasattr(product, field):
            setattr(product, field, value)
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: str) -> bool:
    """删除产品，返回是否成功"""
    product = get_product_by_id(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


def count_products(
    db: Session,
    name: Optional[str] = None,
    category_id: Optional[str] = None,
    created_by_admin_id: Optional[str] = None,
    barcode_or_qr: Optional[str] = None
) -> int:
    """统计产品总数，支持多条件过滤"""
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if created_by_admin_id:
        query = query.filter(Product.created_by_admin_id == created_by_admin_id)
    if barcode_or_qr:
        query = query.filter(Product.barcode_or_qr.ilike(f"%{barcode_or_qr}%"))
    return query.count()


def get_products_by_category(db: Session, category_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
    """根据分类ID获取产品列表"""
    return db.query(Product).filter(Product.category_id == category_id).offset(skip).limit(limit).all()


def get_products_by_admin(db: Session, admin_id: str, skip: int = 0, limit: int = 100) -> List[Product]:
    """根据管理员ID获取该管理员创建的产品列表"""
    return db.query(Product).filter(Product.created_by_admin_id == admin_id).offset(skip).limit(limit).all()


def search_products_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Product]:
    """根据产品名称模糊搜索产品"""
    return db.query(Product).filter(Product.name.ilike(f"%{name}%")).offset(skip).limit(limit).all()


def get_expired_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """获取已过期的产品列表"""
    from datetime import date
    today = date.today()
    return db.query(Product).filter(Product.expiration_date < today).offset(skip).limit(limit).all()


def get_expiring_soon_products(db: Session, days: int = 7, skip: int = 0, limit: int = 100) -> List[Product]:
    """获取即将过期的产品列表（默认7天内）"""
    from datetime import date, timedelta
    today = date.today()
    expiry_date = today + timedelta(days=days)
    return db.query(Product).filter(
        Product.expiration_date.between(today, expiry_date)
    ).offset(skip).limit(limit).all()



