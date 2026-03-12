from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# ------------------ Category ------------------
class CategoryBase(BaseModel):
	category_name: str = Field(..., description="分类名称（如：食品、美妆）")

class CategoryCreate(CategoryBase):
	pass

class CategoryUpdate(BaseModel):
	category_name: Optional[str] = Field(None, description="分类名称（如：食品、美妆）")

class CategoryRead(CategoryBase):
	category_id: str
	created_at: datetime
	updated_at: datetime
	model_config = {"from_attributes": True}

class CategorySimple(BaseModel):
	"""简化的分类信息，用于嵌套返回"""
	category_id: str
	category_name: str
	model_config = {"from_attributes": True}

class CategoryListResponse(BaseModel):
    """分类列表响应模型"""
    categories: List[CategoryRead]
    total: int

# ------------------ Product ------------------
class ProductBase(BaseModel):
	barcode_or_qr: str = Field(..., description="扫码值（条形码或二维码）")
	name: str = Field(..., description="产品名称")
	category_id: str = Field(..., description="关联的分类ID")
	created_by_admin_id: Optional[str] = Field(None, description="添加该产品的管理员ID")
	production_date: Optional[date] = Field(None, description="生产日期")
	expiration_date: Optional[date] = Field(None, description="到期日期")
	batch_number: Optional[str] = Field(None, description="批次号")
	description: Optional[str] = Field(None, description="产品详细描述")
	image_url: Optional[str] = Field(None, description="产品图像URL")

class ProductCreate(ProductBase):
	pass

class ProductUpdate(BaseModel):
	barcode_or_qr: Optional[str] = None
	name: Optional[str] = None
	category_id: Optional[str] = None
	created_by_admin_id: Optional[str] = None
	production_date: Optional[date] = None
	expiration_date: Optional[date] = None
	batch_number: Optional[str] = None
	description: Optional[str] = None
	image_url: Optional[str] = None

class ProductRead(ProductBase):
	product_id: str
	created_at: datetime
	updated_at: datetime
	model_config = {"from_attributes": True}

# ------------------ Admin ------------------
class AdminBase(BaseModel):
	username: str = Field(..., description="登录用户名")
	password_hash: str = Field(..., description="加密后的密码")
	role: str = Field(..., description="角色（如：super_admin, editor）")
	is_active: int = Field(..., description="账户状态（1:活跃, 0:禁用）")

class AdminCreate(AdminBase):
	pass

class AdminUpdate(BaseModel):
	password_hash: Optional[str] = None
	role: Optional[str] = None
	is_active: Optional[int] = None
	username: Optional[str] = None

class AdminRead(AdminBase):
	admin_id: str
	created_at: datetime
	model_config = {"from_attributes": True}

class AdminSimple(BaseModel):
	"""简化的管理员信息，用于嵌套返回"""
	admin_id: str
	username: str
	model_config = {"from_attributes": True}

class AdminListResponse(BaseModel):
    """管理员列表响应模型"""
    admins: List[AdminRead]
    total: int

# ------------------ User ------------------
class UserBase(BaseModel):
	openid: str = Field(..., description="微信用户唯一标识")
	nickname: Optional[str] = Field(None, description="昵称")
	avatar_url: Optional[str] = Field(None, description="头像URL")
	is_active: int = Field(1, description="账户状态（1:活跃, 0:禁用）")
	phone_number: Optional[str] = Field(None, description="手机号")
	email: Optional[str] = Field(None, description="邮箱")
	introduction: Optional[str] = Field(None, description="个人介绍")

class UserCreate(UserBase):
	pass

class UserUpdate(BaseModel):
	nickname: Optional[str] = None
	avatar_url: Optional[str] = None
	is_active: Optional[int] = None
	phone_number: Optional[str] = None
	email: Optional[str] = None
	introduction: Optional[str] = None

class UserRead(UserBase):
	user_id: str
	created_at: datetime
	last_login_at: Optional[datetime] = None
	model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserRead]
    total: int

# ------------------ Product Extended Models ------------------
class ProductReadWithRelations(ProductBase):
	"""带关联信息的产品读取模型"""
	product_id: str
	created_at: datetime
	updated_at: datetime
	category: Optional[CategorySimple] = None
	created_by_admin: Optional[AdminSimple] = None
	model_config = {"from_attributes": True}

class ProductListResponse(BaseModel):
    """产品列表响应模型"""
    products: List[ProductReadWithRelations]
    total: int

class OpenFoodFactsResponse(BaseModel):
    """OpenFoodFacts API 响应模型"""
    barcode_or_qr: str
    name: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    created_by_admin_id: Optional[str] = None
    production_date: Optional[date] = None
    expiration_date: Optional[date] = None
    batch_number: Optional[str] = None
    status: str = Field(..., description="请求状态: success, not_found, ssl_error, timeout, network_error, unknown_error")
    message: str = Field(..., description="状态描述信息")

# ------------------ ScanHistory ------------------
class ScanHistoryBase(BaseModel):
    user_id: str = Field(..., description="关联的用户ID")
    product_id: str = Field(..., description="关联的产品ID")

class ScanHistoryCreate(BaseModel):
    product_id: str = Field(..., description="关联的产品ID")

class ScanHistoryRead(ScanHistoryBase):
    history_id: str
    scan_time: datetime
    model_config = {"from_attributes": True}

class ScanHistoryWithDetails(BaseModel):
    """带详细信息的扫描记录"""
    history_id: str
    scan_time: datetime
    user: Optional[UserRead] = None
    product: Optional[ProductRead] = None
    model_config = {"from_attributes": True}

class ScanHistoryListResponse(BaseModel):
    """扫描记录列表响应模型"""
    scan_histories: List[ScanHistoryWithDetails]
    total: int

class ScanStatistics(BaseModel):
    """扫描统计信息"""
    total_scans: int = Field(..., description="总扫描次数")
    unique_users: int = Field(..., description="独立用户数")
    unique_products: int = Field(..., description="独立产品数")
    today_scans: int = Field(..., description="今日扫描次数")
    week_scans: int = Field(..., description="本周扫描次数")
    month_scans: int = Field(..., description="本月扫描次数")

class ExpiredProductInfo(BaseModel):
    """过期产品信息"""
    product_id: str
    name: str
    barcode_or_qr: str
    expiration_date: Optional[date] = None
    production_date: Optional[date] = None
    batch_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[CategorySimple] = None
    scan_time: datetime = Field(..., description="用户扫描该产品的时间")
    days_since_expired: Optional[int] = Field(None, description="已过期天数（正数表示已过期天数）")
    days_until_expiration: Optional[int] = Field(None, description="距离过期天数（正数表示还有几天过期，负数表示已过期）")
    status: str = Field(..., description="状态：expired（已过期）或 expiring_soon（即将过期）")

class UserExpiredProductsResponse(BaseModel):
    """用户过期产品响应模型"""
    expired_products: List[ExpiredProductInfo] = Field(..., description="已过期的产品列表")
    expiring_soon_products: List[ExpiredProductInfo] = Field(..., description="即将过期的产品列表")
    expired_count: int = Field(..., description="已过期产品数量")
    expiring_soon_count: int = Field(..., description="即将过期产品数量")
    total_count: int = Field(..., description="总数量")
