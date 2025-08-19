# core/selenium_crawler.py
import logging
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
# **核心改动**: 导入配置
from config import WEBDRIVER_PATH


class SeleniumCrawler:
    """
    使用Selenium驱动真实浏览器进行内容提取，能有效处理JavaScript动态加载的网页。
    """

    def __init__(self):
        # **核心改动**: 从config文件中读取路径
        self.webdriver_path = WEBDRIVER_PATH

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service(executable_path=self.webdriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except WebDriverException as e:
            logging.error(
                f"无法初始化Selenium WebDriver。请确保 '{self.webdriver_path}' 路径正确且与您的Chrome浏览器版本匹配。错误: {e}")
            self.driver = None
        except Exception as e:
            logging.error(f"初始化WebDriver时发生未知错误: {e}")
            self.driver = None

    def extract_content(self, url: str) -> Tuple[bool, str]:
        """
        从URL提取网页的主要文本内容。
        """
        if not self.driver:
            return False, "WebDriver未初始化"
        if not url or not url.startswith(('http://', 'https://')):
            return False, "无效的URL"

        try:
            self.driver.get(url)
            time.sleep(3)

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form']):
                tag.decompose()

            article_body = soup.find('article') or soup.find('main') or soup.body
            if not article_body:
                return False, "无法定位内容区域"

            text = article_body.get_text(separator='\n', strip=True)
            lines = (line.strip() for line in text.splitlines())
            long_lines = [line for line in lines if len(line.split()) > 2]
            content = '\n'.join(long_lines)

            if not content:
                return False, "提取内容为空"

            logging.info(f"成功从 {url} 提取内容, 长度: {len(content)}")
            return True, content

        except Exception as e:
            logging.error(f"使用Selenium爬取 {url} 时发生错误: {e}")
            return False, f"爬取失败: {type(e).__name__}"

    def close(self):
        """关闭浏览器驱动。"""
        if self.driver:
            self.driver.quit()
