# app_ui.py
import gradio as gr
import time
import pandas as pd
from typing import Generator, Any, List, Callable
from config import LLM_CONFIG, SUPPORTED_SEARCH_ENGINES, PRESET_COINS, FONT_PATH
from core.search_engine import get_search_engines
from core.selenium_crawler import SeleniumCrawler
from core.llm_service import LLMService
from core.data_handler import DataHandler
from core.output_formatter import format_summary_for_display, format_raw_data_for_display
from core.analysis import analyze_sentiment_simple, generate_word_cloud, create_sentiment_pie_chart

data_handler = DataHandler()


def search_and_crawl_flow(api_key: str, base_url: str, model_name: str, search_engine_names: List[str],
                          time_period: str, query: str, search_count: float, crawl_count: float,
                          is_direct_crawl: bool = False) -> Generator[Any, None, None]:
    yield from unified_task_processor(
        api_key=api_key, base_url=base_url, model_name=model_name,
        search_engine_names=search_engine_names, time_period=time_period, query=query,
        search_count=search_count, crawl_count=crawl_count, is_direct_crawl=is_direct_crawl,
        url_list=None
    )


def targeted_crawl_flow(api_key: str, base_url: str, model_name: str, url_list_str: str) -> Generator[Any, None, None]:
    urls = [url.strip() for url in url_list_str.splitlines() if url.strip()]
    if not urls:
        yield "错误：URL列表不能为空。", "无", format_raw_data_for_display([]), None, None, gr.Button(
            interactive=True), gr.Button(interactive=True), tuple(gr.Button(interactive=True) for _ in PRESET_COINS)
        return
    yield from unified_task_processor(
        api_key=api_key, base_url=base_url, model_name=model_name,
        crawl_count=len(urls), url_list=urls, query="Targeted Crawl"
    )


