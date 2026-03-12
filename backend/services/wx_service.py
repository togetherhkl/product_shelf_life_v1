import requests
from datetime import datetime, timedelta,timezone
from jose import jwt
from sqlalchemy.orm import Session
from core.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,WX_APPID,WX_SECRET
from models.orm_models import User
from core.settings import SessionLocal
import os

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def wx_login(data: str):
    code = data.code
    # 1. 请求微信服务器获取openid
    url = (
        f"https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={WX_APPID}&secret={WX_SECRET}&js_code={code}&grant_type=authorization_code"
    )
    resp = requests.get(url)
    wx_data = resp.json()
    openid = wx_data.get("openid")
    if not openid:
        return None

    # 2. 查找/创建用户
    db: Session = SessionLocal()
    user = db.query(User).filter_by(openid=openid).first()
    if not user:
        user = User(openid=openid, 
                    is_active=1, 
                    last_login_at=datetime.now(),
                    nickname=data.nickname,
                    avatar_url=data.avatar_url)
        db.add(user)
        db.commit()
        db.refresh(user)
    else: # 更新最后登录时间
        user.last_login_at = datetime.now()
        user.is_active = 1
        # user.nickname = data.nickname
        # user.avatar_url = data.avatar_url
        db.commit()
        db.refresh(user)

    # 3. 生成JWT
    access_token = create_access_token({"sub": user.user_id})
    print("Generated access token:", access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "phone_number": user.phone_number,
    }

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        db: Session = SessionLocal()
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None
