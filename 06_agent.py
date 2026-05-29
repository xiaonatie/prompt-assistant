from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent as create_react_agent

# 1. 创建模型
llm = ChatOpenAI(
    model="Qwen/Qwen3-8B",
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-uthsoqitkjgdmqnnravkpckuksytplkxlyotbarbznlsjucu"
)

# 2. 自定义工具
@tool
def get_card_info(card_name: str) -> str:
    """查询游戏王卡牌信息。参数：card_name 卡牌名称"""
    card_db = {
        "青眼白龙": "8星 光属性 龙族 ATK/3000 DEF/2500，海马濑人的招牌怪兽",
        "黑魔导": "7星 暗属性 魔法师族 ATK/2500 DEF/2100，武藤游戏的招牌怪兽",
        "沉默魔术师": "4星 光属性 魔法师族 ATK/1000 DEF/1000",
    }
    return card_db.get(card_name, f"未找到卡牌：{card_name}")

# 3. 用 langgraph 创建 Agent（新版推荐写法）
agent = create_react_agent(llm, [get_card_info])

# 4. 测试
result = agent.invoke({"messages": "青眼白龙的攻击力是多少？"})

print("=== 完整执行过程 ===")
for msg in result["messages"]:
    print(f"[{msg.__class__.__name__}] {msg.content[:100] if msg.content else '(空)'}")
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"  → 调用工具: {tc['name']}({tc['args']})")

print("\n=== 最终回答 ===")
final_msg = result["messages"][-1]
print(final_msg.content)