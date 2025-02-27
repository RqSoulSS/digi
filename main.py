from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
import time
from database import init_db, save_order, update_order, get_order, get_orders_by_status
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Твой ID продавца в Digiseller
DIGISELLER_SELLER_ID = "1112289"

# Твой API-ключ Digiseller
DIGISELLER_API_KEY = "59222275B5D04373BF47C4DF9686E73B"

# URL API Digiseller
DIGISELLER_API_URL = "https://api.digiseller.ru/api/order/info"

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Инициализируем базу данных
init_db()

# Функция для проверки статуса заказов
def check_orders_status():
    orders = get_orders_by_status("waiting")  # Берем только неоплаченные заказы
    headers = {"Authorization": f"Bearer {DIGISELLER_API_KEY}"}  # Добавляем API-ключ в заголовки

    for unique_code in orders:
        response = requests.get(DIGISELLER_API_URL, 
                                params={"id_seller": DIGISELLER_SELLER_ID, "unique_code": unique_code}, 
                                headers=headers)  # Отправляем запрос
        data = response.json()

        if data.get("order", {}).get("status") == "delivered":
            update_order(unique_code, "delivered", time.time())

# Запускаем фоновую проверку каждые 5 минут
scheduler = BackgroundScheduler()
scheduler.add_job(check_orders_status, "interval", minutes=5)
scheduler.start()

# Webhook для Digiseller (получение данных о новом заказе)
@app.post("/digiseller-webhook")
async def digiseller_webhook(data: dict):
    unique_code = data.get("unique_code")
    quantity = data.get("quantity", 1)

    if unique_code:
        save_order(unique_code, quantity)
        return RedirectResponse(url=f"/order/{unique_code}")

    return {"status": "error", "message": "Invalid data"}

# Страница заказа
@app.get("/order/{unique_code}", response_class=HTMLResponse)
async def order_page(request: Request, unique_code: str):
    order = get_order(unique_code)
    if not order:
        return HTMLResponse("Заказ не найден", status_code=404)

    order_id, unique_code, quantity, status, timestamp = order
    remaining_time = max(0, 120 * 3600 - (time.time() - timestamp)) if timestamp else None

    return templates.TemplateResponse("order.html", {
        "request": request,
        "unique_code": unique_code,
        "quantity": quantity,
        "status": status,
        "oplata_url": f"https://oplata.info/info/?code={unique_code}",
        "remaining_time": remaining_time
    })
