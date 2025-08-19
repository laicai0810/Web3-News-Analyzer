# config.py
# 在此处管理您的API密钥和模型配置

from typing import List, Dict, Optional

# **重要**: 请将下面的路径替换为您本地chromedriver.exe的完整路径
# Windows示例: "D:\\program\\web3_news_analyzer\\chromedriver.exe" (注意使用双反斜杠)
# macOS/Linux示例: "/home/user/web3_news_analyzer/chromedriver"
WEBDRIVER_PATH = "D:\\program\\web3_news_analyzer\\chromedriver.exe"


# 大模型API配置
LLM_CONFIG: Dict[str, Optional[str]] = {
    "api_key": "YOUR_API_KEY_HERE",
    "base_url": None,
    "model_name": "gpt-3.5-turbo"
}

# 默认使用英文字体以保证兼容性
FONT_PATH = "DejaVuSans.ttf"

# 支持的搜索引擎列表
SUPPORTED_SEARCH_ENGINES: List[str] = ["Bing", "Google", "Baidu", "DuckDuckGo"]

# 预设的加密货币爬取按钮
PRESET_COINS: List[str] = ["BTC", "ETH", "SOL", "BNB"]

# --- 反爬虫配置 ---
USER_AGENTS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
]
PROXIES: List[str] = []