def unified_task_processor(**kwargs) -> Generator[Any, None, None]:
    status, summary = "正在启动任务...", "等待分析结果..."
    dataframe = format_raw_data_for_display([])
    pie_chart, word_cloud = None, None
    analyze_btn = gr.Button(interactive=False)
    targeted_btn = gr.Button(interactive=False)
    preset_btns = [gr.Button(interactive=False) for _ in PRESET_COINS]

    def yield_state(df_override: pd.DataFrame = None):
        display_df = df_override if df_override is not None else dataframe
        outputs = (status, summary, display_df, pie_chart, word_cloud, analyze_btn, targeted_btn) + tuple(preset_btns)
        return outputs

    crawler = SeleniumCrawler()
    if not crawler.driver:
        status = "错误: Selenium WebDriver未能启动。"
        summary = "请确保在 config.py 中设置的 'WEBDRIVER_PATH' 路径正确，且驱动版本与Chrome浏览器匹配。"
        analyze_btn = gr.Button(interactive=True)
        targeted_btn = gr.Button(interactive=True)
        preset_btns = [gr.Button(interactive=True) for _ in PRESET_COINS]
        yield yield_state()
        return

    yield yield_state()

    url_list = kwargs.get('url_list')
    if url_list:
        search_results = [type('obj', (object,), {'link': url, 'title': f'指定网址 {i + 1}', 'source': '用户指定'}) for
                          i, url in enumerate(url_list)]
    else:
        search_engine_names = kwargs.get('search_engine_names', [])
        if not search_engine_names:
            status = "错误：请至少选择一个搜索引擎。"
            analyze_btn = gr.Button(interactive=True);
            preset_btns = [gr.Button(interactive=True) for _ in PRESET_COINS]
            yield yield_state();
            crawler.close();
            return

        search_count = int(kwargs.get('search_count', 10))
        crawl_count = int(kwargs.get('crawl_count', 5))
        if crawl_count > search_count * len(search_engine_names):
            search_count = crawl_count // len(search_engine_names) + 1
            status = f"提示：为满足爬取数量，已自动将各引擎搜索数量调整为 {search_count}"
            yield yield_state();
            time.sleep(2)

        status = f"正在使用 {', '.join(search_engine_names)} 进行搜索..."
        yield yield_state()
        search_engines = get_search_engines(search_engine_names)
        all_search_results = []
        for engine in search_engines:
            all_search_results.extend(
                engine.search(kwargs.get('query'), time_period=kwargs.get('time_period'), max_results=search_count))

        unique_links = set()
        search_results = [res for res in all_search_results if
                          res.link not in unique_links and not unique_links.add(res.link)]
        if not search_results:
            status = "未能找到相关结果。"
            analyze_btn = gr.Button(interactive=True);
            preset_btns = [gr.Button(interactive=True) for _ in PRESET_COINS]
            yield yield_state();
            crawler.close();
            return

    dataframe = format_raw_data_for_display(search_results)
    status = "搜索完成，正在爬取网页..."
    yield yield_state()

    full_content, sentiments = "", []
    links_to_crawl = search_results[:int(kwargs.get('crawl_count', 5))]

    for i, result in enumerate(links_to_crawl):
        df_index = dataframe[dataframe['链接'] == result.link].index
        if df_index.empty: continue
        status = f"正在爬取第 {i + 1}/{len(links_to_crawl)} 个网页..."
        yield yield_state()
        success, content_or_error = crawler.extract_content(result.link)
        dataframe.loc[df_index, '爬取状态'] = "成功" if success else f"失败: {content_or_error}"
        if success:
            dataframe.loc[df_index, '爬取内容'] = content_or_error
            full_content += content_or_error + "\n"
            sentiment = analyze_sentiment_simple(content_or_error)
            sentiments.append(sentiment)
            dataframe.loc[df_index, '情绪'] = sentiment

        display_dataframe = dataframe.copy()
        display_dataframe['爬取内容'] = display_dataframe['爬取内容'].str.slice(0, 150) + '...'
        yield yield_state(df_override=display_dataframe)
        time.sleep(0.2)

    if full_content:
        status = "正在生成可视化图表..."
        yield yield_state()
        pie_chart = create_sentiment_pie_chart(sentiments)
        word_cloud = generate_word_cloud(full_content, FONT_PATH)
        yield yield_state()

    data_handler.save_to_csv(dataframe.to_dict('records'), kwargs.get('query', 'task'))
    status = "数据已保存，正在完成最后步骤..."
    yield yield_state()

    if not kwargs.get('url_list') and not kwargs.get('is_direct_crawl') and kwargs.get('api_key') and kwargs.get(
            'api_key') != "YOUR_API_KEY_HERE" and full_content:
        status = "正在调用大模型进行总结..."
        yield yield_state()
        llm_service = LLMService(kwargs.get('api_key'), kwargs.get('base_url') if kwargs.get('base_url') else None,
                                 kwargs.get('model_name'))
        summary = format_summary_for_display(llm_service.summarize_news(full_content, kwargs.get('query')),
                                             [res.link for res in links_to_crawl])
    else:
        summary = "已跳过大模型分析。"

    status = "任务完成！"
    analyze_btn = gr.Button(interactive=True)
    targeted_btn = gr.Button(interactive=True)
    preset_btns = [gr.Button(interactive=True) for _ in PRESET_COINS]
    yield yield_state()
    crawler.close()


