import random
import numpy as np
import threading
import time

# 定义合理阈值
HEART_RATE_RANGE = (60, 200)  # 心跳频率 (bpm)
RESPIRATORY_RATE_RANGE = (40, 80)  # 呼吸频率 (breaths per minute)
MUSCLE_TENSION_RANGE = (1, 100)  # 肌肉张紧度 (1-10 scale)
SWEAT_RANGE = (1, 100)  # 出汗程度 (1-10 scale)

# 定义生成符合正态分布的随机数的函数
def generate_normal_random(mean, std_dev, min_val, max_val):
    while True:
        value = np.random.normal(mean, std_dev)
        if min_val <= value <= max_val:
            return value

# 定义生成心跳频率的函数
def generate_heart_rate():
    mean = (HEART_RATE_RANGE[0] + HEART_RATE_RANGE[1]) / 2
    std_dev = (HEART_RATE_RANGE[1] - HEART_RATE_RANGE[0]) / 6  # 99.7% 的数据在3个标准差内
    return generate_normal_random(mean, std_dev, HEART_RATE_RANGE[0], HEART_RATE_RANGE[1])

# 定义生成呼吸频率的函数
def generate_respiratory_rate():
    mean = (RESPIRATORY_RATE_RANGE[0] + RESPIRATORY_RATE_RANGE[1]) / 2
    std_dev = (RESPIRATORY_RATE_RANGE[1] - RESPIRATORY_RATE_RANGE[0]) / 6
    return generate_normal_random(mean, std_dev, RESPIRATORY_RATE_RANGE[0], RESPIRATORY_RATE_RANGE[1])

# 定义生成肌肉张紧度的函数
def generate_muscle_tension():
    mean = (MUSCLE_TENSION_RANGE[0] + MUSCLE_TENSION_RANGE[1]) / 2
    std_dev = (MUSCLE_TENSION_RANGE[1] - MUSCLE_TENSION_RANGE[0]) / 6
    return generate_normal_random(mean, std_dev, MUSCLE_TENSION_RANGE[0], MUSCLE_TENSION_RANGE[1])

# 定义生成出汗程度的函数
def generate_sweat():
    mean = (SWEAT_RANGE[0] + SWEAT_RANGE[1]) / 2
    std_dev = (SWEAT_RANGE[1] - SWEAT_RANGE[0]) / 6
    return generate_normal_random(mean, std_dev, SWEAT_RANGE[0], SWEAT_RANGE[1])

# 定义多线程生成数据的函数
def generate_data(thread_id):
    while True:
        heart_rate = generate_heart_rate()
        respiratory_rate = generate_respiratory_rate()
        muscle_tension = generate_muscle_tension()
        sweat = generate_sweat()
        
        print(f"Thread {thread_id}: Heart Rate: {heart_rate:.2f} bpm, Respiratory Rate: {respiratory_rate:.2f} breaths/min, "
              f"Muscle Tension: {muscle_tension:.2f}, Sweat: {sweat:.2f}")
        
        time.sleep(1)  # 每隔1秒生成一次数据

# 创建并启动多个线程
num_threads = 4  # 可以根据需要调整线程数量
threads = []

for i in range(num_threads):
    thread = threading.Thread(target=generate_data, args=(i,))
    thread.start()
    threads.append(thread)

# 等待所有线程完成
for thread in threads:
    thread.join()