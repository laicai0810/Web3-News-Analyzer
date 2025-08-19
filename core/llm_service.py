# core/llm_service.py
import openai
import logging
from typing import Optional

class LLMService:
    """封装与大语言模型交互的服务。"""
    def __init__(self, api_key: str, base_url: Optional[str] = None, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.client: Optional[openai.OpenAI] = None
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            logging.warning("LLMService: API key is missing or a placeholder.")
            return
        try:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            logging.info(f"LLMService initialized for model '{model_name}'")
        except Exception as e:
            logging.error(f"Failed to initialize OpenAI client: {e}")

    def summarize_news(self, content: str, query: str) -> str:
        """使用LLM分析和总结新闻内容。"""
        if not self.client: return "错误：LLM客户端未正确初始化（请检查API Key）。"
        if not content: return "错误：输入内容为空，无法进行总结。"

        # 截断过长内容以避免超出token限制
        max_content_length = 15000
        if len(content) > max_content_length:
            content = content[:max_content_length]

        system_prompt = "你是一个专业的Web3行业分析师。你的任务是基于提供的网络搜索结果，为用户提供一个关于特定主题的、简洁、中立、有条理的新闻总结。"
        user_prompt = f"""
        请根据以下关于“{query}”的搜索内容，总结最近的主要新闻动态。
        要求:
        1. 总结必须客观中立，只陈述事实。
        2. 内容清晰，重点突出，分为几个要点。
        3. 如果内容不足以形成有意义的总结，请指出信息不足。
        搜索内容：
        ---
        {content}
        ---
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2, max_tokens=1024,
            )
            summary = response.choices[0].message.content
            return summary.strip() if summary else "总结为空。"
        except openai.APIError as e:
            logging.error(f"OpenAI API Error: {e}")
            return f"错误：API返回错误 - {e}"
        except Exception as e:
            logging.error(f"An unexpected error occurred during LLM call: {e}")
            return f"错误：调用LLM时发生未知错误。"
