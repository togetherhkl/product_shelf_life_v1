from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.orm_models import User
from schemas.orm_schema import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
	"""根据 user_id 查询用户"""
	return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_openid(db: Session, openid: str) -> Optional[User]:
	"""根据 openid 查询用户"""
	return db.query(User).filter(User.openid == openid).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
	"""根据手机号查询用户（如果有）"""
	return db.query(User).filter(User.phone_number == phone).first()

def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nickname: Optional[str] = None,
    phone_number: Optional[str] = None,
    email: Optional[str] = None,
    openid: Optional[str] = None
) -> List[User]:
    """分页列出用户，支持多条件模糊搜索"""
    query = db.query(User)
    if nickname:
        query = query.filter(User.nickname.ilike(f"%{nickname}%"))
    if phone_number:
        query = query.filter(User.phone_number.ilike(f"%{phone_number}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if openid:
        query = query.filter(User.openid.ilike(f"%{openid}%"))
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user_in: UserCreate) -> User:
	"""创建新用户；user_in 为 Pydantic 的 UserCreate 或等价 dict-like 对象"""
	user = User(
		openid=user_in.openid,
		nickname=getattr(user_in, 'nickname', None),
		avatar_url=getattr(user_in, 'avatar_url', None),
		is_active=getattr(user_in, 'is_active', 1),
		phone_number=getattr(user_in, 'phone_number', None),
		email=getattr(user_in, 'email', None),
		introduction=getattr(user_in, 'introduction', None),
	)
	db.add(user)
	try:
		db.commit()
	except IntegrityError as e:
		db.rollback()
		# 触发唯一性约束（如 openid/phone/email 重复）时抛出异常，调用方可捕获并返回友好提示
		raise
	db.refresh(user)
	return user


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
	"""更新用户字段（部分更新），传入已加载的 user 实例和 UserUpdate schema"""
	data = user_in.__dict__ if hasattr(user_in, '__dict__') else dict(user_in)
	for field, value in data.items():
		if value is None:
			continue
		# 只更新模型中存在的属性
		if hasattr(user, field):
			setattr(user, field, value)
	db.add(user)
	try:
		db.commit()
	except IntegrityError:
		db.rollback()
		raise
	db.refresh(user)
	return user


def delete_user(db: Session, user_id: str) -> bool:
	"""删除用户，返回是否成功"""
	user = get_user_by_id(db, user_id)
	if not user:
		return False
	db.delete(user)
	db.commit()
	return True

def count_users(
    db: Session,
    nickname: Optional[str] = None,
    phone_number: Optional[str] = None,
    email: Optional[str] = None,
    openid: Optional[str] = None
) -> int:
    """统计用户总数（支持搜索条件）"""
    query = db.query(User)
    
    # 应用相同的搜索条件
    if nickname:
        query = query.filter(User.nickname.ilike(f"%{nickname}%"))
    if phone_number:
        query = query.filter(User.phone_number.ilike(f"%{phone_number}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if openid:
        query = query.filter(User.openid.ilike(f"%{openid}%"))
    
    return query.count()