# main.py
from app_ui import create_ui
import logging

if __name__ == "__main__":
    # 配置全局日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
    )

    print("正在启动Web3新闻分析器...")
    print("请在浏览器中打开 http://127.0.0.1:7860")

    app = create_ui()
    app.launch()