from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm_models import Admin
from schemas.orm_schema import AdminCreate, AdminUpdate


def get_admin_by_id(db: Session, admin_id: str) -> Optional[Admin]:
    """根据 admin_id 查询管理员"""
    return db.query(Admin).filter(Admin.admin_id == admin_id).first()


def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    """根据 username 查询管理员"""
    return db.query(Admin).filter(Admin.username == username).first()


def list_admins(db: Session, skip: int = 0, limit: int = 100, username: Optional[str] = None, role: Optional[str] = None) -> List[Admin]:
    """分页列出管理员，支持用户名模糊搜索和角色精确匹配"""
    query = db.query(Admin)
    if username:
        query = query.filter(Admin.username.ilike(f"%{username}%"))
    if role:
        query = query.filter(Admin.role == role)
    return query.offset(skip).limit(limit).all()


def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
    """创建新管理员；admin_in 为 Pydantic 的 AdminCreate 或等价 dict-like 对象"""
    admin = Admin(
        username=admin_in.username,
        password_hash=admin_in.password_hash,
        role=admin_in.role,
        is_active=getattr(admin_in, 'is_active', 1),
    )
    db.add(admin)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # 触发唯一性约束（如 username 重复）时抛出异常，调用方可捕获并返回友好提示
        raise
    db.refresh(admin)
    return admin


def update_admin(db: Session, admin: Admin, admin_in: AdminUpdate) -> Admin:
    """更新管理员字段（部分更新），传入已加载的 admin 实例和 AdminUpdate schema"""
    data = admin_in.__dict__ if hasattr(admin_in, '__dict__') else dict(admin_in)
    for field, value in data.items():
        if value is None:
            continue
        # 只更新模型中存在的属性
        if hasattr(admin, field):
            setattr(admin, field, value)
    # print("更新后的admin信息：", admin)
    db.add(admin)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(admin)
    return admin


def delete_admin(db: Session, admin_id: str) -> bool:
    """删除管理员，返回是否成功"""
    admin = get_admin_by_id(db, admin_id)
    if not admin:
        return False
    db.delete(admin)
    db.commit()
    return True


def count_admins(db: Session, username: Optional[str] = None, role: Optional[str] = None) -> int:
    """统计管理员总数，支持用户名和角色过滤"""
    query = db.query(Admin)
    if username:
        query = query.filter(Admin.username.ilike(f"%{username}%"))
    if role:
        query = query.filter(Admin.role == role)
    return query.count()