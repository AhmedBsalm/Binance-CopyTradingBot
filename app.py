from fastapi import FastAPI, BackgroundTasks, HTTPException
import asyncio
import time
from copyTrader import Copytrader



app = FastAPI()

tasks = {}

@app.post("/copyUser/{TRADER_UUID}/{pubkey}/{secretkey}/{leverage}/{usdtamount}")
async def start_copyTrading(background_tasks: BackgroundTasks, TRADER_UUID: str, pubkey: str, secretkey: str, leverage: int, usdtamount: float):
    task_id = str(time.time())
    copier = Copytrader(pubkey, secretkey, leverage, usdtamount, TRADER_UUID)
    loop = asyncio.get_running_loop()
    
    async def start_trading():
        try:
            await copier.run(task_id)
        except asyncio.CancelledError:
            print("Task was cancelled")

    task = loop.create_task(start_trading())
    tasks[task_id] = task
    return {"message": "trading started", "user_id": task_id}

@app.post("/stopTrade/{task_id}")
async def cancel_task(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.cancel()
    return {"message": "Task cancelled", "task_id": task_id}
