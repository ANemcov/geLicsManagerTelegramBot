# sources/web_api.py
import logging
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

@app.get("/api")
def index():
    return {"message": "Grotem Lic API is running"}

@app.get("/api/solutions/{solution_name}/licenses")
def get_licenses(solution_name: str, x_telegram_initdata: str = Header(...)):
    bot_token = settings['telegram_bot_token']
        
    # Проверяем подпись initData
    if not is_valid_init_data(x_telegram_initdata, bot_token):
        raise HTTPException(status_code=403, detail="Invalid Telegram initData")

    # Если проверка успешна — вызываем логику лицензий
    if not connector.get_lic_info(solution_name):
        return JSONResponse(status_code=400, content={"error": connector.error_description})

    return connector.data

@app.post("/api/solutions/{solution_name}/reset")
def reset_licenses(solution_name: str):
    if not connector.reset_lic_count(solution_name):
        return JSONResponse(status_code=400, content={"error": connector.error_description})
    return {"status": "ok"}

@app.post("/api/solutions/{solution_name}/set/{count}")
def set_licenses(solution_name: str, count: int):
    if not connector.set_lic_count(solution_name, lic_count=count):
        return JSONResponse(status_code=400, content={"error": connector.error_description})
    return {"status": "ok"}

app.mount("/app", StaticFiles(directory="static", html=True), name="static")
