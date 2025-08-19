# core/analysis.py
import jieba
from wordcloud import WordCloud
import matplotlib

# Use a backend that doesn't require a GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from typing import List, Dict, Optional

# --- 情绪词典保持不变，以分析中文内容 ---
BULLISH_WORDS = [
    "上涨", "突破", "新高", "利好", "增长", "飙升", "看好", "乐观", "买入", "增持",
    "支持", "复苏", "强劲", "盈利", "牛市", "成功", "批准", "采用", "合作", "升级",
    "ATH", "新高", "减半", "halving", "bull run", "bullish", "pump", "long", "buy",
    "暴涨", "巨鲸", "抄底", "加仓", "持有", "生态", "赋能", "创新"
]
BEARISH_WORDS = [
    "下跌", "暴跌", "新低", "利空", "亏损", "看跌", "悲观", "卖出", "风险", "警告",
    "监管", "禁止", "打击", "熊市", "失败", "拒绝", "抛售", "担忧", "清算", "崩盘",
    "correction", "dip", "dump", "short", "sell", "bearish", "risk", "bubble", "泡沫",
    "回调", "恐慌", "砸盘", "出货", "割肉", "监管", "审查", "漏洞"
]

# --- 优化点: 大幅扩充英文金融交易词汇表 ---
FINANCIAL_VOCAB = set([
    # Major Coins & Tokens
    'btc', 'eth', 'sol', 'bnb', 'xrp', 'ada', 'doge', 'shib', 'dot', 'avax', 'link', 'matic',
    'bitcoin', 'ethereum', 'solana', 'cardano', 'polkadot', 'avalanche', 'chainlink', 'polygon',
    # Core Concepts
    'crypto', 'cryptocurrency', 'blockchain', 'web3', 'decentralized', 'smart contract', 'token',
    'defi', 'nft', 'metaverse', 'dao', 'dapp', 'wallet', 'tokenomics', 'staking', 'yield farming',
    'liquid staking', 'lending', 'borrowing', 'stablecoin', 'cbdc', 'privacy coin',
    # Trading & Market Terms
    'trading', 'exchange', 'market', 'price', 'volume', 'market cap', 'volatility', 'liquidity',
    'bull', 'bear', 'bullish', 'bearish', 'ath', 'atl', 'pump', 'dump', 'long', 'short', 'leverage',
    'futures', 'options', 'perpetual', 'spot', 'margin', 'spread', 'arbitrage', 'slippage',
    'resistance', 'support', 'trend', 'breakout', 'correction', 'dip', 'hodl', 'fomo', 'fud',
    'order book', 'limit order', 'market order', 'stop loss', 'take profit', 'whale', 'retail',
    # Technical Analysis
    'technical analysis', 'chart', 'candlestick', 'rsi', 'macd', 'moving average', 'bollinger bands',
    'fibonacci', 'indicator', 'signal',
    # Macro & Regulatory
    'investment', 'investor', 'fund', 'etf', 'sec', 'cftc', 'fed', 'federal reserve', 'interest rate',
    'inflation', 'recession', 'regulation', 'policy', 'adoption', 'partnership', 'security',
    # Chinese Equivalents (to catch bilingual articles)
    '加密货币', '区块链', '交易所', '交易', '价格', '市场', '波动', '市值', '交易量', '投资',
    '投资者', '基金', '期货', '合约', '杠杆', '做多', '做空', '流动性', '挖矿', '去中心化',
    '智能合约', '利率', '美联储', '监管', '通胀', '加息', '降息', '经济', '技术分析'
])


def analyze_sentiment_simple(text: str) -> str:
    if not isinstance(text, str): return "Neutral"
    score = 0
    text_lower = text.lower()
    for word in BULLISH_WORDS: score += text_lower.count(word.lower())
    for word in BEARISH_WORDS: score -= text_lower.count(word.lower())
    if score > 0: return "Bullish"
    if score < 0: return "Bearish"
    return "Neutral"


def generate_word_cloud(text: str, font_path: Optional[str] = None) -> Optional[np.ndarray]:
    if font_path and not os.path.exists(font_path):
        logging.warning(f"Font file not found: {font_path}. Using default font.")
        font_path = None

    try:
        # Use a simple split for English and jieba for Chinese context
        word_list = jieba.cut(text.lower(), cut_all=False)

        filtered_words = [
            word for word in word_list if word in FINANCIAL_VOCAB and len(word) > 1
        ]

        if not filtered_words:
            logging.warning("No relevant financial vocabulary found for word cloud.")
            return None

        text_segmented = " ".join(filtered_words)

        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            font_path=font_path,
            collocations=True,  # Allow common English phrases like "interest rate"
            prefer_horizontal=0.9
        ).generate(text_segmented)

        return wordcloud.to_array()
    except Exception as e:
        logging.error(f"Could not generate word cloud: {e}")
        return None


def create_sentiment_pie_chart(sentiments: List[str]) -> Optional[plt.Figure]:
    try:
        sentiment_counts: Dict[str, int] = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
        for s in sentiments:
            if s in sentiment_counts: sentiment_counts[s] += 1

        labels, sizes, colors = [], [], []

        if sentiment_counts["Bullish"] > 0:
            labels.append('Bullish');
            sizes.append(sentiment_counts["Bullish"]);
            colors.append('#4CAF50')
        if sentiment_counts["Bearish"] > 0:
            labels.append('Bearish');
            sizes.append(sentiment_counts["Bearish"]);
            colors.append('#F44336')
        if sentiment_counts["Neutral"] > 0:
            labels.append('Neutral');
            sizes.append(sentiment_counts["Neutral"]);
            colors.append('#9E9E9E')

        fig, ax = plt.subplots()
        if not sizes:
            ax.text(0.5, 0.5, 'No sentiment data available', ha='center', va='center')
            ax.axis('off')
        else:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
                   wedgeprops={'edgecolor': 'white', 'linewidth': 2})
            ax.axis('equal')

        return fig
    except Exception as e:
        logging.error(f"Could not create pie chart: {e}")
        return None
