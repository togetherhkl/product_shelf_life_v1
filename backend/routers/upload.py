from fastapi import APIRouter, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Literal
from services.file_service import save_file, download_file
import os

router = APIRouter(tags=["upload"])

@router.post("/uploads", description="上传多个文件到指定目录")
async def upload_files(
    files: List[UploadFile],  # 接受多个文件
    file_type: Literal["images", "videos", "audios"] = Query(..., description="文件类型，可选值为 'images', 'videos', 'audios'")
    
):
    """
    上传多个文件到指定目录。
    Args:
        files (List[UploadFile]): 上传的文件列表。
        file_type (Literal): 文件类型，限制为 'images', 'videos', 'audios'。
    Returns:
        dict: 包含上传结果的响应。
    """
    try:
        save_info = save_file(file_type, files)  # 保存每个文件
        return {
            "message": "Files uploaded successfully",
            "file_paths": save_info,
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.get("/download", description="下载指定路径的文件")
async def download_file_route(
    file_path: str = Query(..., description="文件的完整路径")
):
    """
    下载指定路径的文件。
    Args:
        file_path (str): 文件的完整路径。
    Returns:
        FileResponse: 用于下载文件的响应。
    """
    try:
        return download_file(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")