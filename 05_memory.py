from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 手动维护对话历史
history = []

# 第一轮对话
history.append(HumanMessage(content="我叫张麒鹏，我是游戏王玩家"))

response1 = llm.invoke(history)
print("=== 第一轮 ===")
print(response1.content)

# 把AI的回复也存进历史
history.append(AIMessage(content=response1.content))

# 第二轮对话
history.append(HumanMessage(content="我叫什么名字？我喜欢什么？"))

response2 = llm.invoke(history)
print("\n=== 第二轮 ===")
print(response2.content)

# 3. 看看完整的对话历史
print("\n=== 完整对话历史 ===")
for msg in history:
    role = "人类" if isinstance(msg, HumanMessage) else "AI"
    print(f"[{role}] {msg.content[:50]}...")