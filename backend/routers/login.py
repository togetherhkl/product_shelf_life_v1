from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from services import wx_service


router = APIRouter(tags=["login"])

class WxLoginRequest(BaseModel):
    code: str
    avatar_url: str
    nickname: str

@router.post("/login/wx")
async def wx_login(data: WxLoginRequest):
    """
    微信小程序登录，前端传递 code，后端获取openid并生成JWT
    """
    result = await wx_service.wx_login(data)
    if not result:
        raise HTTPException(status_code=400, detail="登录失败")
    return result



