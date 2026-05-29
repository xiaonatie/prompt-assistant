from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 创建输出解析器 —— 要求AI返回逗号分隔的列表
parser = CommaSeparatedListOutputParser()

# 3. 从解析器自动获取格式指令，塞进提示词里
format_instructions = parser.get_format_instructions()
print("=== 格式指令 ===")
print(format_instructions)

# 4. 创建模板，把格式指令也加进去
prompt = ChatPromptTemplate.from_template(
    "列举{count}个{category}。\n{format_instructions}"
)

# 5. 填入变量
filled_prompt = prompt.invoke({
    "count": "5",
    "category": "游戏王经典卡牌",
    "format_instructions": format_instructions
})

# 6. 调用模型
response = llm.invoke(filled_prompt)
print("\n=== AI 原始回复 ===")
print(type(response.content))
print(response.content)

# 7. 解析成列表
result = parser.invoke(response)
print("\n=== 解析后的结果 ===")
print(type(result))
print(result)