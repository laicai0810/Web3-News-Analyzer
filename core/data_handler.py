# core/data_handler.py
import pandas as pd
import logging
import os
from datetime import datetime
from typing import List, Dict


class DataHandler:
    """处理数据存储，例如将结果保存到CSV文件。"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
        except OSError as e:
            logging.error(f"创建输出目录 {self.output_dir} 失败: {e}")

    def save_to_csv(self, data: List[Dict], query: str) -> None:
        """将数据安全地保存到CSV文件。"""
        if not data:
            logging.warning("无数据可保存。")
            return

        try:
            df = pd.DataFrame(data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 清理查询词作为文件名，避免非法字符
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{safe_query}_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)

            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logging.info(f"数据成功保存到 {filepath}")
        except Exception as e:
            logging.error(f"保存数据到CSV失败: {e}")
