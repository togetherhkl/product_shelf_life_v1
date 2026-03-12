from fastapi import UploadFile
from fastapi.responses import FileResponse
from typing import List
import datetime
import os


def save_file(file_type: str, files: List[UploadFile]):
    """
    Save the uploaded file to the specified directory.
    """
    # Create the directory if it doesn't exist
    upload_dir = os.path.join("static", file_type)
    os.makedirs(upload_dir, exist_ok=True)

    #存储上传成功的文件路径
    uploaded_files = []

    for file in files:
        # 使用时间戳给文件重命名，防止重复
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        new_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, new_filename)

        # 使用 file.read() 读取文件内容
        with open(file_path, "wb") as f:
            f.write(file.file.read())  # 修正为 file.file.read()
        uploaded_files.append(file_path)
    # 返回上传成功的文件路径
    return uploaded_files


def download_file(file_path: str) -> FileResponse:
    """
    下载指定路径的文件
    Args:
        file_path (str): 文件的完整路径
    Returns:
        FileResponse: 用于下载文件的响应
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),  # 下载时的文件名
        media_type="application/octet-stream"  # 设置为通用二进制流
    )