from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm_models import Category
from schemas.orm_schema import CategoryCreate, CategoryUpdate


def get_category_by_id(db: Session, category_id: str) -> Optional[Category]:
    """根据 category_id 查询分类"""
    return db.query(Category).filter(Category.category_id == category_id).first()


def get_category_by_name(db: Session, category_name: str) -> Optional[Category]:
    """根据分类名称查询分类"""
    return db.query(Category).filter(Category.category_name == category_name).first()


def list_categories(db: Session, skip: int = 0, limit: int = 100, category_name: Optional[str] = None) -> List[Category]:
    """分页列出分类，支持分类名称模糊搜索"""
    query = db.query(Category)
    if category_name:
        query = query.filter(Category.category_name.ilike(f"%{category_name}%"))
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category_in: CategoryCreate) -> Category:
    """创建新分类；category_in 为 Pydantic 的 CategoryCreate 或等价 dict-like 对象"""
    category = Category(
        category_name=category_in.category_name,
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # 触发唯一性约束（如 category_name 重复）时抛出异常，调用方可捕获并返回友好提示
        raise
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, category_in: CategoryUpdate) -> Category:
    """更新分类字段（部分更新），传入已加载的 category 实例和 CategoryUpdate schema"""
    data = category_in.__dict__ if hasattr(category_in, '__dict__') else dict(category_in)
    for field, value in data.items():
        if value is None:
            continue
        # 只更新模型中存在的属性
        if hasattr(category, field):
            setattr(category, field, value)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: str) -> bool:
    """删除分类，返回是否成功"""
    category = get_category_by_id(db, category_id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True


def count_categories(db: Session, category_name: Optional[str] = None) -> int:
    """统计分类总数，支持按名称过滤"""
    query = db.query(Category)
    if category_name:
        query = query.filter(Category.category_name.ilike(f"%{category_name}%"))
    return query.count()
