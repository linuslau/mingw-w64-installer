import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("安装包")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.frames = {}
        for F in (WelcomePage, SplashPage, SelectOptionsPage, InstallDirPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_cancel(self):
        if messagebox.askyesno("取消", "你确定要取消安装吗？"):
            self.destroy()

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="欢迎使用安装向导", font=("Arial", 14))
        label.pack(pady=10)

        description = tk.Label(self, text="此向导将引导您完成安装过程。\n请点击'下一步'继续。")
        description.pack(pady=10)

        # 示例图片
        self.photo = tk.PhotoImage(file="your_image_path.png")  # 替换为你的图片路径
        image_label = tk.Label(self, image=self.photo)
        image_label.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        cancel_button = tk.Button(button_frame, text="取消", command=controller.on_cancel)
        cancel_button.pack(side="right", padx=5)

        next_button = tk.Button(button_frame, text="下一步", command=lambda: controller.show_frame("SplashPage"))
        next_button.pack(side="right", padx=5)

class SplashPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="获取存储库描述文件...", font=("Arial", 14))
        label.pack(pady=20)

        self.status_text = tk.StringVar()
        self.status_text.set("Getting repository description file...")
        status_label = tk.Label(self, textvariable=self.status_text)
        status_label.pack(pady=10)

        self.after(100, self.download_file)

    def download_file(self):
        def task():
            try:
                response = requests.get("https://example.com/repository_description.txt", timeout=5)
                if response.status_code == 200:
                    self.status_text.set("文件下载成功！")
                else:
                    self.status_text.set("文件下载失败，继续下一步。")
            except requests.RequestException:
                self.status_text.set("连接超时，继续下一步。")
            finally:
                self.controller.show_frame("SelectOptionsPage")

        threading.Thread(target=task).start()

class SelectOptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="选择选项", font=("Arial", 14))
        label.pack(pady=10)

        description = tk.Label(self, text="请选择以下选项：")
        description.pack(pady=10)

        self.options = []
        for i in range(5):
            option_frame = tk.Frame(self)
            option_frame.pack(pady=5, padx=10, fill="x")
            label = tk.Label(option_frame, text=f"选项 {i+1}:")
            label.pack(side="left")
            combo = ttk.Combobox(option_frame, values=[f"选项 {i+1} - 值 {j+1}" for j in range(5)])
            combo.pack(side="right", fill="x", expand=True)
            self.options.append(combo)

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        cancel_button = tk.Button(button_frame, text="取消", command=controller.on_cancel)
        cancel_button.pack(side="right", padx=5)

        next_button = tk.Button(button_frame, text="下一步", command=lambda: controller.show_frame("InstallDirPage"))
        next_button.pack(side="right", padx=5)

        back_button = tk.Button(button_frame, text="上一步", command=lambda: controller.show_frame("WelcomePage"))
        back_button.pack(side="right", padx=5)

class InstallDirPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="选择安装目录", font=("Arial", 14))
        label.pack(pady=10)

        description = tk.Label(self, text="请选择安装目录：")
        description.pack(pady=10)

        self.install_dir = tk.StringVar()
        entry = tk.Entry(self, textvariable=self.install_dir, width=50)
        entry.pack(pady=5)

        browse_button = tk.Button(self, text="浏览...", command=self.browse_directory)
        browse_button.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        cancel_button = tk.Button(button_frame, text="取消", command=controller.on_cancel)
        cancel_button.pack(side="right", padx=5)

        next_button = tk.Button(button_frame, text="下一步", command=self.install)
        next_button.pack(side="right", padx=5)

        back_button = tk.Button(button_frame, text="上一步", command=lambda: controller.show_frame("SelectOptionsPage"))
        back_button.pack(side="right", padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.install_dir.set(directory)

    def install(self):
        if self.install_dir.get():
            messagebox.showinfo("安装", "安装已完成！")
        else:
            messagebox.showwarning("警告", "请选择安装目录！")

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
