# 提示词助手

一个轻量级的 AI 提示词管理桌面工具，支持模板管理、一键复制、AI 智能推荐。

## 功能

- 📋 模板管理：内置 7 个专业提示词模板，支持增删改
- 📎 一键复制：点击模板直接复制到剪贴板
- 🤖 AI 推荐：描述需求，AI 自动推荐或生成模板
- 💬 追问对话：对 AI 推荐结果不满意可继续追问
- 🔍 搜索过滤：快速找到需要的模板
- 🎯 首次配置：首次启动引导填写 API Key

## 安装

### 方式一：直接运行（需要 Python 环境）

1. 克隆仓库
```bash
git clone https://github.com/你的用户名/prompt-assistant.git
cd prompt-assistant
2. 安装依赖
pip install -r requirements.txt
3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的硅基流动 API Key  
4. 运行程序
python prompt_assistant.py
方式二：安装包（无需 Python）
下载 Releases 中的安装包，双击安装即可。首次启动会引导配置 API Key。
获取 API Key
1. 注册 硅基流动
2. 进入控制台 → API Key 管理 → 创建新 Key
3. 首次启动程序时填入即可
技术栈  技能
Python 3.14
Tkinter（GUI）  特金特
LangChain（AI 调用）
硅基流动 API（Qwen3-8B 模型）
