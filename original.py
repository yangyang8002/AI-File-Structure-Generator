import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import re
import requests
import json
from datetime import datetime

class FileStructureGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("文件结构生成器 - DeepSeek API集成")
        self.root.geometry("900x700")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        
        # DeepSeek API 部分
        ttk.Label(self.main_frame, text="DeepSeek API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar()
        self.api_entry = ttk.Entry(self.main_frame, textvariable=self.api_key_var, width=50)
        self.api_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 模型选择
        ttk.Label(self.main_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="deepseek-chat")
        model_combo = ttk.Combobox(self.main_frame, textvariable=self.model_var, width=20)
        model_combo['values'] = ('deepseek-chat', 'deepseek-coder')
        model_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 自然语言描述输入
        ttk.Label(self.main_frame, text="自然语言描述:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.desc_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=10)
        self.desc_text.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 分析按钮
        ttk.Button(self.main_frame, text="分析结构", command=self.analyze_structure).grid(row=3, column=1, sticky=tk.E, pady=5)
        
        # 文件结构显示
        ttk.Label(self.main_frame, text="生成的文件结构:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.structure_text = scrolledtext.ScrolledText(self.main_frame, width=60, height=15)
        self.structure_text.grid(row=4, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 生成按钮
        ttk.Button(self.main_frame, text="生成文件结构", command=self.generate_files).grid(row=5, column=1, sticky=tk.E, pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 插入默认示例
        self.insert_example()
    
    def insert_example(self):
        example = """创建一个Python项目，包含以下内容：
- 主程序文件main.py，包含一个简单的Flask应用
- 工具模块utils.py，包含一些辅助函数
- 测试目录tests，包含测试文件test_main.py和test_utils.py
- 配置文件config.json，包含API密钥和其他设置
- 依赖文件requirements.txt，列出项目依赖
- README.md文件，说明项目用途和使用方法"""
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, example)
    
    def call_deepseek_api(self, prompt):
        """调用DeepSeek API分析文件结构"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            raise ValueError("请提供DeepSeek API密钥")
        
        model = self.model_var.get()
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 精心设计的提示词，用于解析文件结构
        system_prompt = """你是一个文件结构分析专家。请根据用户的自然语言描述，生成对应的文件结构。
输出格式要求：
1. 每行表示一个文件或目录
2. 目录以斜杠(/)结尾
3. 使用缩进表示层级关系（每级4个空格）
4. 不要包含任何注释或额外解释
5. 确保文件扩展名正确

示例输出：
project/
    src/
        main.py
        utils.py
    tests/
        test_main.py
        test_utils.py
    config.json
    requirements.txt
    README.md

请严格按照上述格式输出，不要添加任何额外内容。"""
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        self.status_var.set("正在调用DeepSeek API...")
        self.root.update()
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return content.strip()
            else:
                raise Exception("API响应格式不正确")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API调用失败: {str(e)}")
    
    def analyze_structure(self):
        """分析用户输入的自然语言描述"""
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not description:
            messagebox.showerror("错误", "请输入文件结构描述")
            return
        
        try:
            # 调用DeepSeek API分析结构
            structure = self.call_deepseek_api(description)
            
            # 显示生成的文件结构
            self.structure_text.delete(1.0, tk.END)
            self.structure_text.insert(1.0, structure)
            
            self.status_var.set("分析完成!")
            
        except Exception as e:
            messagebox.showerror("错误", f"分析文件结构时出错: {str(e)}")
            self.status_var.set("分析失败")
    
    def parse_structure(self, text):
        """解析文件结构文本"""
        lines = text.split('\n')
        structure = {}
        current_path = []
        
        for line in lines:
            # 忽略空行和注释
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # 计算缩进级别
            indent = len(line) - len(line.lstrip())
            level = indent // 4  # 假设每级缩进为4个空格
            
            # 调整当前路径
            current_path = current_path[:level]
            item_name = line.strip()
            
            # 如果是目录（以/结尾）
            if item_name.endswith('/'):
                dir_name = item_name[:-1]
                current_path.append(dir_name)
                full_path = os.path.join(*current_path)
                structure[full_path] = {'type': 'dir'}
            else:
                # 是文件
                full_path = os.path.join(*current_path, item_name)
                structure[full_path] = {'type': 'file'}
        
        return structure
    
    def generate_files(self):
        """生成文件结构"""
        structure_text = self.structure_text.get(1.0, tk.END)
        
        if not structure_text.strip():
            messagebox.showerror("错误", "请先分析文件结构")
            return
        
        try:
            structure = self.parse_structure(structure_text)
            
            # 创建目录和文件
            for path, info in structure.items():
                if info['type'] == 'dir':
                    os.makedirs(path, exist_ok=True)
                    self.status_var.set(f"创建目录: {path}")
                    self.root.update()
                else:
                    # 创建文件
                    dir_name = os.path.dirname(path)
                    if dir_name and not os.path.exists(dir_name):
                        os.makedirs(dir_name, exist_ok=True)
                    
                    # 根据文件类型生成内容
                    content = self.generate_file_content(path)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.status_var.set(f"创建文件: {path}")
                    self.root.update()
            
            self.status_var.set("文件结构生成完成!")
            messagebox.showinfo("成功", "文件结构已成功生成!")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成文件结构时出错: {str(e)}")
            self.status_var.set("生成失败")
    
    def generate_file_content(self, file_path):
        """根据文件路径生成文件内容"""
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        # 根据文件类型生成不同的内容
        if ext == '.py':
            return self.generate_python_content(filename)
        elif ext == '.json':
            return self.generate_json_content(filename)
        elif filename.lower() == 'readme.md':
            return self.generate_readme_content(file_path)
        elif ext == '.txt':
            return self.generate_text_content(filename)
        elif ext == '.html':
            return self.generate_html_content(filename)
        elif ext == '.css':
            return self.generate_css_content(filename)
        elif ext == '.js':
            return self.generate_js_content(filename)
        else:
            return f"# {filename}\n# 生成时间: {self.get_current_time()}"
    
    def generate_python_content(self, filename):
        return f'''# {filename}
# 生成时间: {self.get_current_time()}

def main():
    """主函数"""
    print("Hello from {filename}")

if __name__ == "__main__":
    main()
'''
    
    def generate_json_content(self, filename):
        return f'''{{
    "name": "{filename}",
    "generated_at": "{self.get_current_time()}"
}}'''
    
    def generate_readme_content(self, file_path):
        dir_name = os.path.dirname(file_path)
        project_name = dir_name if dir_name else "项目"
        return f'''# {project_name}

## 概述
这是一个自动生成的项目。

## 使用说明
1. 安装依赖: `pip install -r requirements.txt`
2. 运行主程序: `python main.py`

## 生成信息
- 生成时间: {self.get_current_time()}
- 使用工具: 文件结构生成器
'''
    
    def generate_text_content(self, filename):
        return f'''{filename}
生成时间: {self.get_current_time()}

依赖列表:
requests>=2.25.0
'''
    
    def generate_html_content(self, filename):
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{filename}</title>
</head>
<body>
    <h1>{filename}</h1>
    <p>生成时间: {self.get_current_time()}</p>
</body>
</html>'''
    
    def generate_css_content(self, filename):
        return f'''/* {filename} */
/* 生成时间: {self.get_current_time()} */

body {{
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
}}'''
    
    def generate_js_content(self, filename):
        return f'''// {filename}
// 生成时间: {self.get_current_time()}

function main() {{
    console.log("Hello from {filename}");
}}

// 启动应用
main();'''
    
    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileStructureGenerator(root)
    root.mainloop()