"""提示词助手 - 桌面悬浮工具"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os, sys, re, threading, pyperclip
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, "prompt_templates.json")
load_dotenv(os.path.join(APP_DIR, ".env"))

DEFAULT_TEMPLATES = {
    "深度分析报告": "你是一位资深{领域}分析师。请对以下主题进行深度分析：\n【分析主题】{主题}\n\n请按以下结构输出：\n1. 背景概述（100字内）\n2. 核心论点（3-5条，每条一句话+一段展开）\n3. 数据/证据支撑（如有）\n4. 反方观点及回应\n5. 结论与建议（可操作的具体建议，不要空话）\n6. 潜在风险提示\n\n语气：专业但不学术，让{受众}也能看懂",
    "代码Review": "请对以下{语言}代码进行Code Review：\n\n{代码}\n\n请从以下维度逐一评价（每项1-5分）：\n- 可读性\n- 健壮性\n- 性能\n- 安全性\n- 可维护性\n\n对每个维度说明扣分原因，最后给出修改建议的代码",
    "文案爆款拆解": "请拆解以下爆款文案的底层逻辑：\n\n{文案内容}\n\n请分析：\n1. 钩子设计\n2. 情绪曲线\n3. 痛点映射\n4. 结构公式\n5. 可复用模板：提取出通用模板，填入{行业}、{产品}、{痛点}就能生成同结构文案",
    "学习路线规划": "我想学习{技能}，当前水平：{当前水平}，目标：{目标水平}，可用时间：每天{时间}。\n\n请制定学习路线：\n1. 按周划分阶段\n2. 每个阶段推荐1-2个核心学习资源\n3. 标注容易放弃的瓶颈点及应对方法\n4. 每周的自测检查点",
    "会议纪要整理": "请将以下会议内容整理为结构化纪要：\n\n{会议内容}\n\n格式：\n【会议主题】\n【参会人员】\n【核心决议】（用表格）\n【遗留问题】（标注优先级）\n【下一步行动】",
    "竞品分析": "请对比分析以下产品：\n产品A：{产品A}\n产品B：{产品B}\n\n对比维度：\n1. 核心功能差异（表格对比）\n2. 目标用户画像差异\n3. 定价策略差异\n4. 各自最大优势与致命短板\n5. 如果我是{角色}，应该选哪个？",
    "Bug排查助手": "我遇到了一个bug：\n【技术栈】{技术栈}\n【期望行为】{期望}\n【实际行为】{实际}\n【错误信息】{报错内容}\n【相关代码】{代码}\n\n请按步骤分析：\n1. 最可能的原因（置信度1-10）\n2. 其他可能原因\n3. 排查方法\n4. 修复代码\n5. 验证方法",
}

def load_templates():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    save_templates(DEFAULT_TEMPLATES)
    return DEFAULT_TEMPLATES.copy()

def save_templates(templates):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

class AIRecommender:

    def __init__(self):
        self.llm = None
        self.history = []

    def _get_llm(self):
        if self.llm is None:
            self.llm = ChatOpenAI(model="Qwen/Qwen3-8B", base_url="https://api.siliconflow.cn/v1", api_key=os.getenv("SILICONFLOW_API_KEY"))
        return self.llm

    def recommend(self, user_need, templates):
        tl = "\n".join([f"- {n}：{c}" for n, c in templates.items()])
        self.history = [("system", f"你是提示词助手。现有模板：\n{tl}\n\n请推荐最合适的模板。格式：\n推荐模板：【名称】\n推荐理由：【理由】\n无匹配时：\n推荐模板：【无匹配】\n建议模板：【新名称】\n模板内容：【新内容，用{{变量}}标记】\n\n用户可追问，根据追问调整。"), ("human", user_need)]
        return self._chat()

    def follow_up(self, question):
        self.history.append(("human", question))
        return self._chat()

    def _chat(self):
        msgs = []
        for role, content in self.history:
            if role == "system": msgs.append(SystemMessage(content=content))
            elif role == "human": msgs.append(HumanMessage(content=content))
            elif role == "ai": msgs.append(AIMessage(content=content))
        resp = self._get_llm().invoke(msgs)
        self.history.append(("ai", resp.content))
        return resp.content

class PromptAssistant:
    def __init__(self):
        self.templates = load_templates()
        self.ai = AIRecommender()
        self._ai_running = False
        self.root = tk.Tk()
        self.root.title("提示词助手")
        self.root.geometry("320x520")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#2b2b2b")

        title_frame = tk.Frame(self.root, bg="#3c3f41", height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="提示词助手", bg="#3c3f41", fg="white", font=("Microsoft YaHei", 12, "bold")).pack(side=tk.LEFT, padx=10, pady=8)
        btn_frame = tk.Frame(title_frame, bg="#3c3f41")
        btn_frame.pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="AI", command=self.ai_recommend, bg="#6c5ce7", fg="white", font=("Microsoft YaHei", 10), relief=tk.FLAT, padx=6, cursor="hand2").pack(side=tk.RIGHT, padx=(4, 0))
        tk.Button(btn_frame, text="+", command=self.add_template, bg="#4a9eff", fg="white", font=("Microsoft YaHei", 10, "bold"), relief=tk.FLAT, padx=8, cursor="hand2").pack(side=tk.RIGHT)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var, bg="#3c3f41", fg="white", insertbackground="white", font=("Microsoft YaHei", 10), relief=tk.FLAT)
        self.search_entry.pack(fill=tk.X, padx=10, pady=(8, 4), ipady=4)
        self.search_entry.insert(0, "搜索...")
        self.search_entry.bind("<FocusIn>", self._search_focus_in)
        self.search_entry.bind("<FocusOut>", self._search_focus_out)

        scroll_container = tk.Frame(self.root, bg="#2b2b2b")
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        self.canvas = tk.Canvas(scroll_container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg="#2b2b2b")
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.search_var.trace_add("write", self.filter_list)
        self.render_list()

        self.status = tk.Label(self.root, text=f"共 {len(self.templates)} 个模板 | 点击复制 | AI推荐", bg="#2b2b2b", fg="#888888", font=("Microsoft YaHei", 8))
        self.status.pack(side=tk.BOTTOM, pady=5)
                # 首次启动检查API Key
        if not os.getenv("SILICONFLOW_API_KEY"):
            self.root.after(100, self.show_api_key_setup)
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _search_focus_in(self, e):
        if self.search_entry.get() == "搜索...":
            self.search_entry.delete(0, tk.END)

    def _search_focus_out(self, e):
        if not self.search_entry.get():
            self.search_entry.insert(0, "搜索...")

    def render_list(self, filter_text=""):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        for name, content in self.templates.items():
            if filter_text and filter_text.lower() not in name.lower():
                continue
            card = tk.Frame(self.list_frame, bg="#3c3f41", cursor="hand2")
            card.pack(fill=tk.X, pady=2)
            preview = content.split("\n")[0][:30]
            name_label = tk.Label(card, text=name, bg="#3c3f41", fg="white", font=("Microsoft YaHei", 10, "bold"), anchor="w")
            name_label.pack(fill=tk.X, padx=8, pady=(6, 0), anchor="w")
            preview_label = tk.Label(card, text=preview, bg="#3c3f41", fg="#999999", font=("Microsoft YaHei", 8), anchor="w")
            preview_label.pack(fill=tk.X, padx=8, pady=(0, 4), anchor="w")
            def on_right_click(event, tname=name):
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="编辑", command=lambda: self.edit_template(tname))
                menu.add_command(label="删除", command=lambda: self.delete_template(tname))
                menu.post(event.x_root, event.y_root)
            for w in [card, name_label, preview_label]:
                w.bind("<Button-1>", lambda e, c=content: self.copy_prompt(c))
                w.bind("<Button-3>", on_right_click)
                w.configure(cursor="hand2")

    def filter_list(self, *args):
        text = self.search_var.get()
        if text == "搜索...": text = ""
        self.render_list(text)

    def copy_prompt(self, content):
        pyperclip.copy(content)
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        tip.geometry(f"+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 200}")
        tk.Label(tip, text="已复制到剪贴板", bg="#4a9eff", fg="white", font=("Microsoft YaHei", 10), padx=10, pady=5).pack()
        tip.after(1500, tip.destroy)

    def add_template(self):
        name = simpledialog.askstring("添加模板", "模板名称：", parent=self.root)
        if not name: return
        if name in self.templates:
            messagebox.showwarning("提示", "该名称已存在")
            return
        content = self.open_editor("", f"编辑 {name}")
        if content:
            self.templates[name] = content
            save_templates(self.templates)
            self.render_list()

    def edit_template(self, name):
        content = self.open_editor(self.templates[name], f"编辑 {name}")
        if content is not None:
            self.templates[name] = content
            save_templates(self.templates)
            self.render_list()

    def delete_template(self, name):
        if messagebox.askyesno("确认", f"删除 {name}？"):
            del self.templates[name]
            save_templates(self.templates)
            self.render_list()

    def open_editor(self, initial_text, title):
        editor = tk.Toplevel(self.root)
        editor.title(title)
        editor.geometry("500x350")
        editor.attributes("-topmost", True)
        editor.configure(bg="#2b2b2b")
        text = tk.Text(editor, bg="#3c3f41", fg="white", insertbackground="white", font=("Microsoft YaHei", 10), wrap=tk.WORD, relief=tk.FLAT)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        text.insert("1.0", initial_text)
        result = [None]
        def save():
            result[0] = text.get("1.0", tk.END).strip()
            editor.destroy()
        tk.Button(editor, text="保存", command=save, bg="#4a9eff", fg="white", font=("Microsoft YaHei", 10), relief=tk.FLAT, padx=20, cursor="hand2").pack(pady=10)
        editor.grab_set()
        self.root.wait_window(editor)
        return result[0]

    def ai_recommend(self):
        if self._ai_running: return
        dialog = tk.Toplevel(self.root)
        dialog.title("AI 推荐模板")
        dialog.geometry("400x200")
        dialog.attributes("-topmost", True)
        dialog.configure(bg="#2b2b2b")
        tk.Label(dialog, text="描述你要做什么，AI帮你找模板：", bg="#2b2b2b", fg="white", font=("Microsoft YaHei", 10)).pack(pady=(15, 5))
        entry = tk.Text(dialog, bg="#3c3f41", fg="white", insertbackground="white", font=("Microsoft YaHei", 10), wrap=tk.WORD, relief=tk.FLAT, height=4)
        entry.pack(fill=tk.X, padx=15, pady=5)
        result = [None]
        def submit():
            result[0] = entry.get("1.0", tk.END).strip()
            dialog.destroy()
        tk.Button(dialog, text="推荐", command=submit, bg="#6c5ce7", fg="white", font=("Microsoft YaHei", 10), relief=tk.FLAT, padx=20, cursor="hand2").pack(pady=10)
        dialog.grab_set()
        self.root.wait_window(dialog)
        if not result[0]: return

        self._ai_running = True
        loading_win = tk.Toplevel(self.root)
        loading_win.title("加载中")
        loading_win.geometry("300x100")
        loading_win.attributes("-topmost", True)
        loading_win.configure(bg="#2b2b2b")
        loading_win.resizable(False, False)
        tk.Label(loading_win, text="AI 正在思考，请稍候...", bg="#2b2b2b", fg="white", font=("Microsoft YaHei", 10)).pack(pady=(15, 5))
        progress = ttk.Progressbar(loading_win, mode='indeterminate', length=250)
        progress.pack(pady=5)
        progress.start(15)
        self.root.update()

        def do_recommend():
            try:
                ai_response = self.ai.recommend(result[0], self.templates)
                name_match = re.search(r'建议模板：【(.+?)】', ai_response)
                content_match = re.search(r'模板内容：【(.+?)】', ai_response, re.DOTALL)
                if name_match and content_match:
                    self.templates[name_match.group(1)] = content_match.group(1)
                    save_templates(self.templates)
                    self.root.after(0, self.render_list)
                self.root.after(0, lambda: loading_win.destroy())
                self.root.after(0, lambda: self.show_ai_result(ai_response))
            except Exception as e:
                err_msg = str(e)
                if "401" in err_msg or "api_key" in err_msg.lower() or "authentication" in err_msg.lower():
                    friendly = "API Key 无效或已过期，请点击右上角 AI 按钮重新配置。"
                elif "429" in err_msg:
                    friendly = "API 调用次数已达上限，请稍后再试或更换 Key。"
                elif "timeout" in err_msg.lower() or "connection" in err_msg.lower():
                    friendly = "网络连接失败，请检查网络后重试。"
                else:
                    friendly = f"AI推荐失败：{err_msg}"
                self.root.after(0, lambda: loading_win.destroy())
                self.root.after(0, lambda: messagebox.showerror("错误", friendly))                
                self.root.after(0, lambda: loading_win.destroy())
                self.root.after(0, lambda: messagebox.showerror("错误", f"AI推荐失败：{e}"))
            finally:
                self.root.after(0, lambda: self.status.config(text=f"共 {len(self.templates)} 个模板 | 点击复制 | AI推荐"))
                self._ai_running = False
        threading.Thread(target=do_recommend, daemon=True).start()

    def show_ai_result(self, response):
        win = tk.Toplevel(self.root)
        win.title("AI 推荐")
        win.geometry("550x600")
        win.attributes("-topmost", True)
        win.configure(bg="#2b2b2b")
        tk.Label(win, text="AI 推荐结果", bg="#2b2b2b", fg="white", font=("Microsoft YaHei", 12, "bold")).pack(pady=(10, 5))

        chat_text = tk.Text(win, bg="#3c3f41", fg="white", insertbackground="white", font=("Microsoft YaHei", 10), wrap=tk.WORD, relief=tk.FLAT)
        chat_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        chat_text.insert("1.0", response)
        chat_text.config(state=tk.DISABLED)

        input_frame = tk.Frame(win, bg="#2b2b2b")
        input_frame.pack(fill=tk.X, padx=15, pady=(5, 5))
        follow_entry = tk.Entry(input_frame, bg="#3c3f41", fg="white", insertbackground="white", font=("Microsoft YaHei", 10), relief=tk.FLAT)
        follow_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=4, padx=(0, 5))
        follow_entry.insert(0, "输入追问...")
        def on_focus_in(e):
            if follow_entry.get() == "输入追问...": follow_entry.delete(0, tk.END)
        follow_entry.bind("<FocusIn>", on_focus_in)

        def do_follow_up():
            question = follow_entry.get().strip()
            if not question or question == "输入追问...": return
            follow_entry.delete(0, tk.END)
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"\n\n{'='*30}\n[你的追问] {question}\n{'='*30}\n")
            chat_text.config(state=tk.DISABLED)
            self.status.config(text="AI 正在思考...")
            def do_follow():
                try:
                    ai_reply = self.ai.follow_up(question)
                    def update():
                        chat_text.config(state=tk.NORMAL)
                        chat_text.insert(tk.END, f"\n[AI 回复] {ai_reply}")
                        chat_text.config(state=tk.DISABLED)
                        chat_text.see(tk.END)
                        self.status.config(text=f"共 {len(self.templates)} 个模板 | 点击复制 | AI推荐")
                    self.root.after(0, update)
                except Exception as e:
                    err_msg = str(e)
                    if "401" in err_msg or "api_key" in err_msg.lower():
                        friendly = "API Key 无效或已过期，请重新配置。"
                    elif "429" in err_msg:
                        friendly = "API 调用次数已达上限，请稍后再试。"
                    elif "timeout" in err_msg.lower() or "connection" in err_msg.lower():
                        friendly = "网络连接失败，请检查网络后重试。"
                    else:
                        friendly = err_msg
                    def show_err():
                        chat_text.config(state=tk.NORMAL)
                        chat_text.insert(tk.END, f"\n[错误] {friendly}")
                        chat_text.config(state=tk.DISABLED)
                        self.status.config(text=f"共 {len(self.templates)} 个模板 | 点击复制 | AI推荐")
                    self.root.after(0, show_err)                    
                    def show_err():
                        chat_text.config(state=tk.NORMAL)
                        chat_text.insert(tk.END, f"\n[错误] {e}")
                        chat_text.config(state=tk.DISABLED)
                        self.status.config(text=f"共 {len(self.templates)} 个模板 | 点击复制 | AI推荐")
                    self.root.after(0, show_err)
            threading.Thread(target=do_follow, daemon=True).start()

        follow_entry.bind("<Return>", lambda e: do_follow_up())
        tk.Button(input_frame, text="追问", command=do_follow_up, bg="#6c5ce7", fg="white", font=("Microsoft YaHei", 9), relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.RIGHT)

        btn_frame = tk.Frame(win, bg="#2b2b2b")
        btn_frame.pack(pady=10)
        def copy_result():
            chat_text.config(state=tk.NORMAL)
            pyperclip.copy(chat_text.get("1.0", tk.END).strip())
            chat_text.config(state=tk.DISABLED)
        def save_as_template():
            chat_text.config(state=tk.NORMAL)
            all_text = chat_text.get("1.0", tk.END).strip()
            chat_text.config(state=tk.DISABLED)
            name = simpledialog.askstring("保存模板", "模板名称：", parent=win)
            if name:
                self.templates[name] = all_text
                save_templates(self.templates)
                self.render_list()
                win.destroy()
        tk.Button(btn_frame, text="复制全部", command=copy_result, bg="#4a9eff", fg="white", font=("Microsoft YaHei", 9), relief=tk.FLAT, padx=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="存为新模板", command=save_as_template, bg="#6c5ce7", fg="white", font=("Microsoft YaHei", 9), relief=tk.FLAT, padx=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="关闭", command=win.destroy, bg="#555555", fg="white", font=("Microsoft YaHei", 9), relief=tk.FLAT, padx=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
    def show_api_key_setup(self):
        setup_win = tk.Toplevel(self.root)
        setup_win.title("首次配置")
        setup_win.geometry("400x200")
        setup_win.attributes("-topmost", True)
        setup_win.configure(bg="#2b2b2b")
        setup_win.grab_set()

        tk.Label(setup_win, text="欢迎使用提示词助手！", bg="#2b2b2b", fg="white",
                font=("Microsoft YaHei", 12, "bold")).pack(pady=(15, 5))
        tk.Label(setup_win, text="请输入硅基流动 API Key（没有可跳过，AI推荐功能暂不可用）", bg="#2b2b2b", fg="#999999",
                font=("Microsoft YaHei", 9)).pack(pady=(0, 10))

        entry = tk.Entry(setup_win, bg="#3c3f41", fg="white", insertbackground="white",
                        font=("Microsoft YaHei", 10), relief=tk.FLAT, width=40)
        entry.pack(ipady=4, padx=20)

        def save_key():
            key = entry.get().strip()
            if key:
                with open(os.path.join(APP_DIR, ".env"), "w", encoding="utf-8") as f:
                    f.write(f"SILICONFLOW_API_KEY={key}")
                os.environ["SILICONFLOW_API_KEY"] = key
                self.ai = AIRecommender()
            setup_win.destroy()

        btn_frame = tk.Frame(setup_win, bg="#2b2b2b")
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="保存", command=save_key,
                 bg="#4a9eff", fg="white", font=("Microsoft YaHei", 9),
                 relief=tk.FLAT, padx=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="跳过", command=setup_win.destroy,
                 bg="#555555", fg="white", font=("Microsoft YaHei", 9),
                 relief=tk.FLAT, padx=15, cursor="hand2").pack(side=tk.LEFT, padx=5)
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PromptAssistant()
    app.run()