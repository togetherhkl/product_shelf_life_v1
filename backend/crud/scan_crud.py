"""
扫描记录 CRUD 操作
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc

from models.orm_models import ScanHistory, User, Product
from schemas.orm_schema import ScanHistoryCreate


def create_scan_history(db: Session, scan_data: ScanHistoryCreate, user_id = str) -> ScanHistory:
    """创建新的扫描记录"""
    db_scan = ScanHistory(
        product_id=scan_data.product_id
    )
    db_scan.user_id = user_id
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan


def get_scan_history_by_id(db: Session, history_id: str) -> Optional[ScanHistory]:
    """根据记录ID获取扫描记录"""
    return db.query(ScanHistory).filter(ScanHistory.history_id == history_id).first()


def get_scan_history_with_details(db: Session, history_id: str) -> Optional[ScanHistory]:
    """根据记录ID获取带详细信息的扫描记录"""
    return db.query(ScanHistory).options(
        joinedload(ScanHistory.user),
        joinedload(ScanHistory.product).joinedload(Product.category)
    ).filter(ScanHistory.history_id == history_id).first()


def list_scan_histories(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[ScanHistory]:
    """分页获取扫描记录列表，支持多条件筛选"""
    query = db.query(ScanHistory).options(
        joinedload(ScanHistory.user),
        joinedload(ScanHistory.product).joinedload(Product.category)
    )
    
    # 用户ID筛选
    if user_id:
        query = query.filter(ScanHistory.user_id == user_id)
    
    # 产品ID筛选
    if product_id:
        query = query.filter(ScanHistory.product_id == product_id)
    
    # 日期范围筛选
    if start_date:
        query = query.filter(func.date(ScanHistory.scan_time) >= start_date)
    if end_date:
        query = query.filter(func.date(ScanHistory.scan_time) <= end_date)
    
    return query.order_by(desc(ScanHistory.scan_time)).offset(skip).limit(limit).all()


def count_scan_histories(
    db: Session,
    user_id: Optional[str] = None,
    product_id: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """统计扫描记录总数"""
    query = db.query(ScanHistory)
    
    # 用户ID筛选
    if user_id:
        query = query.filter(ScanHistory.user_id == user_id)
    
    # 产品ID筛选
    if product_id:
        query = query.filter(ScanHistory.product_id == product_id)
    
    # 日期范围筛选
    if start_date:
        query = query.filter(func.date(ScanHistory.scan_time) >= start_date)
    if end_date:
        query = query.filter(func.date(ScanHistory.scan_time) <= end_date)
    
    return query.count()


def get_user_scan_histories(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 20
) -> List[ScanHistory]:
    """获取指定用户的扫描记录"""
    return db.query(ScanHistory).options(
        joinedload(ScanHistory.product).joinedload(Product.category)
    ).filter(
        ScanHistory.user_id == user_id
    ).order_by(desc(ScanHistory.scan_time)).offset(skip).limit(limit).all()


def get_product_scan_histories(
    db: Session, 
    product_id: str, 
    skip: int = 0, 
    limit: int = 20
) -> List[ScanHistory]:
    """获取指定产品的扫描记录"""
    return db.query(ScanHistory).options(
        joinedload(ScanHistory.user)
    ).filter(
        ScanHistory.product_id == product_id
    ).order_by(desc(ScanHistory.scan_time)).offset(skip).limit(limit).all()


def get_recent_scan_histories(
    db: Session, 
    hours: int = 24, 
    skip: int = 0, 
    limit: int = 20
) -> List[ScanHistory]:
    """获取最近几小时的扫描记录"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    return db.query(ScanHistory).options(
        joinedload(ScanHistory.user),
        joinedload(ScanHistory.product).joinedload(Product.category)
    ).filter(
        ScanHistory.scan_time >= cutoff_time
    ).order_by(desc(ScanHistory.scan_time)).offset(skip).limit(limit).all()


