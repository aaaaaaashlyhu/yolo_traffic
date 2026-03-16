import os
import random
import shutil
import xml.etree.ElementTree as ET
from tqdm import tqdm  # 进度条库，如果报错请 pip install tqdm

# ================= 配置区域 =================
# 原始数据路径 (基于你的截图)
RAW_IMAGE_DIR = 'raw_data/train/images'  # 假设图片都在这里
RAW_XML_DIR = 'raw_data/XML'  # 假设xml都在这里

# 输出路径 (就是你刚建好的 datasets)
BASE_DIR = 'datasets'

# 划分比例
TRAIN_RATIO = 0.8


# 类别映射 (CCTSDB 特有逻辑)
# 0: Prohibitory (禁令, 红圆), 1: Warning (警告, 黄三角), 2: Mandatory (指示, 蓝圆)
def get_class_id(class_name):
    class_name = class_name.lower()
    if class_name.startswith('p'): return 0  # 比如 p1, pne
    if class_name.startswith('w'): return 1  # 比如 w1, w57
    if class_name.startswith('i'): return 2  # 比如 i1, i5
    return -1  # 其他忽略


# ================= 主逻辑 =================
def convert_box(size, box):
    # 将 XML 的 (xmin, ymin, xmax, ymax) 转为 YOLO 的 (x, y, w, h)
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    return (x * dw, y * dh, w * dw, h * dh)


def main():
    # 1. 收集所有图片文件
    print("正在扫描图片...")
    if not os.path.exists(RAW_IMAGE_DIR):
        print(f"错误: 找不到文件夹 {RAW_IMAGE_DIR}")
        return

    images = [f for f in os.listdir(RAW_IMAGE_DIR) if f.endswith('.jpg') or f.endswith('.png')]
    random.shuffle(images)  # 打乱顺序

    train_count = int(len(images) * TRAIN_RATIO)
    print(f"共找到 {len(images)} 张图片。训练集: {train_count}, 验证集: {len(images) - train_count}")

    # 2. 开始处理
    for i, image_name in enumerate(tqdm(images)):
        # 决定是 train 还是 val
        subset = 'train' if i < train_count else 'val'

        # 构建文件路径
        image_src_path = os.path.join(RAW_IMAGE_DIR, image_name)
        xml_name = image_name.rsplit('.', 1)[0] + '.xml'
        xml_src_path = os.path.join(RAW_XML_DIR, xml_name)

        # 检查 XML 是否存在
        if not os.path.exists(xml_src_path):
            continue  # 如果没标签就跳过

        # 解析 XML
        try:
            tree = ET.parse(xml_src_path)
            root = tree.getroot()
            size = root.find('size')
            w_img = int(size.find('width').text)
            h_img = int(size.find('height').text)

            # 准备写入 txt 的内容
            yolo_lines = []
            for obj in root.iter('object'):
                cls_name = obj.find('name').text
                cls_id = get_class_id(cls_name)

                if cls_id != -1:
                    xmlbox = obj.find('bndbox')
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                         float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    bb = convert_box((w_img, h_img), b)
                    yolo_lines.append(f"{cls_id} {bb[0]} {bb[1]} {bb[2]} {bb[3]}")

            # 如果这张图里有我们要的目标，才保存
            if yolo_lines:
                # 复制图片
                target_img_path = os.path.join(BASE_DIR, 'images', subset, image_name)
                shutil.copy(image_src_path, target_img_path)

                # 保存 txt
                txt_name = image_name.rsplit('.', 1)[0] + '.txt'
                target_txt_path = os.path.join(BASE_DIR, 'labels', subset, txt_name)
                with open(target_txt_path, 'w') as f:
                    f.write('\n'.join(yolo_lines))

        except Exception as e:
            print(f"处理 {image_name} 时出错: {e}")

    print("处理完成！请检查 datasets 文件夹。")


if __name__ == '__main__':
    main()