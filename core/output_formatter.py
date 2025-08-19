# core/output_formatter.py
from .search_engine import SearchResult
import pandas as pd
from typing import List


def format_summary_for_display(summary: str, crawled_links: List[str]) -> str:
    if not summary: return "### AI分析总结\n\n未能生成总结。"
    header = "### AI分析总结\n\n"
    links_header = "\n\n---\n\n**参考来源:**\n"
    links_body = ""
    if crawled_links:
        for i, link in enumerate(crawled_links):
            links_body += f"{i + 1}. [{link}]({link})\n"
    else:
        links_body = "无有效参考来源。\n"
    return f"{header}{summary}{links_header}{links_body}"


def format_raw_data_for_display(search_results: List[SearchResult]) -> pd.DataFrame:
    """
    更新DataFrame结构，增加“序号”列。
    """
    headers = ["序号", "标题", "链接", "来源", "日期", "爬取状态", "爬取内容", "情绪"]
    if not search_results:
        return pd.DataFrame(columns=headers)

    data_for_df = [
        {
            "序号": i + 1,
            "标题": res.title, "链接": res.link, "来源": res.source,
            "日期": res.to_dict()['date'], "爬取状态": "待处理", "爬取内容": "", "情绪": "待分析"
        }
        for i, res in enumerate(search_results)
    ]
    return pd.DataFrame(data_for_df, columns=headers)
