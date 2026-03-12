from fastapi import FastAPI,Depends
import uvicorn
from routers import login,user,upload,admin,category,product,scan
from starlette.middleware.cors import CORSMiddleware#解决跨域问题
from fastapi.staticfiles import StaticFiles
from core import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 静态文件服务
app.mount("/api/static", StaticFiles(directory="static"), name="static")
app.include_router(login.router,prefix="/api")
app.include_router(user.router,prefix="/api")
app.include_router(upload.router,prefix="/api")
app.include_router(admin.router,prefix="/api")
app.include_router(category.router,prefix="/api")
app.include_router(product.router,prefix="/api")
app.include_router(scan.router,prefix="/api")




@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)