# **Web3深度新闻分析器 (Selenium版)**

这是一个功能强大的Web3新闻舆情分析工具，旨在帮助用户快速收集、分析并可视化来自多个主流搜索引擎的加密货币相关新闻。项目采用Selenium驱动真实浏览器进行深度内容抓取，有效解决了JavaScript动态加载网页的内容提取难题，并集成了基本的情绪分析和热词可视化功能。

## **✨ 功能特性**

* **多引擎聚合搜索**: 可同时选择并聚合来自Bing, Google, Baidu等多个搜索引擎的结果，信息来源更广泛。  
* **深度内容提取**: 采用Selenium框架，能够驱动真实的Chrome浏览器进行网页渲染，精准抓取由JavaScript动态加载的新闻正文，内容更完整。  
* **指定网址精准爬取**: 支持用户直接输入一个或多个新闻网址，进行点对点的精准内容提取和分析。  
* **自动化情绪分析**: 内置基于金融领域专业词典的情绪分析引擎，自动判断每篇新闻的“看多(Bullish)”、“看空(Bearish)”或“中性(Neutral)”倾向。  
* **金融热词可视化**:  
  * **词云图**: 聚合所有新闻内容，筛选出与金融交易最相关的热点词汇，并生成词云图，快速把握市场焦点。  
  * **情绪饼图**: 将情绪分析结果以饼图形式可视化，直观展示当前市场的整体舆论氛围。  
* **灵活的配置选项**: 用户可自由设定搜索数量、爬取数量、新闻时间范围等参数。  
* **大模型总结 (可选)**: 可配置API密钥，调用大语言模型对所有新闻内容进行深度总结和提炼。  
* **数据持久化**: 所有抓取和分析的结构化数据（包括新闻正文和情绪）将自动保存为CSV文件，方便二次分析。

## **🚀 快速开始**

### **环境准备**

在运行本项目前，请确保您的电脑已安装：

1. **Python 3.8 或更高版本**  
2. **Google Chrome 浏览器**

### **安装步骤**

1. 克隆或下载项目  
   将本项目代码下载到您的本地文件夹。  
2. 安装依赖库  
   打开终端或命令行，进入项目根目录，然后运行以下命令安装所有必需的Python库：  
   pip install \-r requirements.txt

3. **配置ChromeDriver**  
   * **检查Chrome版本**: 在Chrome浏览器地址栏输入 chrome://version 查看您的版本号 (例如: 127.0.6533.73)。  
   * **下载WebDriver**: 访问 [Chrome for Testing availability](https://googlechromelabs.github.io/chrome-for-testing/) 官方镜像站，找到与您浏览器版本**完全匹配**的 chromedriver，下载对应您操作系统的zip压缩包。  
   * **配置路径**: 解压下载的文件，得到 chromedriver.exe (Windows) 或 chromedriver (Mac/Linux)。然后打开项目中的 config.py 文件，将 WEBDRIVER\_PATH 的值修改为您刚刚解压的 chromedriver 文件的**完整绝对路径**。  
     \# Windows示例 (注意使用双反斜杠):  
     WEBDRIVER\_PATH \= "D:\\\\program\\\\web3\_news\_analyzer\\\\chromedriver.exe"

     \# macOS/Linux示例:  
     \# WEBDRIVER\_PATH \= "/Users/yourname/projects/web3\_news\_analyzer/chromedriver"

4. (可选) 配置大模型API  
   如果您希望使用AI总结功能，请打开 config.py 文件，填入您的API密钥和模型信息。  
   LLM\_CONFIG \= {  
       "api\_key": "YOUR\_API\_KEY\_HERE",  
       "base\_url": "YOUR\_API\_BASE\_URL\_HERE", \# 如果是本地模型  
       "model\_name": "your\_model\_name"  
   }

### **运行程序**

一切准备就绪后，在项目根目录的终端中运行以下命令：

python main.py

程序启动后，会显示一个本地网址 (通常是 http://127.0.0.1:7860)。在您的浏览器中打开该网址即可开始使用。

## **📖 使用指南**

本工具提供两种核心工作模式：

### **模式一: 搜索引擎聚合分析**

1. **选择搜索引擎**: 在“搜索引擎”多选框中，勾选一个或多个您希望使用的引擎。  
2. **设定参数**: 根据需要调整新闻时间范围、搜索数量和爬取数量。  
3. **输入关键词**: 在“输入自定义关键词”框中输入您关心的主题（例如：以太坊坎昆升级影响）。  
4. **启动分析**: 点击“启动分析”按钮。  
5. **快速分析**: 您也可以直接点击下方的预设币种按钮（如 BTC, ETH）进行一键分析。

### **模式二: 指定网址精准爬取**

1. **切换标签页**: 点击“模式二: 指定网址精准爬取”标签页。  
2. **输入网址**: 在文本框中输入一个或多个完整的新闻网址，每行一个。  
3. **开始爬取**: 点击“开始精准爬取”按钮。

程序运行期间，右侧的输出区域会实时显示任务状态、分析结果、数据表格和可视化图表。

## **📁 项目结构**

web3\_news\_analyzer/  
├── main.py               \# 主程序入口  
├── app\_ui.py             \# Gradio界面定义  
├── config.py             \# 配置文件 (API密钥, WebDriver路径等)  
├── requirements.txt      \# Python依赖库  
├── README.md             \# 项目说明文档  
├── .gitignore            \# Git忽略文件配置  
└── core/  
    ├── \_\_init\_\_.py  
    ├── selenium\_crawler.py \# 基于Selenium的深度爬虫  
    ├── search\_engine.py    \# 搜索引擎聚合模块  
    ├── llm\_service.py      \# 大语言模型服务  
    ├── data\_handler.py     \# CSV数据存储  
    ├── output\_formatter.py \# 输出格式化  
    └── analysis.py         \# 情绪分析与词云图生成  
