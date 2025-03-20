from services.astrology import compute_astrology
from services.chart_generator import generate_chart_image
from pydantic import BaseModel
import datetime
import asyncio
import time

# 创建测试数据
class TestBirthData(BaseModel):
    name: str
    birth_date: datetime.datetime
    utcoffset: int
    latitude: float
    longitude: float
    city: str = None


test_data = TestBirthData(
    name="测试用户3",
    birth_date=datetime.datetime(2004, 7, 30, 10, 0),
    utcoffset=8, # 时区
    latitude=39.9042,
    longitude=116.4074,
    city="北京"
)

# 执行计算并打印结果，并计时
start_time = time.time()
result = compute_astrology(test_data)
compute_time = time.time()- start_time

print(f"星盘计算耗时: {compute_time:.4f} 秒")
print(f"行星数量: {len(result['planets'])}")
print(f"宫位数量: {len(result['houses'])}")
print(f"相位数量: {len(result['aspects'])}")

# result = compute_astrology(test_data)
# print(f"行星数量: {len(result['planets'])}")
# print(result['planets'])
# print(f"宫位数量: {len(result['houses'])}")
# print(result['houses'])
# print(f"相位数量: {len(result['aspects'])}")
# print(result['aspects'])

# 使用上面计算的结果测试图像生成, 添加计时功能
async def test_image_generation():
    result = compute_astrology(test_data)

    # 计算时间
    start_time = time.time()
    image_url = await generate_chart_image(result)
    generate_time = time.time() - start_time

    print(f"图像生成耗时：{generate_time:.4f}秒")
    print(f"生成的图像URL: {image_url}")

    return{
        "compute_time": compute_time,
        "generate_time": generate_time,
        "total_time": compute_time + generate_time,
        "image_url": image_url
    }

# asyncio.run(test_image_generation())
# 执行异步测试并显示结果
result = asyncio.run(test_image_generation())
print(f"总执行时间: {result['total_time']:.4f} 秒")
print(f"计算占比: {(result['compute_time'] / result['total_time'] * 100):.1f}%")
print(f"图像生成占比: {(result['generate_time'] / result['total_time'] * 100):.1f}%")