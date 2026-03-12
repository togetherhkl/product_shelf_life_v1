from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.db_depend import get_db
from dependencies.admin_auth_depend import get_current_admin
import crud.category_crud as category_crud
from schemas.orm_schema import CategoryCreate, CategoryRead, CategoryUpdate, CategoryListResponse

router = APIRouter(prefix="/category", tags=["category"])

@router.post("/", response_model=CategoryRead)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """创建新分类（需要管理员权限）"""
    # 检查分类名称是否已存在
    existing = category_crud.get_category_by_name(db, category_in.category_name)
    if existing:
        raise HTTPException(status_code=400, detail="分类名称已存在")
    try:
        category = category_crud.create_category(db, category_in)
        return CategoryRead.model_validate(category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: str, db: Session = Depends(get_db)):
    """根据 category_id 查询分类（公开接口）"""
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类未找到")
    return CategoryRead.model_validate(category)

@router.get("/", response_model=CategoryListResponse)
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=2000),
    category_name: Optional[str] = Query(None, description="按分类名称模糊搜索"),
    db: Session = Depends(get_db)
):
    """分页列出分类（公开接口），支持分类名称模糊搜索"""
    # 获取分类列表
    categories = category_crud.list_categories(db, skip=skip, limit=limit, category_name=category_name)
    
    # 获取总数
    total = category_crud.count_categories(db, category_name=category_name)
    
    return CategoryListResponse(
        categories=[CategoryRead.model_validate(c) for c in categories],
        total=total
    )

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: str, category_in: CategoryUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """更新分类（需要管理员权限）"""
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类未找到")
    
    # 如果要更新分类名称，检查新名称是否已存在
    if category_in.category_name:
        existing = category_crud.get_category_by_name(db, category_in.category_name)
        if existing and existing.category_id != category_id:
            raise HTTPException(status_code=400, detail="分类名称已存在")
    
    try:
        category = category_crud.update_category(db, category, category_in)
        return CategoryRead.model_validate(category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
def delete_category(category_id: str, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    """删除分类（需要管理员权限）"""
    # 检查分类是否有关联的产品
    category = category_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类未找到")
    
    # 检查是否有产品使用该分类
    if category.products:
        raise HTTPException(status_code=400, detail="无法删除分类：该分类下还有产品")
    
    ok = category_crud.delete_category(db, category_id)
    if not ok:
        raise HTTPException(status_code=404, detail="分类未找到")
    return {"deleted": True}

@router.get("/count/total")
def count_categories(
    category_name: Optional[str] = Query(None, description="按分类名称过滤统计"),
    db: Session = Depends(get_db)
):
    """统计分类总数（公开接口）"""
    count = category_crud.count_categories(db, category_name=category_name)
    return {"total": count}
