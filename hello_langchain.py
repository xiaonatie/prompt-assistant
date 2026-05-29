from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

response = llm.invoke("用一句话介绍游戏王")
print(response.content)