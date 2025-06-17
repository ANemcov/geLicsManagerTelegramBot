# sources/web_api.py
import logging
import httpx
from fastapi import Header
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from bot import GrotemServerConnector
from settings import get_settings
from fastapi import Request, HTTPException, Header
from utils.telegram_auth import is_valid_init_data, get_user_from_init_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

settings = get_settings()
connector = GrotemServerConnector(settings['bitmobile_host'], settings['root_password'])

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

async def send_admin_message(text: str):
    url = f"https://api.telegram.org/bot{settings['telegram_bot_token']}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": settings['admin_chat'], "text": text})

@app.get("/api")
async def index():
    return {"message": "Grotem Lic API is running"}

@app.get("/api/solutions")
async def get_solution_list(x_telegram_initdata: str = Header(...)):
    bot_token = settings['telegram_bot_token']
        
    # Проверяем подпись initData
    if not is_valid_init_data(x_telegram_initdata, bot_token):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    # Если проверка успешна — вызываем логику лицензий
    if not connector.get_solution_list():
        return JSONResponse(status_code=400, content={"error": connector.error_description})

    return connector.data

@app.get("/api/solutions/{solution_name}/licenses")
async def get_licenses(solution_name: str, x_telegram_initdata: str = Header(...)):
    bot_token = settings['telegram_bot_token']
        
    # Проверяем подпись initData
    if not is_valid_init_data(x_telegram_initdata, bot_token):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    # Если проверка успешна — вызываем логику лицензий
    if not connector.get_lic_info(solution_name):
        return JSONResponse(status_code=400, content={"error": connector.error_description})

    return connector.data

@app.post("/api/solutions/{solution_name}/reset")
async def reset_licenses(solution_name: str, x_telegram_initdata: str = Header(...)):
    bot_token = settings['telegram_bot_token']

    # Проверяем подпись initData
    if not is_valid_init_data(x_telegram_initdata, bot_token):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    user = get_user_from_init_data(x_telegram_initdata)
    
    if not connector.reset_lic_count(solution_name):
        return JSONResponse(status_code=400, content={"error": connector.error_description})

    text = (f"Пользователь @{user.get('username', user.get('id'))} "
            f"сбросил лицензии решения '{solution_name}'.")
    
    await send_admin_message(text)
    
    return {"status": "ok"}

@app.post("/api/solutions/{solution_name}/set/{count}")
async def set_licenses(solution_name: str, count: int, x_telegram_initdata: str = Header(...)):
    bot_token = settings['telegram_bot_token']

    # Проверяем подпись initData
    if not is_valid_init_data(x_telegram_initdata, bot_token):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    user = get_user_from_init_data(x_telegram_initdata)

    if not connector.get_lic_info(solution_name):
        return JSONResponse(status_code=400, content={"error": connector.error_description})

    old_total = connector.data.get('TotalLicenses', '?')
    
    if not connector.set_lic_count(solution_name, lic_count=count):
        return JSONResponse(status_code=400, content={"error": connector.error_description})
    
    text = (f"Пользователь @{user.get('username', user.get('id'))} "
            f"изменил количество лицензий решения '{solution_name}': {old_total} → {count}.")
    await send_admin_message(text)
    
    return {"status": "ok"}

app.mount("/app", StaticFiles(directory="static", html=True), name="static")
