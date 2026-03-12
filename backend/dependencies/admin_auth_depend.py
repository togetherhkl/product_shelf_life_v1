from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt
from core.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from dependencies.db_depend import get_db
import crud.admin_crud as admin_crud
import hashlib
from services import wx_service  # 假设这是用户验证函数

bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """简单密码哈希，使用 SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

def create_admin_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_admin_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        if not admin_id:
            return None
        admin = admin_crud.get_admin_by_id(db, admin_id)
        if not admin or admin.is_active != 1:
            return None
        return admin
    except Exception:
        return None

async def get_current_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme), 
                            db: Session = Depends(get_db)):
    """
    强制管理员登录依赖：
    - 未提供 token -> 抛出 401
    - 提供但 token 无效 -> 抛出 401
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未提供认证信息")
    token = credentials.credentials
    admin = verify_admin_token(token, db)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效或已过期")
    return admin

from dependencies.admin_auth_depend import verify_admin_token  # 导入管理员验证函数

async def get_current_user_or_admin(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
                                    db: Session = Depends(get_db)):
    """
    联合依赖：尝试验证用户 token，如果失败，尝试管理员 token。
    返回 (user, admin) 元组，其中一个为实例，另一个为 None。
    如果两个都无效，返回 (None, None)。
    """
    if credentials is None:
        return None, None
    token = credentials.credentials
    
    # 先尝试用户 token
    user = wx_service.verify_token(token)  # 假设这是用户验证函数
    if user:
        return user, None
    
    # 如果用户验证失败，尝试管理员 token
    admin = verify_admin_token(token, db)
    if admin:
        return None, admin
    
    return None, None