# core/search_engine.py
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

# --- SearchResult and SearchEngine classes remain the same ---
class SearchResult:
    def __init__(self, title: str, link: str, snippet: str, source: str, date: Optional[datetime] = None):
        self.title, self.link, self.snippet, self.source, self.date = title, link, snippet, source, date
    def to_dict(self) -> dict:
        return {"title": self.title, "link": self.link, "snippet": self.snippet, "source": self.source, "date": self.date.strftime('%Y-%m-%d') if self.date else "N/A"}

class SearchEngine(ABC):
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'})
    @abstractmethod
    def search(self, query: str, time_period: str = "any", max_results: int = 10) -> List[SearchResult]: pass

# --- Existing Bing and Google classes remain the same ---
class BingSearch(SearchEngine):
    TIME_FILTER_MAP = {"过去24小时": "d", "过去一周": "w", "过去一月": "m"}
    def __init__(self): super().__init__(source_name="Bing")
    def search(self, query: str, time_period: str = "任何时间", max_results: int = 10) -> List[SearchResult]:
        results: List[SearchResult] = []
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        if time_period in self.TIME_FILTER_MAP: url += f'&filters=ex1:"ez{self.TIME_FILTER_MAP[time_period]}"'
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for item in soup.find_all('li', class_='b_algo', limit=max_results):
                title_tag, link_tag = item.find('h2'), item.find('a')
                if title_tag and link_tag and link_tag.get('href'):
                    snippet_tag = item.find('div', class_='b_caption')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    results.append(SearchResult(title_tag.get_text(), link_tag['href'], snippet, self.source_name, datetime.now()))
        except requests.RequestException as e: logging.error(f"Bing search failed: {e}")
        return results

class GoogleSearch(SearchEngine):
    def __init__(self): super().__init__(source_name="Google")
    def search(self, query: str, time_period: str = "any", max_results: int = 10) -> List[SearchResult]:
        logging.warning("GoogleSearch is a placeholder.")
        return [SearchResult("[Sample] Google Result", "http://google.com", "This is a sample from Google.", self.source_name)]

# --- NEW: Baidu Search Engine Placeholder ---
class BaiduSearch(SearchEngine):
    def __init__(self):
        super().__init__(source_name="Baidu")

    def search(self, query: str, time_period: str = "any", max_results: int = 10) -> List[SearchResult]:
        logging.warning("BaiduSearch is a placeholder and requires specific scraping logic.")
        # Baidu has strong anti-scraping. A real implementation is complex.
        # Returning a sample result for demonstration.
        return [SearchResult(
            title="[示例] 来自百度的结果",
            link="http://baidu.com",
            snippet="这是一个来自百度的示例结果。",
            source=self.source_name
        )]

# --- NEW: DuckDuckGo Search Engine Placeholder (Popular in Europe/SEA for Privacy) ---
class DuckDuckGoSearch(SearchEngine):
    def __init__(self):
        super().__init__(source_name="DuckDuckGo")

    def search(self, query: str, time_period: str = "any", max_results: int = 10) -> List[SearchResult]:
        logging.warning("DuckDuckGoSearch is a placeholder and requires specific scraping logic.")
        return [SearchResult(
            title="[Sample] DuckDuckGo Result",
            link="http://duckduckgo.com",
            snippet="This is a sample result from DuckDuckGo.",
            source=self.source_name
        )]


def get_search_engines(names: List[str]) -> List[SearchEngine]:
    """Factory function to get search engine instances."""
    engines: List[SearchEngine] = []
    for name in names:
        name_lower = name.lower()
        if name_lower == 'bing': engines.append(BingSearch())
        elif name_lower == 'google': engines.append(GoogleSearch())
        elif name_lower == 'baidu': engines.append(BaiduSearch())
        elif name_lower == 'duckduckgo': engines.append(DuckDuckGoSearch())
        else: logging.warning(f"Unsupported search engine '{name}' skipped.")
    return engines
