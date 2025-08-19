# core/crawler.py
import requests
from bs4 import BeautifulSoup
import logging
import random
from typing import Tuple, Optional, Dict, List
from config import USER_AGENTS, PROXIES


class WebCrawler:
    """
    负责从URL提取主要文本内容，内置反爬机制。
    """

    def __init__(self):
        self.user_agents: List[str] = USER_AGENTS
        self.proxies_list: List[str] = PROXIES

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """如果配置了代理，则随机选择一个并格式化。"""
        if not self.proxies_list:
            return None
        proxy_url = random.choice(self.proxies_list)
        return {"http": proxy_url, "https": proxy_url}

    def extract_content(self, url: str) -> Tuple[bool, str]:
        """
        从URL提取网页的主要文本内容。
        :return: 元组 (success, content_or_error_message)。
        """
        if not url or not url.startswith(('http://', 'https://')):
            return False, "无效的URL"

        headers = {'User-Agent': random.choice(self.user_agents)}
        proxies = self.get_random_proxy()

        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 移除所有非内容标签，增强正文提取效果
            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'figure', 'figcaption']):
                tag.decompose()

            # **优化点1: 智能定位正文区域**
            # 优先寻找<article>或<main>标签，如果找不到，再使用整个<body>
            article_body = soup.find('article') or soup.find('main') or soup.body
            if not article_body: return False, "无法定位内容区域"

            text = article_body.get_text(separator='\n', strip=True)
            lines = (line.strip() for line in text.splitlines())

            # **优化点2: 放宽文本行长度限制**
            # 将单词数限制从5个降低到2个，以保留更多短句
            long_lines = [line for line in lines if len(line.split()) > 2]
            content = '\n'.join(long_lines)

            if not content: return False, "提取内容为空"

            logging.info(f"成功从 {url} 提取内容, 长度: {len(content)}")
            return True, content

        except requests.exceptions.Timeout:
            return False, "请求超时"
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP错误: {e.response.status_code}"
        except requests.RequestException as e:
            return False, f"请求失败: {type(e).__name__}"
        except Exception as e:
            logging.error(f"爬取 {url} 时发生未知错误: {e}", exc_info=True)
            return False, "未知错误"
