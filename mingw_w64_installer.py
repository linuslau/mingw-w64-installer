import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import threading
import time
import os
import urllib.request

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("安装包")
        self.geometry("400x400")
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
        if page_name == "SplashPage":
            frame.start_download()

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
        self.status_label = tk.Label(self, textvariable=self.status_text)
        self.status_label.pack(pady=10)

    def start_download(self):
        self.status_text.set("Getting repository description file...")
        self.after(100, self.download_file)

    def download_file(self):
        def task():
            url = "https://sourceforge.net/projects/mingw-w64/files/Toolchains%20targetting%20Win32/Personal%20Builds/mingw-builds/installer/repository.txt/download"  # 假定的文件URL
            total_timeout = 6  # 总共最多尝试10秒
            timeout_per_try = 2  # 单次连接最多5秒
            attempts = 0
            start_time = time.time()

            while time.time() - start_time < total_timeout:
                try:
                    response = requests.get(url, timeout=timeout_per_try)
                    if response.status_code == 200:
                        with open("repository.txt", "wb") as file:
                            file.write(response.content)
                        self.status_text.set("文件下载成功！")
                        time.sleep(2)  # 保持一段时间显示
                        self.controller.show_frame("SelectOptionsPage")
                        return
                except requests.RequestException:
                    attempts += 1
                    self.status_text.set(f"尝试连接中...（尝试次数：{attempts}）")
            else:
                self.status_text.set("连接超时，继续下一步。")
                time.sleep(2)  # 保持一段时间显示
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

        self.repository_data = self.parse_repository_file()

        # 标签和下拉框
        ttk.Label(self, text="Version:").pack(pady=5, anchor='w')
        self.version_combobox = ttk.Combobox(self, state='readonly')
        self.version_combobox.pack(fill='x', padx=10)
        self.version_combobox.bind("<<ComboboxSelected>>", self.update_combobox_options)

        ttk.Label(self, text="Architecture:").pack(pady=5, anchor='w')
        self.architecture_combobox = ttk.Combobox(self, state='readonly')
        self.architecture_combobox.pack(fill='x', padx=10)
        self.architecture_combobox.bind("<<ComboboxSelected>>", self.update_combobox_options)

        ttk.Label(self, text="Threads:").pack(pady=5, anchor='w')
        self.threads_combobox = ttk.Combobox(self, state='readonly')
        self.threads_combobox.pack(fill='x', padx=10)
        self.threads_combobox.bind("<<ComboboxSelected>>", self.update_combobox_options)

        ttk.Label(self, text="Exception:").pack(pady=5, anchor='w')
        self.exception_combobox = ttk.Combobox(self, state='readonly')
        self.exception_combobox.pack(fill='x', padx=10)
        self.exception_combobox.bind("<<ComboboxSelected>>", self.update_combobox_options)

        ttk.Label(self, text="Build Revision:").pack(pady=5, anchor='w')
        self.build_revision_combobox = ttk.Combobox(self, state='readonly')
        self.build_revision_combobox.pack(fill='x', padx=10)
        self.build_revision_combobox.bind("<<ComboboxSelected>>", self.update_combobox_options)

        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", pady=10)

        cancel_button = tk.Button(button_frame, text="取消", command=controller.on_cancel)
        cancel_button.pack(side="right", padx=5)

        next_button = tk.Button(button_frame, text="下一步", command=self.download_file)
        next_button.pack(side="right", padx=5)

        back_button = tk.Button(button_frame, text="上一步", command=lambda: controller.show_frame("WelcomePage"))
        back_button.pack(side="right", padx=5)

        # 初始加载
        self.version_combobox['values'] = sorted(set([entry[0] for entry in self.repository_data]))
        self.version_combobox.current(0)
        self.update_combobox_options(None)

    def parse_repository_file(self):
        repository_file = 'repository.txt'
        data = []

        if os.path.exists(repository_file):
            with open(repository_file, 'r') as file:
                for line in file:
                    if line.strip():
                        data.append(line.strip().split('|'))

        return data

    def update_combobox_options(self, event):
        version = self.version_combobox.get()
        architecture = self.architecture_combobox.get()
        threads = self.threads_combobox.get()
        exception = self.exception_combobox.get()
        build_revision = self.build_revision_combobox.get()

        filtered_data = [entry for entry in self.repository_data if entry[0] == version]
        architectures = sorted(set([entry[1].strip() for entry in filtered_data]))
        if architecture not in architectures:
            self.architecture_combobox.set('')
        self.architecture_combobox['values'] = architectures

        filtered_data = [entry for entry in self.repository_data if entry[0] == version and entry[1].strip() == architecture]
        thread_options = sorted(set([entry[2].strip() for entry in filtered_data]))
        if threads not in thread_options:
            self.threads_combobox.set('')
        self.threads_combobox['values'] = thread_options

        filtered_data = [entry for entry in self.repository_data if entry[0] == version and entry[1].strip() == architecture and entry[2].strip() == threads]
        exception_options = sorted(set([entry[3].strip() for entry in filtered_data]))
        if exception not in exception_options:
            self.exception_combobox.set('')
        self.exception_combobox['values'] = exception_options

        filtered_data = [entry for entry in self.repository_data if entry[0] == version and entry[1].strip() == architecture and entry[2].strip() == threads and entry[3].strip() == exception]
        build_revision_options = sorted(set([entry[4].strip() for entry in filtered_data]))
        if build_revision not in build_revision_options:
            self.build_revision_combobox.set('')
        self.build_revision_combobox['values'] = build_revision_options

    def download_file(self):
        version = self.version_combobox.get()
        architecture = self.architecture_combobox.get()
        threads = self.threads_combobox.get()
        exception = self.exception_combobox.get()
        build_revision = self.build_revision_combobox.get()

        # 找到匹配的URL
        for entry in self.repository_data:
            if (entry[0] == version and entry[1].strip() == architecture and
                entry[2].strip() == threads and entry[3].strip() == exception and
                entry[4].strip() == build_revision):
                url = entry[5]
                break
        else:
            messagebox.showerror("Error", "No matching entry found.")
            return

        # 下载文件
        local_filename = url.split('/')[-1]
        try:
            urllib.request.urlretrieve(url, local_filename)
            messagebox.showinfo("Success", f"Downloaded {local_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {str(e)}")


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
