"""
扫描记录相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from datetime import datetime

from dependencies.db_depend import get_db
from dependencies.admin_auth_depend import get_current_admin
from dependencies.auth_depend import get_current_user
import crud.scan_crud as scan_crud
import crud.user_crud as user_crud
import crud.product_crud as product_crud
from schemas.orm_schema import (
    ScanHistoryCreate, ScanHistoryRead, ScanHistoryWithDetails, 
    ScanHistoryListResponse, ScanStatistics, UserExpiredProductsResponse
)

router = APIRouter(prefix="/scan", tags=["scan"])


# @router.post("/", response_model=ScanHistoryRead)
@router.post("/")
def create_scan_record(
    scan_data: ScanHistoryCreate,
    db: Session = Depends(get_db),
    current_user =Depends(get_current_user)
):
    """创建扫描记录（公开接口）"""
    # 验证用户是否存在
    user = user_crud.get_user_by_id(db, current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # # 验证产品是否存在
    product = product_crud.get_product_by_id(db, scan_data.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 判断扫描记录是否存在
    existing_scan = scan_crud.check_user_scanned_product(db, user.user_id, scan_data.product_id)
    if existing_scan:
        # 更新扫描时间
        existing_scan.scan_time = datetime.now()
        db.commit()
        db.refresh(existing_scan)
        return ScanHistoryRead.model_validate(existing_scan)
    else:   
        # 创建扫描记录
        scan_history = scan_crud.create_scan_history(db, scan_data, user.user_id)
        return ScanHistoryRead.model_validate(scan_history)


@router.get("/{history_id}", response_model=ScanHistoryWithDetails)
def get_scan_record(
    history_id: str,
    db: Session = Depends(get_db)
):
    """获取扫描记录详情（公开接口）"""
    scan_history = scan_crud.get_scan_history_with_details(db, history_id)
    if not scan_history:
        raise HTTPException(status_code=404, detail="扫描记录不存在")
    return ScanHistoryWithDetails.model_validate(scan_history)


@router.get("/", response_model=ScanHistoryListResponse)
def list_scan_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    user_id: Optional[str] = Query(None, description="按用户ID筛选"),
    product_id: Optional[str] = Query(None, description="按产品ID筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """分页获取扫描记录列表（需要管理员权限）"""
    scan_histories = scan_crud.list_scan_histories(
        db, skip=skip, limit=limit,
        user_id=user_id, product_id=product_id,
        start_date=start_date, end_date=end_date
    )
    
    total = scan_crud.count_scan_histories(
        db, user_id=user_id, product_id=product_id,
        start_date=start_date, end_date=end_date
    )
    
    return ScanHistoryListResponse(
        scan_histories=[ScanHistoryWithDetails.model_validate(s) for s in scan_histories],
        total=total
    )


@router.get("/user/", response_model=ScanHistoryListResponse)
def get_user_scan_records(
    current_user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取用户的扫描记录（公开接口）"""
    scan_histories = scan_crud.get_user_scan_histories(db, current_user.user_id, skip, limit)
    total = scan_crud.get_user_scan_count(db, current_user.user_id)
    
    return ScanHistoryListResponse(
        scan_histories=[ScanHistoryWithDetails.model_validate(s) for s in scan_histories],
        total=total
    )


@router.get("/user/expired-products", response_model=UserExpiredProductsResponse)
def get_user_expired_products(
    current_user=Depends(get_current_user),
    days_threshold: int = Query(7, ge=1, le=30, description="即将过期的天数阈值（默认7天）"),
    db: Session = Depends(get_db)
):
    """
    获取用户扫描过的已过期和即将过期的产品（公开接口）
    
    返回：
    - expired_products: 已过期的产品列表
    - expiring_soon_products: 即将过期的产品列表（在指定天数内）
    - expired_count: 已过期产品数量
    - expiring_soon_count: 即将过期产品数量
    - total_count: 总数量
    """
    result = scan_crud.get_user_expired_and_expiring_products(
        db, 
        current_user.user_id, 
        days_threshold
    )
    
    return UserExpiredProductsResponse(**result)



@router.get("/product/{product_id}", response_model=ScanHistoryListResponse)
def get_product_scan_records(
    product_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取产品的扫描记录（公开接口）"""
    # 验证产品是否存在
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    scan_histories = scan_crud.get_product_scan_histories(db, product_id, skip, limit)
    total = scan_crud.get_product_scan_count(db, product_id)
    
    return ScanHistoryListResponse(
        scan_histories=[ScanHistoryWithDetails.model_validate(s) for s in scan_histories],
        total=total
    )


@router.get("/recent/list", response_model=ScanHistoryListResponse)
def get_recent_scan_records(
    hours: int = Query(24, ge=1, le=168, description="最近几小时"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """获取最近的扫描记录（需要管理员权限）"""
    scan_histories = scan_crud.get_recent_scan_histories(db, hours, skip, limit)
    
    # 计算总数
    from datetime import datetime, timedelta
    cutoff_time = datetime.now() - timedelta(hours=hours)
    total = scan_crud.count_scan_histories(
        db, start_date=cutoff_time.date()
    )
    
    return ScanHistoryListResponse(
        scan_histories=[ScanHistoryWithDetails.model_validate(s) for s in scan_histories],
        total=total
    )


@router.get("/statistics/overview", response_model=ScanStatistics)
def get_scan_statistics(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """获取扫描统计信息（需要管理员权限）"""
    stats = scan_crud.get_scan_statistics(db)
    return ScanStatistics(**stats)


@router.get("/statistics/popular-products")
def get_popular_products(
    days: int = Query(7, ge=1, le=365, description="统计天数"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取热门产品（公开接口）"""
    return scan_crud.get_popular_products(db, days, limit)


@router.get("/statistics/active-users")
def get_active_users(
    days: int = Query(7, ge=1, le=365, description="统计天数"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """获取活跃用户（需要管理员权限）"""
    return scan_crud.get_active_users(db, days, limit)


@router.get("/statistics/daily-count")
def get_daily_scan_count(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """获取每日扫描统计（需要管理员权限）"""
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="日期范围不能超过365天")
    
    return scan_crud.get_daily_scan_count(db, start_date, end_date)


@router.delete("/{history_id}")
def delete_scan_record(
    history_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """删除扫描记录（需要管理员权限）"""
    success = scan_crud.delete_scan_history(db, history_id)
    if not success:
        raise HTTPException(status_code=404, detail="扫描记录不存在")
    return {"deleted": True}


@router.delete("/user/{user_id}/all")
def delete_user_scan_records(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """删除用户的所有扫描记录（需要管理员权限）"""
    # 验证用户是否存在
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    deleted_count = scan_crud.delete_user_scan_histories(db, user_id)
    return {"deleted_count": deleted_count}


@router.delete("/product/{product_id}/all")
def delete_product_scan_records(
    product_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """删除产品的所有扫描记录（需要管理员权限）"""
    # 验证产品是否存在
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    deleted_count = scan_crud.delete_product_scan_histories(db, product_id)
    return {"deleted_count": deleted_count}


@router.get("/check/{user_id}/{product_id}")
def check_user_scanned_product(
    user_id: str,
    product_id: str,
    db: Session = Depends(get_db)
):
    """检查用户是否扫描过某个产品（公开接口）"""
    # 验证用户和产品是否存在
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    scanned = scan_crud.check_user_scanned_product(db, user_id, product_id)
    
    return {"scanned": scanned}