def create_ui():
    ALL_ENGINES = ["Bing", "Google", "Baidu", "DuckDuckGo"]
    with gr.Blocks(theme=gr.themes.Soft(), title="Web3新闻分析器") as iface:
        gr.Markdown("# Web3深度新闻分析器 (Selenium版)")
        with gr.Accordion("API与模型配置", open=False):
            with gr.Row():
                api_key_input = gr.Textbox(label="大模型API密钥 (可选)", value=LLM_CONFIG["api_key"], type="password",
                                           scale=2)
                base_url_input = gr.Textbox(label="API Base URL (可选)", value=LLM_CONFIG["base_url"] or "", scale=2)
                model_name_input = gr.Textbox(label="模型名称", value=LLM_CONFIG["model_name"], scale=1)

        with gr.Row(equal_height=False):
            with gr.Column(scale=4):
                with gr.Tabs():
                    with gr.TabItem("模式一: 搜索引擎聚合分析"):
                        with gr.Group():
                            gr.Markdown("### 检索设置")
                            search_engine_input = gr.CheckboxGroup(label="搜索引擎 (可多选)", choices=ALL_ENGINES,
                                                                   value=[ALL_ENGINES[0]])
                            time_period_input = gr.Radio(label="新闻时间范围",
                                                         choices=["任何时间", "过去24小时", "过去一周", "过去一月"],
                                                         value="任何时间")
                            search_count_input = gr.Number(label="各引擎搜索数量", value=10, minimum=1, step=1)
                            crawl_count_input = gr.Number(label="总计爬取数量", value=5, minimum=1, step=1)
                        with gr.Group():
                            gr.Markdown("### 操作面板")
                            query_input = gr.Textbox(label="输入自定义关键词", placeholder="例如：比特币ETF进展")
                            analyze_button = gr.Button("启动分析", variant="primary")
                            gr.Markdown("#### 或点击预设币种进行快速分析")
                            preset_buttons: List[gr.Button] = [gr.Button(coin) for coin in PRESET_COINS]

                    with gr.TabItem("模式二: 指定网址精准爬取"):
                        with gr.Group():
                            gr.Markdown("### 输入网址队列")
                            url_list_input = gr.Textbox(label="输入新闻网址 (每行一个)", lines=10,
                                                        placeholder="https://www.coindesk.com/...\nhttps://cointelegraph.com/...")
                            targeted_crawl_button = gr.Button("开始精准爬取", variant="primary")

            with gr.Column(scale=6):
                with gr.Group():
                    status_output = gr.Label(label="任务状态")
                    summary_output = gr.Markdown(label="AI总结 (仅在搜索模式下生成)")
                raw_data_output = gr.DataFrame(label="新闻数据与情绪分析 (内容已截断显示)", interactive=False,
                                               wrap=True)
                with gr.Row():
                    with gr.Column(scale=4):
                        gr.Markdown("### 情绪分析")
                        sentiment_pie_chart = gr.Plot(label="看多/看空情绪分布")
                    with gr.Column(scale=6):
                        gr.Markdown("### 金融热词")
                        word_cloud_output = gr.Image(label="新闻词云图", interactive=False)

        common_outputs = [status_output, summary_output, raw_data_output, sentiment_pie_chart, word_cloud_output,
                          analyze_button, targeted_crawl_button, *preset_buttons]
        search_inputs = [api_key_input, base_url_input, model_name_input, search_engine_input, time_period_input,
                         query_input, search_count_input, crawl_count_input]
        analyze_button.click(fn=search_and_crawl_flow, inputs=search_inputs, outputs=common_outputs)

        def create_preset_handler(coin: str) -> Callable[..., Generator[Any, None, None]]:
            def handler(api_key, base_url, model_name, search_engines, time_period, search_count, crawl_count):
                yield from search_and_crawl_flow(
                    api_key=api_key, base_url=base_url, model_name=model_name,
                    search_engine_names=search_engines, time_period=time_period,
                    query=f"{coin} 最新新闻", search_count=search_count,
                    crawl_count=crawl_count, is_direct_crawl=True
                )

            return handler

        preset_inputs = [api_key_input, base_url_input, model_name_input, search_engine_input, time_period_input,
                         search_count_input, crawl_count_input]
        for i, coin_button in enumerate(preset_buttons):
            handler_fn = create_preset_handler(PRESET_COINS[i])
            coin_button.click(fn=handler_fn, inputs=preset_inputs, outputs=common_outputs)

        targeted_inputs = [api_key_input, base_url_input, model_name_input, url_list_input]
        targeted_crawl_button.click(fn=targeted_crawl_flow, inputs=targeted_inputs, outputs=common_outputs)

    return iface
