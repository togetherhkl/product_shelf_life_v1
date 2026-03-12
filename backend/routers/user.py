from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dependencies.db_depend import get_db
from dependencies.auth_depend import get_current_user
import crud.user_crud as user_crud
from schemas.orm_schema import UserCreate, UserRead, UserUpdate, UserListResponse
from dependencies.admin_auth_depend import get_current_admin,get_current_user_or_admin
from typing import Optional

router = APIRouter(prefix="/user", tags=["user"])

@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """创建新用户（一般通过小程序登录创建）"""
    # 如果 openid 已存在，返回已存在的用户
    existing = user_crud.get_user_by_openid(db, user_in.openid)
    if existing:
        return UserRead.model_validate(existing)
    try:
        user = user_crud.create_user(db, user_in)
        return UserRead.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserRead.model_validate(current_user)


@router.put("/me", response_model=UserRead)
def update_me(update_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """更新当前登录用户的资料（部分更新）"""
    try:
        current_user = db.merge(current_user) 
        user = user_crud.update_user(db, current_user, update_in)
        return UserRead.model_validate(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """根据 user_id 查询用户；仅允许本人访问他人信息需要额外权限，这里限制为本人查询"""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    # 仅允许本人查看
    if user.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="无权查看该用户信息")
    return UserRead.model_validate(user)


@router.get("/", response_model=UserListResponse)  # 修改响应模型
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    nickname: Optional[str] = Query(None, description="按昵称模糊搜索"),
    phone_number: Optional[str] = Query(None, description="按手机号模糊搜索"),
    email: Optional[str] = Query(None, description="按邮箱模糊搜索"),
    openid: Optional[str] = Query(None, description="按 OpenID 模糊搜索"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    """分页列出用户（受保护，需管理员登录），支持多条件搜索"""
    # 获取用户列表
    users = user_crud.list_users(
        db, skip=skip, limit=limit,
        nickname=nickname, phone_number=phone_number, email=email, openid=openid
    )
    
    # 获取总数（需要添加这个方法）
    total = user_crud.count_users(
        db, nickname=nickname, phone_number=phone_number, email=email, openid=openid
    )
    
    return UserListResponse(
        users=[UserRead.model_validate(u) for u in users],
        total=total
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    user_or_admin=Depends(get_current_user_or_admin)
):
    """删除用户，允许本人或管理员删除"""
    current_user, current_admin = user_or_admin
    
    # 如果是管理员，允许删除任何用户
    if current_admin is not None:
        pass  # 管理员权限，无需额外检查
    # 如果是本人，允许删除
    elif current_user is not None and user_id == current_user.user_id:
        pass
    else:
        raise HTTPException(status_code=403, detail="无权删除该用户")
    
    ok = user_crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="用户未找到")
    return {"deleted": True}
