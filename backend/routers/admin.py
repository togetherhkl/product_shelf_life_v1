from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from dependencies.db_depend import get_db
from dependencies.admin_auth_depend import get_current_admin, hash_password, verify_password, create_admin_access_token
import crud.admin_crud as admin_crud
from schemas.orm_schema import AdminCreate, AdminRead, AdminUpdate, AdminListResponse
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: str
    username: str
    role: str

@router.post("/login", response_model=AdminLoginResponse)
def admin_login(login_in: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = admin_crud.get_admin_by_username(db, login_in.username)
    if not admin or not verify_password(login_in.password, admin.password_hash) or admin.is_active != 1:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    # 生成 token
    access_token = create_admin_access_token({"sub": admin.admin_id})
    return AdminLoginResponse(
        access_token=access_token,
        admin_id=admin.admin_id,
        username=admin.username,
        role=admin.role
    )

@router.post("/", response_model=AdminRead)
def create_admin(admin_in: AdminCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """创建新管理员（需要管理员权限）"""
    # 只有超级管理员能创建管理员
    if current_admin.role != 'super_admin':
        raise HTTPException(status_code=403, detail="仅超级管理员可创建新管理员")
    admin_data = admin_in.model_dump()
    admin_data['password_hash'] = hash_password(admin_data['password_hash'])
    admin_in_hashed = AdminCreate(**admin_data)
    try:
        admin = admin_crud.create_admin(db, admin_in_hashed)
        return AdminRead.model_validate(admin)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=AdminRead)
def get_me(current_admin=Depends(get_current_admin)):
    """获取当前登录管理员信息"""
    return AdminRead.model_validate(current_admin)

@router.put("/me", response_model=AdminRead)
def update_me(update_in: AdminUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """更新当前登录管理员的资料（部分更新）"""
    if update_in.password_hash:
        update_in.password_hash = hash_password(update_in.password_hash)
    try:
        current_admin = db.merge(current_admin)
        admin = admin_crud.update_admin(db, current_admin, update_in)
        return AdminRead.model_validate(admin)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{admin_id}", response_model=AdminRead)
def get_admin(admin_id: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """根据 admin_id 查询管理员；仅允许本人或超级管理员"""
    admin = admin_crud.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员未找到")
    # 仅允许本人查看或超级管理员
    if admin.admin_id != current_admin.admin_id and current_admin.role != 'super_admin':
        raise HTTPException(status_code=403, detail="无权查看该管理员信息")
    return AdminRead.model_validate(admin)

@router.get("/", response_model=AdminListResponse)
def list_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    username: Optional[str] = Query(None, description="按用户名模糊搜索"),
    role: Optional[str] = Query(None, description="按角色精确匹配"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """分页列出管理员（需要管理员权限），支持用户名模糊搜索和角色精确匹配"""
    # 获取管理员列表
    admins = admin_crud.list_admins(db, skip=skip, limit=limit, username=username, role=role)
    
    # 获取总数
    total = admin_crud.count_admins(db, username=username, role=role)
    
    return AdminListResponse(
        admins=[AdminRead.model_validate(a) for a in admins],
        total=total
    )

@router.put("/{admin_id}", response_model=AdminRead)
def update_admin(admin_id: str, update_in: AdminUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """更新指定管理员（需要本人或超级管理员权限）"""
    print("更新信息：", update_in)
    admin = admin_crud.get_admin_by_id(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="管理员未找到")
    if admin.admin_id != current_admin.admin_id and current_admin.role != 'super_admin':
        raise HTTPException(status_code=403, detail="无权更新该管理员信息")
    if update_in.password_hash:
        update_in.password_hash = hash_password(update_in.password_hash)
    try:
        admin = admin_crud.update_admin(db, admin, update_in)
        return AdminRead.model_validate(admin)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{admin_id}")
def delete_admin(admin_id: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """删除管理员（需要超级管理员权限）"""
    if current_admin.role != 'super_admin':
        raise HTTPException(status_code=403, detail="仅超级管理员可删除管理员")
    ok = admin_crud.delete_admin(db, admin_id)
    if not ok:
        raise HTTPException(status_code=404, detail="管理员未找到")
    return {"deleted": True}