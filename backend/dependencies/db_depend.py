from core.settings import SessionLocal, engine
from models import orm_models

orm_models.Base.metadata.create_all(bind=engine)

async def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()