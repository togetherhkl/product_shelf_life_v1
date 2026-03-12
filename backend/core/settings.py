from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

#加载.env文件
load_dotenv('.env')
#数据库连接
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# 密钥
SECRET_KEY = os.getenv('SECRET_KEY')

#后端跨域地址
BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS").split(",")

#项目名称
PROJECT_NAME = os.getenv("PROJECT_NAME")

#微信小程序相关配置
WX_APPID = os.getenv("WX_APPID")
WX_SECRET = os.getenv("WX_SECRET")

#JWT算法
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
#数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