def get_popular_products(
    db: Session, 
    days: int = 7, 
    limit: int = 10
) -> List[dict]:
    """获取最近几天扫描次数最多的产品"""
    cutoff_date = date.today() - timedelta(days=days)
    
    result = db.query(
        Product.product_id,
        Product.name,
        Product.image_url,
        func.count(ScanHistory.history_id).label('scan_count')
    ).join(
        ScanHistory, Product.product_id == ScanHistory.product_id
    ).filter(
        func.date(ScanHistory.scan_time) >= cutoff_date
    ).group_by(
        Product.product_id, Product.name, Product.image_url
    ).order_by(
        desc('scan_count')
    ).limit(limit).all()
    
    return [
        {
            'product_id': row.product_id,
            'product_name': row.name,
            'image_url': row.image_url,
            'scan_count': row.scan_count
        }
        for row in result
    ]


def get_active_users(
    db: Session, 
    days: int = 7, 
    limit: int = 10
) -> List[dict]:
    """获取最近几天最活跃的用户"""
    cutoff_date = date.today() - timedelta(days=days)
    
    result = db.query(
        User.user_id,
        User.nickname,
        User.avatar_url,
        func.count(ScanHistory.history_id).label('scan_count')
    ).join(
        ScanHistory, User.user_id == ScanHistory.user_id
    ).filter(
        func.date(ScanHistory.scan_time) >= cutoff_date
    ).group_by(
        User.user_id, User.nickname, User.avatar_url
    ).order_by(
        desc('scan_count')
    ).limit(limit).all()
    
    return [
        {
            'user_id': row.user_id,
            'nickname': row.nickname or '匿名用户',
            'avatar_url': row.avatar_url,
            'scan_count': row.scan_count
        }
        for row in result
    ]


