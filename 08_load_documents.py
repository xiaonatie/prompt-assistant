from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import os

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 先创建一个示例文本文件
knowledge_dir = r"C:\Users\张麒鹏\OneDrive\桌面\langchain-learning\knowledge"
os.makedirs(knowledge_dir, exist_ok=True)

sample_text = """青眼白龙：8星 光属性 龙族 ATK/3000 DEF/2500。海马濑人的招牌怪兽，游戏王OCG中攻击力最高的通常怪兽之一。
黑魔导：7星 暗属性 魔法师族 ATK/2500 DEF/2100。武藤游戏的招牌怪兽，游戏王系列最具代表性的魔法师族怪兽。
星尘龙：8星 风属性 龙族 ATK/2500 DEF/2000。不动游星的招牌怪兽，拥有破坏抗性效果。
沉默魔术师：4星 光属性 魔法师族 ATK/1000 DEF/1000。每回合攻击力上升500，是强力的成长型怪兽。
火焰翼人：6星 炎属性 战士族 ATK/2100 DEF/1200。游城十代的招牌怪兽之一，融合怪兽。"""

with open(os.path.join(knowledge_dir, "cards.txt"), "w", encoding="utf-8") as f:
    f.write(sample_text)

# 3. 从文件加载文档（核心！）
loader = TextLoader(os.path.join(knowledge_dir, "cards.txt"), encoding="utf-8")
docs = loader.load()

print(f"=== 加载了 {len(docs)} 个文档 ===")
print(f"总字符数：{len(docs[0].page_content)}")

# 4. 文本切块（长文档需要切成小段）
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,      # 每块最大100字符
    chunk_overlap=20     # 块之间重叠20字符，避免切断语义
)
chunks = splitter.split_documents(docs)

print(f"\n=== 切成 {len(chunks)} 块 ===")
for i, chunk in enumerate(chunks):
    print(f"块{i}: {chunk.page_content[:60]}...")

# 5. 存入向量库
vectorstore = FAISS.from_documents(chunks, embeddings)

# 6. 问答测试
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
question = "十代的招牌怪兽是什么？"
related_docs = retriever.invoke(question)

context = "\n".join([doc.page_content for doc in related_docs])

prompt = ChatPromptTemplate.from_template(
    "根据以下资料回答问题。如果资料中没有相关信息，请说'我不知道'。\n\n"
    "资料：\n{context}\n\n"
    "问题：{question}"
)

chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"context": context, "question": question})

print(f"\n=== 问题 ===")
print(question)
print(f"\n=== AI 回答 ===")
print(answer)