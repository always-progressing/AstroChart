# run.py
import uvicorn
import os

if __name__ == "__main__":
    # 设置环境变量
    os.environ["CHART_URL_BASE"] = "/static/charts"  # 前端可访问的URL路径
    os.environ["CHART_DIR"] = "static/charts"        # 本地存储目录
    
    # Redis配置（根据你的实际环境修改）
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_PASSWORD"] = ""
    os.environ["REDIS_DB"] = "0"
    
    # 启动服务器，指定端口和主机
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",  # 允许外部访问
        port=8000,       # 与前端配置匹配的端口
        reload=True      # 开发模式下自动重载
    )