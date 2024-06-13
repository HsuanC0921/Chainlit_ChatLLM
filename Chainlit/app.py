# 匯入 os 模組，用於操作系統功能
import os
# 從 operator 模組匯入 itemgetter 函數，用於從字典或其他數據結構中取出特定元素
from operator import itemgetter
# 匯入 langchain_openai 中的 ChatOpenAI 類，用於與 OpenAI 的聊天模型進行互動
from langchain_openai import ChatOpenAI
# 匯入 langchain 中的 ChatPromptTemplate 和 MessagesPlaceholder 類，用於建立和管理聊天提示模板
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# 匯入 langchain 中的 StrOutputParser 類，用於解析模型的字串輸出
from langchain.schema.output_parser import StrOutputParser
# 匯入 Runnable 相關類，用於建立可執行的工作流
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
# 匯入 RunnableConfig 類，用於配置 Runnable 的行為
from langchain.schema.runnable.config import RunnableConfig
# 匯入 ConversationBufferMemory 類，用於在工作階段中維護對話記憶體
from langchain.memory import ConversationBufferMemory

# 匯入 chainlit 模組，用於構建對話式 AI 應用
import chainlit as cl
# 匯入 chainlit 中的 ThreadDict 類型，用於表示工作階段的執行緒
from chainlit.types import ThreadDict
# 匯入 chainlit 中的 Slider 類，用於創建滑動條輸入控件
from chainlit.input_widget import Slider
# 匯入 dotenv 模組，用於從 .env 檔案加載環境變數(各種api key)
from dotenv import load_dotenv

load_dotenv()  # 加載 .env 檔案中的環境變數
api_key = os.getenv("OPENAI_API_KEY")  # 從環境變數中獲取名為 "OPENAI_API_KEY" 的 API 金鑰

def setup_runnable(temperature, top_p, max_tokens): # 設定可執行的工作流，包括模型初始化、提示模板設定和工作流組合。
    # 從使用者工作階段中獲取名為 "memory" 的記憶體物件
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    # 建立 ChatOpenAI 物件，配置基本 URL、API 金鑰和模型名稱，並加入動態調整的參數
    model = ChatOpenAI(
        base_url="http://localhost:8000/v1",
        api_key=api_key,
        model="HsuanLLM/BreezeDolphin-SLERP-0.1",
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    # 建立聊天提示模板，包含系統提示、歷史消息占位符和使用者問題
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI assistant who answers questions in appropriate length sentences."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    # 建立 RunnablePassthrough 物件，並透過 RunnableLambda 和 itemgetter 獲取歷史記錄
    # 然後將其與提示模板、模型和輸出解析器組合成一個可執行的工作流
    runnable = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
        | StrOutputParser()
    )
    # 將建立的 runnable 物件儲存到使用者工作階段中
    cl.user_session.set("runnable", runnable)

@cl.password_auth_callback
def auth_callback(username: str, password: str): #使用者身份驗證回調函數，檢查用戶名和密碼是否匹配
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return cl.User(identifier="user")

@cl.on_chat_start
async def on_chat_start(): #當聊天開始時執行，初始化記憶體並設定 runnable
    cl.user_session.set("memory", ConversationBufferMemory(return_messages=True))
    # 初始化設定中的溫度、概率值和最大回應字數
    temperature = cl.user_session.get("temperature", 0.7) # 溫度值，溫度越高，生成的結果就越隨機、多樣，但也可能更不流暢、更奇怪
    top_p = cl.user_session.get("top_p", 0.9)  # Top P值，top p 值越高，生成的結果就越流暢、自然，但也可能更重複、更無聊
    max_tokens = cl.user_session.get("max_tokens", 2048) # 定義最大可產生的token數
    setup_runnable(temperature, top_p, max_tokens)

    # 使用 cl.ChatSettings 添加滑動條控件以動態調整 temperature、top_p 和 max_tokens
    settings = await cl.ChatSettings([
        Slider("Temperature", label="Temperature", initial=temperature, min=0.0, max=1.0, step=0.01, on_change=on_temperature_change),
        Slider("Top P", label="Top P", initial=top_p, min=0.0, max=1.0, step=0.01, on_change=on_top_p_change),
        Slider("Max Tokens", label="Max Tokens", initial=max_tokens, min=256, max=8192, step=1, on_change=on_max_tokens_change)
    ]).send()

    # 更新溫度、top_p 和 max_tokens 的值
    temperature = settings["Temperature"]
    top_p = settings["Top P"]
    max_tokens = settings["Max Tokens"]
    setup_runnable(temperature, top_p, max_tokens)

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    # 當聊天復原時執行，從執行緒中恢復消息並重新設定記憶體和 runnable。
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)
    temperature = cl.user_session.get("temperature", 0.7)
    top_p = cl.user_session.get("top_p", 0.9)
    max_tokens = cl.user_session.get("max_tokens", 2048)
    setup_runnable(temperature, top_p, max_tokens)

@cl.on_message
async def on_message(message: cl.Message):
    # 當收到使用者消息時執行，處理消息並將回應發送給使用者。
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory
    runnable = cl.user_session.get("runnable")  # type: Runnable

    response = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await response.stream_token(chunk)

    await response.send()

    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(response.content)

def on_temperature_change(value):
    # 當溫度滑動條的值改變時調用，更新模型的溫度設定。
    cl.user_session.set("temperature", value)
    setup_runnable(value, cl.user_session.get("top_p", 0.9))

def on_top_p_change(value):
    # 當 top_p 滑動條的值改變時調用，更新模型的 top_p 設定。
    cl.user_session.set("top_p", value)
    setup_runnable(cl.user_session.get("temperature", 0.7), value)


def on_max_tokens_change(value):
    # 當 max_tokens 滑動條的值改變時調用，更新模型的 max_tokens 設定。
    cl.user_session.set("max_tokens", value)
    setup_runnable(cl.user_session.get("max_tokens", 2048), value)