def get_scan_statistics(db: Session) -> dict:
    """获取扫描统计信息"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # 本周一
    month_start = today.replace(day=1)  # 本月第一天
    
    # 总扫描次数
    total_scans = db.query(ScanHistory).count()
    
    # 独立用户数
    unique_users = db.query(ScanHistory.user_id).distinct().count()
    
    # 独立产品数
    unique_products = db.query(ScanHistory.product_id).distinct().count()
    
    # 今日扫描次数
    today_scans = db.query(ScanHistory).filter(
        func.date(ScanHistory.scan_time) == today
    ).count()
    
    # 本周扫描次数
    week_scans = db.query(ScanHistory).filter(
        func.date(ScanHistory.scan_time) >= week_start
    ).count()
    
    # 本月扫描次数
    month_scans = db.query(ScanHistory).filter(
        func.date(ScanHistory.scan_time) >= month_start
    ).count()
    
    return {
        'total_scans': total_scans,
        'unique_users': unique_users,
        'unique_products': unique_products,
        'today_scans': today_scans,
        'week_scans': week_scans,
        'month_scans': month_scans
    }


def get_daily_scan_count(
    db: Session, 
    start_date: date, 
    end_date: date
) -> List[dict]:
    """获取指定日期范围内每日的扫描次数"""
    result = db.query(
        func.date(ScanHistory.scan_time).label('scan_date'),
        func.count(ScanHistory.history_id).label('scan_count')
    ).filter(
        and_(
            func.date(ScanHistory.scan_time) >= start_date,
            func.date(ScanHistory.scan_time) <= end_date
        )
    ).group_by(
        func.date(ScanHistory.scan_time)
    ).order_by('scan_date').all()
    
    return [
        {
            'date': row.scan_date.isoformat(),
            'count': row.scan_count
        }
        for row in result
    ]


def delete_scan_history(db: Session, history_id: str) -> bool:
    """删除扫描记录"""
    scan_history = db.query(ScanHistory).filter(ScanHistory.history_id == history_id).first()
    if scan_history:
        db.delete(scan_history)
        db.commit()
        return True
    return False


def delete_user_scan_histories(db: Session, user_id: str) -> int:
    """删除指定用户的所有扫描记录"""
    deleted_count = db.query(ScanHistory).filter(ScanHistory.user_id == user_id).count()
    db.query(ScanHistory).filter(ScanHistory.user_id == user_id).delete()
    db.commit()
    return deleted_count


def delete_product_scan_histories(db: Session, product_id: str) -> int:
    """删除指定产品的所有扫描记录"""
    deleted_count = db.query(ScanHistory).filter(ScanHistory.product_id == product_id).count()
    db.query(ScanHistory).filter(ScanHistory.product_id == product_id).delete()
    db.commit()
    return deleted_count


def check_user_scanned_product(db: Session, user_id: str, product_id: str) -> bool:
    """检查用户是否扫描过某个产品"""
    return db.query(ScanHistory).filter(
        and_(
            ScanHistory.user_id == user_id,
            ScanHistory.product_id == product_id
        )
    ).first()


def get_user_scan_count(db: Session, user_id: str) -> int:
    """获取用户的总扫描次数"""
    return db.query(ScanHistory).filter(ScanHistory.user_id == user_id).count()


def get_product_scan_count(db: Session, product_id: str) -> int:
    """获取产品的总扫描次数"""
    return db.query(ScanHistory).filter(ScanHistory.product_id == product_id).count()


def get_user_last_scan_time(db: Session, user_id: str) -> Optional[datetime]:
    """获取用户最后一次扫描时间"""
    result = db.query(ScanHistory.scan_time).filter(
        ScanHistory.user_id == user_id
    ).order_by(desc(ScanHistory.scan_time)).first()
    
    return result.scan_time if result else None


def get_user_expired_and_expiring_products(
    db: Session, 
    user_id: str, 
    days_threshold: int = 7
) -> dict:
    """
    获取用户扫描过的已过期和即将过期的产品
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        days_threshold: 即将过期的天数阈值（默认7天）
    
    Returns:
        dict: 包含已过期和即将过期产品列表的字典
    """
    today = date.today()
    expiring_threshold_date = today + timedelta(days=days_threshold)
    
    # 查询用户扫描过的所有产品（关联产品信息和分类信息）
    scan_histories = db.query(ScanHistory).options(
        joinedload(ScanHistory.product).joinedload(Product.category)
    ).filter(
        ScanHistory.user_id == user_id,
        Product.expiration_date.isnot(None)  # 只查询有过期日期的产品
    ).order_by(desc(ScanHistory.scan_time)).all()
    
    expired_products = []
    expiring_soon_products = []
    
    for scan_history in scan_histories:
        product = scan_history.product
        expiration_date = product.expiration_date
        
        if not expiration_date:
            continue
        
        # 计算距离过期天数
        days_until_expiration = (expiration_date - today).days
        
        # 构建产品信息字典
        product_info = {
            'product_id': product.product_id,
            'name': product.name,
            'barcode_or_qr': product.barcode_or_qr,
            'expiration_date': product.expiration_date,
            'production_date': product.production_date,
            'batch_number': product.batch_number,
            'description': product.description,
            'image_url': product.image_url,
            'category': product.category,
            'scan_time': scan_history.scan_time,
            'days_until_expiration': days_until_expiration
        }
        
        # 判断是已过期还是即将过期
        if expiration_date < today:
            # 已过期
            product_info['days_since_expired'] = (today - expiration_date).days
            product_info['status'] = 'expired'
            
            # 检查是否已经在列表中（去重）
            if not any(p['product_id'] == product.product_id for p in expired_products):
                expired_products.append(product_info)
        
        elif expiration_date <= expiring_threshold_date:
            # 即将过期（在阈值天数内）
            # 对于即将过期的产品，days_since_expired 为 None，因为还没过期
            # 使用 days_until_expiration 来查看还有几天过期
            product_info['days_since_expired'] = None
            product_info['status'] = 'expiring_soon'
            
            # 检查是否已经在列表中（去重）
            if not any(p['product_id'] == product.product_id for p in expiring_soon_products):
                expiring_soon_products.append(product_info)
    
    return {
        'expired_products': expired_products,
        'expiring_soon_products': expiring_soon_products,
        'expired_count': len(expired_products),
        'expiring_soon_count': len(expiring_soon_products),
        'total_count': len(expired_products) + len(expiring_soon_products)
    }

