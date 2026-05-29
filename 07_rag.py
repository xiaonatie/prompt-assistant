from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 创建 Embedding 模型（把文字转成向量）
embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 3. 准备知识库文档
docs = [
    Document(page_content="青眼白龙：8星 光属性 龙族 ATK/3000 DEF/2500。海马濑人的招牌怪兽，游戏王OCG中攻击力最高的通常怪兽之一。"),
    Document(page_content="黑魔导：7星 暗属性 魔法师族 ATK/2500 DEF/2100。武藤游戏的招牌怪兽，是游戏王系列最具代表性的魔法师族怪兽。"),
    Document(page_content="星尘龙：8星 风属性 龙族 ATK/2500 DEF/2000。不动游星的招牌怪兽，拥有破坏抗性效果。"),
    Document(page_content="沉默魔术师：4星 光属性 魔法师族 ATK/1000 DEF/1000。每回合攻击力上升500，是强力的成长型怪兽。"),
]

# 4. 把文档转成向量，存入 FAISS 向量数据库
vectorstore = FAISS.from_documents(docs, embeddings)

# 5. 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 6. 用户提问
question = "游星的招牌怪兽是什么？"

# 7. 检索相关文档
related_docs = retriever.invoke(question)
print("=== 检索到的相关文档 ===")
for doc in related_docs:
    print(f"- {doc.page_content}")

# 8. 把检索到的文档拼成上下文，让 AI 回答
context = "\n".join([doc.page_content for doc in related_docs])

prompt = ChatPromptTemplate.from_template(
    "根据以下资料回答问题。如果资料中没有相关信息，请说'我不知道'。\n\n"
    "资料：\n{context}\n\n"
    "问题：{question}"
)

chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"context": context, "question": question})

print("\n=== AI 回答 ===")
print(answer)