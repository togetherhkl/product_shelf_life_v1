import uuid
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Date, BigInteger, UniqueConstraint, Boolean
from sqlalchemy.dialects.mysql import CHAR, TINYINT
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

def gen_uuid():
	"""生成UUID字符串"""
	return str(uuid.uuid4())

class Category(Base):
	__tablename__ = 'category'
	# 分类唯一ID，UUID主键
	category_id = Column(CHAR(36), primary_key=True, default=gen_uuid, comment='分类唯一ID')
	# 分类名称
	category_name = Column(String(100), nullable=False, unique=True, comment='分类名称（如：食品、美妆）')
	# 创建时间
	created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')
	# 最后更新时间
	updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='最后更新时间')
	# 关联产品
	products = relationship('Product', back_populates='category')

class Product(Base):
	__tablename__ = 'product'
	# 产品唯一ID，UUID主键
	product_id = Column(CHAR(36), primary_key=True, default=gen_uuid, comment='产品唯一ID')
	# 扫码值（条形码或二维码）
	barcode_or_qr = Column(String(100), nullable=False, unique=True, comment='扫码值（条形码或二维码）')
	# 产品名称
	name = Column(String(255), nullable=False, comment='产品名称')
	# 关联的分类ID
	category_id = Column(CHAR(36), ForeignKey('category.category_id'), nullable=False, comment='关联的分类ID')
	# 添加该产品的管理员ID
	created_by_admin_id = Column(CHAR(36), ForeignKey('admin.admin_id'), nullable=True, comment='添加该产品的管理员ID')
	# 生产日期
	production_date = Column(Date, nullable=True, comment='生产日期')
	# 到期日期
	expiration_date = Column(Date, nullable=True, comment='到期日期')
	# 批次号
	batch_number = Column(String(100), nullable=True, comment='批次号')
	# 产品详细描述
	description = Column(Text, nullable=True, comment='产品详细描述')
	# 产品图像URL
	image_url = Column(String(500), nullable=True, comment='产品图像URL')
	# 创建时间
	created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')
	# 最后更新时间
	updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='最后更新时间')
	# 关联分类
	category = relationship('Category', back_populates='products')
	# 关联添加该产品的管理员
	created_by_admin = relationship('Admin', back_populates='created_products')
	# 关联扫码记录
	scan_histories = relationship('ScanHistory', back_populates='product')

class User(Base):
	__tablename__ = 'user'
	# 用户唯一ID，UUID主键
	user_id = Column(CHAR(36), primary_key=True, default=gen_uuid, comment='用户唯一ID')
	# 微信openid
	openid = Column(String(100), nullable=False, unique=True, comment='微信用户唯一标识')
	# 昵称
	nickname = Column(String(100), nullable=True, comment='昵称')
	# 头像URL
	avatar_url = Column(String(255), nullable=True, comment='头像URL')
	# 账户状态（1:活跃, 0:禁用）
	is_active = Column(TINYINT(1), nullable=False, default=1, comment='账户状态（1:活跃, 0:禁用）')
	# 注册时间
	created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='注册时间')
	# 最后登录时间
	last_login_at = Column(DateTime, nullable=True, comment='最后登录时间')
	# 关联扫码记录
	scan_histories = relationship('ScanHistory', back_populates='user')
	# 手机号
	phone_number = Column(String(20), nullable=True, unique=True, comment='手机号')
	# 邮箱
	email = Column(String(100), nullable=True, unique=True, comment='邮箱')
	# 介绍
	introduction = Column(Text, nullable=True, comment='个人介绍')


class ScanHistory(Base):
	__tablename__ = 'scan_history'
	# 记录唯一ID，UUID主键
	history_id = Column(CHAR(36), primary_key=True, default=gen_uuid, comment='记录唯一ID')
	# 关联的用户ID
	user_id = Column(CHAR(36), ForeignKey('user.user_id'), nullable=False, comment='关联的用户ID')
	# 关联的产品ID
	product_id = Column(CHAR(36), ForeignKey('product.product_id'), nullable=False, comment='关联的产品ID')
	# 扫码发生时间
	scan_time = Column(DateTime, nullable=False, server_default=func.now(), comment='扫码发生时间')
	# 关联用户
	user = relationship('User', back_populates='scan_histories')
	# 关联产品
	product = relationship('Product', back_populates='scan_histories')

class Admin(Base):
	__tablename__ = 'admin'
	# 管理员唯一ID，UUID主键
	admin_id = Column(CHAR(36), primary_key=True, default=gen_uuid, comment='管理员唯一ID')
	# 登录用户名
	username = Column(String(50), nullable=False, unique=True, comment='登录用户名')
	# 加密后的密码
	password_hash = Column(String(255), nullable=False, comment='加密后的密码')
	# 角色
	role = Column(String(50), nullable=False, comment='角色（如：super_admin, editor）')
	# 账户状态（1:活跃, 0:禁用）
	is_active = Column(TINYINT(1), nullable=False, default=1, comment='账户状态（1:活跃, 0:禁用）')
	# 创建时间
	created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='创建时间')
	# 关联该管理员创建的产品
	created_products = relationship('Product', back_populates='created_by_admin')

