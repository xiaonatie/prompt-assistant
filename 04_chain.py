from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

# 1. 创建三个组件
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

prompt = ChatPromptTemplate.from_template(
    "列举{count}个{category}。\n{format_instructions}"
)

parser = CommaSeparatedListOutputParser()

# 2. 用 | 管道符串成链 —— 这就是 LangChain 的核心写法
chain = prompt | llm | parser

# 3. 一条命令，从输入到输出
result = chain.invoke({
    "count": "3",
    "category": "游戏王主角名字",
    "format_instructions": parser.get_format_instructions()
})

print("=== 链式调用结果 ===")
print(result)
print(type(result))