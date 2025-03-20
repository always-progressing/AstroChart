import os
import aiofiles
from pathlib import Path

# 配置图片存储路径
CHART_DIR = Path(os.environ.get('CHART_DIR', 'static/charts'))
CHART_URL_BASE = os.environ.get('CHART_URL_BASE', '/static/charts')

# 确保存储目录存在
os.makedirs(CHART_DIR, exist_ok=True)

async def save_chart_image(image_data, filename):
    """
    保存图片到本地文件系统
    
    Args:
        image_data: 文件数据（字节流）
        filename: 文件名
    
    Returns:
        文件URL
    """
    file_path = CHART_DIR / filename
    
    # 异步写入文件
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(image_data.getbuffer())
    
    # 返回可访问URL
    return f"{CHART_URL_BASE}/{filename}"