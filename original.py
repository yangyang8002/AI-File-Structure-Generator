import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Tuple


# ------------------------------------------------------------------
# 核心解析 & 构建
# ------------------------------------------------------------------
def parse_structure(text: str) -> List[str]:
    """
    解析树形文本，返回“相对路径”列表（文件夹去掉末尾 /）。
    忽略空行、# 注释与行尾注释。
    """
    paths = []

    # 记录前缀长度 → 目录栈
    # (indent_len, folder_name)
    stack: List[Tuple[int, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.split('#', 1)[0].rstrip()
        if not line.strip():
            continue

        # 计算缩进长度（只统计空格或树形符号）
        stripped = line.lstrip('├─└│─ ')
        indent = len(line) - len(stripped)

        name = stripped.strip()
        if not name:
            continue

        # 找到当前应该归属的父目录
        while stack and stack[-1][0] >= indent:
            stack.pop()

        parent = ''
        if stack:
            parent = stack[-1][1]

        # 组装完整相对路径
        full_path = os.path.join(parent, name.rstrip('/'))

        paths.append(full_path)

        # 如果是目录，压栈
        if name.endswith('/'):
            stack.append((indent, full_path))

    return paths


def build_structure(structure_text: str, root_path: str) -> None:
    """根据解析结果在 root_path 里创建文件夹和空文件。"""
    paths = parse_structure(structure_text)

    try:
        for path in paths:
            abs_path = os.path.join(root_path, path)
            if path.endswith('/'):           # 目录
                os.makedirs(abs_path, exist_ok=True)
            else:                            # 文件
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                if not os.path.exists(abs_path):
                    open(abs_path, 'w', encoding='utf-8').close()
    except OSError as e:
        raise RuntimeError(str(e))


# ------------------------------------------------------------------
# Tkinter UI（与之前相同）
# ------------------------------------------------------------------
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("目录结构生成器")
        self.geometry("620x500")
        self.resizable(False, False)

        # 选择路径
        self.path_var = tk.StringVar(value=os.getcwd())
        path_frame = ttk.Frame(self)
        path_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(path_frame, text="目标路径：").pack(side='left')
        ttk.Entry(path_frame, textvariable=self.path_var, state='readonly', width=55).pack(side='left', padx=5)
        ttk.Button(path_frame, text="浏览…", command=self.choose_dir).pack(side='left')

        # 文本框
        ttk.Label(self, text="请在下框粘贴或输入树形结构：").pack(anchor='w', padx=10)
        self.text = tk.Text(self, height=22)
        self.text.pack(fill='both', padx=10, pady=5, expand=True)

        # 示例按钮
        ttk.Button(self, text="载入示例", command=self.load_example).pack(pady=2)

        # 生成按钮
        ttk.Button(self, text="生成目录与文件", command=self.generate).pack(pady=5)

    def choose_dir(self):
        selected = filedialog.askdirectory()
        if selected:
            self.path_var.set(selected)

    def load_example(self):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", EXAMPLE.strip())

    def generate(self):
        structure = self.text.get("1.0", tk.END)
        root = self.path_var.get().strip()
        if not root:
            messagebox.showwarning("警告", "请先选择或输入目标路径！")
            return
        if not structure.strip():
            messagebox.showwarning("警告", "请输入目录结构！")
            return

        try:
            build_structure(structure, root)
            messagebox.showinfo("成功", "目录与文件已生成！")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败：\n{e}")


# ------------------------------------------------------------------
# 示例结构
# ------------------------------------------------------------------
EXAMPLE = """
/domain-distributor/
├── index.php
├── auth/
│   ├── login.php
│   ├── register.php
│   ├── github-login.php
│   └── verify-email.php
├── dashboard.php
├── admin/
│   ├── index.php
│   ├── users.php
│   ├── domains.php
│   └── settings.php
├── includes/
│   ├── config.php
│   ├── db.php
│   ├── functions.php
│   ├── captcha.php
│   └── auth.php
├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── mail/
│   └── sendmail.php
├── api/
│   └── cloudflare.php
└── .env
"""

if __name__ == "__main__":
    app = Application()
    app.mainloop()
