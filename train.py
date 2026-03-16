from ultralytics import YOLO
import os

# 获取当前脚本所在的绝对路径，防止找不到文件
current_dir = os.getcwd()
dataset_dir = os.path.join(current_dir, 'datasets')

# 1. 动态生成 data.yaml
yaml_content = f"""
path: {dataset_dir}  # 自动指向当前目录下的 datasets 文件夹
train: images/train
val: images/val
nc: 3
names: ['Prohibitory', 'Warning', 'Mandatory']
"""

with open('data.yaml', 'w') as f:
    f.write(yaml_content)

print(f"配置已生成，数据集路径: {dataset_dir}")

# 2. 加载模型
model = YOLO('yolo11n.pt')

# 3. 开始训练
# 训练参数说明：
# - epochs=100: 训练100轮（充分训练）
# - imgsz=640: 输入图像尺寸 640x640
# - batch=32: 每批32张图片
# - workers=8: 数据加载使用8个线程
# - name='bitahub_train': 输出文件夹名称
model.train(data='data.yaml', epochs=100, imgsz=640, batch=32, workers=8, name='bitahub_train')