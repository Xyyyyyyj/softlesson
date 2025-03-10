import tkinter as tk
from tkinter import ttk, scrolledtext
import random
import threading  # 用于创建线程
import queue  # 用于队列，多个线程之间通信
from concurrent.futures import ThreadPoolExecutor  # 多线程池
import pandas as pd  # 用于数据处理和存储
import time
from PIL import Image, ImageTk  # 用于处理图片,本来打算修改图片润色gui界面的
import tkinter.messagebox  # 用于创建消息提示框

# 全局变量
step_count = 0
distance = 0.0
calories = 0.0
start_time = time.time()
is_running = True  # 控制数据生成状态的全局变量

# 运动评级阈值
HEART_RATE_THRESHOLD = {'low': 60, 'high': 100}  # 心率阈值
BREATH_RATE_THRESHOLD = {'low': 12, 'high': 20}  # 呼吸频率阈值

USER_INFO_FILE = "user_info.txt"

# 注册函数
def register():
    def register_action():
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm_password.get()

        if not username or not password or not confirm_password:
            tkinter.messagebox.showerror("错误", "用户名和密码不能为空")
            return

        if password != confirm_password:
            tkinter.messagebox.showerror("错误", "两次输入的密码不一致")
            return

        # 检查用户是否已经存在
        try:
            with open(USER_INFO_FILE, "r") as f:
                lines = f.readlines()
                for line in lines:
                    stored_username, _ = line.strip().split(":")
                    if stored_username == username:
                        tkinter.messagebox.showerror("错误", "该用户名已被注册")
                        return
        except FileNotFoundError:
            pass

        # 保存用户信息
        with open(USER_INFO_FILE, "a") as f:
            f.write(f"{username}:{password}\n")

        tkinter.messagebox.showinfo("成功", "注册成功，请登录")
        register_window.destroy()

    register_window = tk.Toplevel()
    register_window.title("注册")

    # 使用 grid 布局
    label_username = tk.Label(register_window, text="用户名:")
    label_username.grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(register_window)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    label_password = tk.Label(register_window, text="密码:")
    label_password.grid(row=1, column=0, padx=10, pady=5)
    entry_password = tk.Entry(register_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    label_confirm_password = tk.Label(register_window, text="确认密码:")
    label_confirm_password.grid(row=2, column=0, padx=10, pady=5)
    entry_confirm_password = tk.Entry(register_window, show="*")
    entry_confirm_password.grid(row=2, column=1, padx=10, pady=5)

    button_register = tk.Button(register_window, text="注册", command=register_action)
    button_register.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# 登录函数
def login():
    def login_action():
        username = entry_username.get()
        password = entry_password.get()

        if not username or not password:
            tkinter.messagebox.showerror("错误", "用户名和密码不能为空")
            return

        # 检查用户信息
        try:
            with open(USER_INFO_FILE, "r") as f:
                lines = f.readlines()
                for line in lines:
                    stored_username, stored_password = line.strip().split(":")
                    if stored_username == username and stored_password == password:
                        tkinter.messagebox.showinfo("成功", "登录成功")
                        login_window.destroy()
                        main_screen()
                        return
            tkinter.messagebox.showerror("错误", "用户名或密码错误")
        except FileNotFoundError:
            tkinter.messagebox.showerror("错误", "用户信息文件不存在，请先注册")

    login_window = tk.Toplevel()
    login_window.title("登录")

    # 使用 grid 布局
    label_username = tk.Label(login_window, text="用户名:")
    label_username.grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    label_password = tk.Label(login_window, text="密码:")
    label_password.grid(row=1, column=0, padx=10, pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5)

    button_login = tk.Button(login_window, text="登录", command=login_action)
    button_login.grid(row=2, column=0, padx=10, pady=10)

    button_register = tk.Button(login_window, text="注册", command=register)
    button_register.grid(row=2, column=1, padx=10, pady=10)

# 欢迎界面
def welcome_screen():
    root = tk.Tk()
    root.title("欢迎界面")

    button_login = tk.Button(root, text="登录", command=login)
    button_login.pack(pady=20)

    root.mainloop()

# 主界面
def main_screen():
    global step_count, distance, calories, start_time, is_running

    main_window = tk.Toplevel()
    main_window.title("智能健身衣 - 主界面")
    main_window.geometry("1200x800")  # 调整窗口大小以适应多个实时数据窗口

    # 线程选择
    thread_label = ttk.Label(main_window, text="选择线程数量:")
    thread_label.grid(row=0, column=0, columnspan=2, pady=5)
    thread_var = tk.IntVar()
    thread_combobox = ttk.Combobox(main_window, textvariable=thread_var, values=list(range(1, 11)))
    thread_combobox.current(0)  # 默认选择第一个选项
    thread_combobox.grid(row=1, column=0, columnspan=2, pady=5)

    def create_data_frame(frame, user_id):
        labels = ['心率', '呼吸率', '体温', '血压', '步数', '运动距离', '消耗的卡路里', '运动时长', '运动评级']
        entries = {}

        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            entries[label] = ttk.Label(frame, text="0")
            entries[label].grid(row=i, column=1, padx=5, pady=2)

        def update_data():
            global step_count, distance, calories, start_time, is_running
            if is_running:
                # 本次新增的步数
                new_steps = random.randint(1, 3)
                step_count += new_steps
                # 严格保证一步对应 0.8 米
                distance += new_steps * 0.8
                calories += new_steps * 0.05  # 假设每步消耗0.05卡路里
                elapsed_time = time.time() - start_time

                # 生成随机数据
                heart_rate = random.randint(80, 120)
                breath_rate = random.randint(15, 25)
                body_temp = random.uniform(36.5, 37.5)
                systolic_pressure = random.randint(110, 130)
                diastolic_pressure = random.randint(70, 80)
                blood_pressure = f"{systolic_pressure}/{diastolic_pressure}"

                # 更新实时数据
                entries['心率'].config(text=str(heart_rate))
                entries['呼吸率'].config(text=str(breath_rate))
                entries['体温'].config(text=f"{body_temp:.1f}°C")
                entries['血压'].config(text=blood_pressure)
                entries['步数'].config(text=str(step_count))
                entries['运动距离'].config(text=f"{distance:.2f} 米")
                entries['消耗的卡路里'].config(text=f"{calories:.2f} 卡")
                entries['运动时长'].config(text=f"{int(elapsed_time // 60)} 分 {int(elapsed_time % 60)} 秒")

                # 运动评级
                if heart_rate > HEART_RATE_THRESHOLD['high'] and breath_rate > BREATH_RATE_THRESHOLD['high']:
                    rating = "运动剧烈"
                elif heart_rate < HEART_RATE_THRESHOLD['low'] and breath_rate < BREATH_RATE_THRESHOLD['low']:
                    rating = "运动过缓"
                else:
                    rating = "运动适中"
                entries['运动评级'].config(text=rating)

            # 每隔1秒更新一次
            main_window.after(1000, update_data)

        update_data()
        return frame

    def on_thread_change(event):
        thread_count = thread_var.get()
        for widget in main_window.grid_slaves():
            if isinstance(widget, ttk.LabelFrame):
                widget.grid_forget()  # 移除旧的实时数据窗口

        for i in range(thread_count):
            frame = ttk.LabelFrame(main_window, text=f"用户{i+1}实时数据")
            frame.grid(row=2, column=i, padx=10, pady=10, sticky='nsew')
            create_data_frame(frame, i)

    thread_combobox.bind("<<ComboboxSelected>>", on_thread_change)
    on_thread_change(None)  # 初始化显示

    def toggle_running():
        global is_running
        is_running = not is_running
        if is_running:
            stop_button.config(text="停止")
        else:
            stop_button.config(text="继续")

    # 操作按钮
    frame_buttons = ttk.Frame(main_window)
    frame_buttons.grid(row=4, column=0, columnspan=10, padx=10, pady=10, sticky='we')

    log_button = ttk.Button(frame_buttons, text="生成工作日志", command=lambda: log_screen(thread_var.get()))
    log_button.grid(row=0, column=0, padx=5, pady=5)

    stop_button = ttk.Button(frame_buttons, text="停止", command=toggle_running)
    stop_button.grid(row=0, column=1, padx=5, pady=5)

    back_button = ttk.Button(frame_buttons, text="返回欢迎界面", command=lambda: [main_window.destroy(), welcome_screen()])
    back_button.grid(row=0, column=2, padx=5, pady=5)

    exit_button = ttk.Button(frame_buttons, text="退出", command=lambda: [main_window.destroy(), exit_screen()])
    exit_button.grid(row=0, column=3, padx=5, pady=5)

# 工作日志界面
def log_screen(thread_count):
    global is_running
    log_window = tk.Toplevel()
    log_window.title("智能健身衣 - 工作日志")
    log_window.geometry("600x400")

    log_text = scrolledtext.ScrolledText(log_window, width=40, height=10)
    log_text.pack(padx=5, pady=5, fill='both', expand=True)

    # 创建线程池
    executor = ThreadPoolExecutor(max_workers=thread_count)

    import csv
    # 打开 CSV 文件以追加模式写入
    csv_file = open("work_log.csv", mode="a", newline='')
    csv_writer = csv.writer(csv_file)
    # 如果文件是空的，写入标题行
    import os
    if os.path.getsize("work_log.csv") == 0:
        csv_writer.writerow(["心率", "呼吸率", "体温", "血压"])

    def generate_log_data():
        while True:
            if is_running:
                # 生成随机数据
                heart_rate = random.randint(80, 120)
                breath_rate = random.randint(15, 25)
                body_temp = random.uniform(36.5, 37.5)
                systolic_pressure = random.randint(110, 130)
                diastolic_pressure = random.randint(70, 80)
                blood_pressure = f"{systolic_pressure}/{diastolic_pressure}"

                # 插入数据到日志
                log_text.insert(tk.END, f"心率: {heart_rate}, 呼吸率: {breath_rate}, 体温: {body_temp:.1f}°C, 血压: {blood_pressure}\n")
                log_text.see(tk.END)

                # 将数据写入 CSV 文件
                csv_writer.writerow([heart_rate, breath_rate, body_temp, blood_pressure])
                csv_file.flush()  # 确保数据立即写入文件

            # 每隔1秒生成一次数据
            time.sleep(1)

    # 提交任务到线程池
    for _ in range(thread_count):
        executor.submit(generate_log_data)

    # 操作按钮
    frame_buttons = ttk.Frame(log_window)
    frame_buttons.pack(padx=10, pady=(0, 10))

# 退出界面
def exit_screen():
    exit_window = tk.Toplevel()
    exit_window.title("感谢使用")
    exit_window.geometry("300x200")

    label = ttk.Label(exit_window, text="感谢您的使用，开启下一段健身之旅", font=("Arial", 12))
    label.pack(pady=50)

    exit_button = ttk.Button(exit_window, text="退出", command=exit_window.quit)
    exit_button.pack(pady=10)

# 启动欢迎界面
welcome_screen()

# 运行主循环
tk.mainloop()