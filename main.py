import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
from services.astrology import compute_astrology
from services.chart_generator import generate_chart_image
from services.memory_cache import redis_client
# import time
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="星盘分析系统")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 添加CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BirthSchema(BaseModel):
    name: str
    birth_date: datetime.datetime
    latitude: float
    longitude: float
    city: Optional[str] = None
    utcoffset: Optional[int] = 8  # 默认使用中国标准时间

@app.post("/v1/chart")
async def calculate_chart(birth_data: BirthSchema, background_tasks: BackgroundTasks):
    """
    计算星盘并返回数据
    """
    # 记录开始时间
    # start_time = time.time()
    
    # # 生成缓存键
    cache_key = f"chart:{birth_data.name}:{birth_data.birth_date.isoformat()}:{birth_data.latitude}:{birth_data.longitude}"
    
    # 检查缓存中是否有结果
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return {
            "data": cached_data, 
            "source": "cache",
            # "processing_time": time.time() - start_time
        }
    
    # 调用天文计算模块
    # compute_start = time.time()
    chart_data = compute_astrology(birth_data)
    # compute_time = time.time() - compute_start
    
    # # 将结果存入缓存
    redis_client.set(cache_key, chart_data, ex=3600)  # 缓存1小时

    # 触发异步任务生成图片
    background_tasks.add_task(generate_chart_image, chart_data)
    
    # total_time = time.time() - start_time
    return {
        "data": chart_data, 
        "source": "computed",
        # "processing_time": total_time,
        # "compute_time": compute_time
    }

@app.get("/v1/chart/{chart_id}")
async def get_chart_image(chart_id: str):
    """
    获取已生成的星盘图像
    """
    # 构建图像URL和本地路径
    from services.storage import CHART_URL_BASE, CHART_DIR
    image_url = f"{CHART_URL_BASE}/{chart_id}.png"
    file_path = f"{CHART_DIR}/{chart_id}.png"
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图像尚未生成或不存在")
    
    return {"image_url": image_url}

@app.get("/health")
async def health_check():
    """
    服务健康检查接口
    """
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}
