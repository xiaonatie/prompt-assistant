from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 创建提示词模板 —— 用 {变量名} 占位
prompt = ChatPromptTemplate.from_template(
    "你是一个{role}。请用{style}的风格，解释{concept}这个概念。"
)

# 3. 填入变量，生成完整的提示词
filled_prompt = prompt.invoke({
    "role": "游戏王资深玩家",
    "style": "中二热血",
    "concept": "同调召唤"
})

print("=== 生成的提示词 ===")
print(filled_prompt)

# 4. 把提示词丢给模型
response = llm.invoke(filled_prompt)
print("\n=== AI 回复 ===")
print(response.content)