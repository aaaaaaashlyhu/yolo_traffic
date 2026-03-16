# 🚦 智能交通标志检测系统

## 项目简介

基于 **YOLOv11 深度学习** 的交通标志智能检测系统。本系统支持图片和视频中的交通标志、行人、车辆等元素的实时识别和分析，可用于智能交通监控、自动驾驶辅助等应用场景。

**项目类型**：毕业课设 | **开发周期**：2025-2026

---

## 🎯 核心功能

### 1. 数据处理与标注
- ✅ XML 格式标注转换为 YOLO 格式
- ✅ 自动数据集划分（train/val）
- ✅ 基于颜色识别的自动标注辅助
- ✅ 标注质量可视化验证

### 2. 模型训练
- ✅ YOLOv11n 迁移学习
- ✅ **100 Epochs 充分训练**
- ✅ 完整的训练指标统计和可视化

### 3. 推理与检测
- ✅ **双模型融合架构**：
  - Model A：自训练交通标志检测（专一性强）
  - Model B：官方通用检测（行人、车辆）
- ✅ 支持图片、视频、摄像头实时推理
- ✅ 置信度阈值可动态调整

### 4. 可视化界面（二选一）
- ✅ **PyQt6 桌面应用** (`main_system.py`)
  - 实时视频监控
  - 统计仪表板（行人数、车辆数、标志数、FPS）
  - 事件日志记录
  
- ✅ **Streamlit Web 应用** (`Web_System/app.py`)
  - 图片上传检测
  - 置信度阈值滑块
  - 响应式网页界面

---

## 📊 性能指标

### 模型训练结果（100 Epochs）
| 指标 | 数值 | 评级 |
|------|------|------|
| **Precision** | 93.88% | ⭐⭐⭐ 优秀 |
| **Recall** | 89.55% | ⭐⭐⭐ 优秀 |
| **mAP50** | 94.90% | ⭐⭐⭐ 优秀 |
| **mAP50-95** | 69.91% | ⭐⭐⭐ 优秀 |

### 推理速度
- CPU: ~15-20 FPS
- GPU: ~45+ FPS (取决于显卡)

---

## 🏗️ 项目结构

```
pythonProject1/
├── 📄 README.md                    # 项目说明文档（本文件）
├── 📄 TRAINING_REPORT.md           # 模型训练详细报告
├── 📄 requirements.txt             # 依赖包清单
├── 📄 train.py                     # 模型训练脚本（100 Epochs）
├── 📄 main_system.py               # PyQt6 GUI 应用（双模型）
├── 📄 predict_video.py             # 视频推理脚本
├── 📄 test_fusion.py               # 双模型融合测试
├── 📄 split_data.py                # 数据集划分工具
├── 📄 auto_label_v3_final.py       # 自动标注辅助
├── 📄 check_labels.py              # 标注可视化
├── 📄 generate_plots.py            # 训练曲线可视化
│
├── 📁 datasets/                    # YOLO 格式数据集
│   ├── images/
│   │   ├── train/                  # 训练集图片
│   │   └── val/                    # 验证集图片
│   └── labels/
│       ├── train/                  # 训练集标签
│       └── val/                    # 验证集标签
│
├── 📁 Web_System/                  # Streamlit Web 应用
│   ├── app.py                      # Web 应用主程序
│   └── bestvvv.pt                  # 模型文件（或相对引用根目录）
│
├── 📁 train/                       # 训练输出结果
│   ├── weights/
│   │   ├── best.pt                 # 最佳权重
│   │   └── last.pt                 # 最后权重
│   └── [训练可视化结果...]         # 曲线图、混淆矩阵等
│
├── 🤖 bestvvv.pt                   # 最终推理模型（3类交通标志）
├── 🤖 yolo11n.pt                   # 官方 YOLOv11n 预训练
├── 🤖 yolov8n.pt                   # 官方 YOLOv8n 预训练
└── 📁 .venv/                       # Python 虚拟环境

```

---

## 🚀 快速开始

### 前置要求
- **Python**: 3.8+
- **操作系统**: Windows / Linux / macOS
- **显存**: 建议 >= 2GB (GPU加速)

### 1. 环境配置

#### 方式 A：使用虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 方式 B：使用 conda
```bash
conda create -n traffic_signs python=3.10
conda activate traffic_signs
pip install -r requirements.txt
```

### 2. 运行推理

#### 选项 1️⃣：PyQt6 GUI 应用（推荐演示）
```bash
python main_system.py
```

**功能**：
- 实时视频监控
- 双模型融合检测
- 统计数据展示
- 事件日志记录

**修改视频源**：编辑 `main_system.py` 第 XX 行
```python
video_source = 'test4.mp4'  # 改为你的视频文件或 0（摄像头）
```

#### 选项 2️⃣：Streamlit Web 应用
```bash
cd Web_System
streamlit run app.py
```

然后在浏览器打开 `http://localhost:8501`

#### 选项 3️⃣：单个图片或视频推理
```bash
python predict_video.py
```

---

## 📚 详细使用说明

### 训练新模型

```bash
python train.py
```

**参数说明**（见 `train.py`）：
- `epochs=100`：训练 100 轮（充分训练）
- `imgsz=640`：输入图像尺寸
- `batch=32`：每批 32 张图片
- `workers=8`：数据加载线程

**输出**：
- 权重保存在 `./train/weights/`
- 训练曲线、混淆矩阵等可视化图表

### 数据处理

```bash
# 1. 数据集划分（XML → YOLO格式）
python split_data.py

# 2. 自动标注辅助（颜色识别）
python auto_label_v3_final.py

# 3. 标注可视化验证
python check_labels.py
```

---

## 🔍 检测对象（3类）

| 类别 ID | 中文名 | 英文名 | 特征 |
|--------|--------|--------|------|
| 0 | 禁令标志 | Prohibitory | 🔴 红圆形 |
| 1 | 警告标志 | Warning | 🟡 黄三角 |
| 2 | 指示标志 | Mandatory | 🔵 蓝圆形 |

**额外检测**（通过官方模型）：
- 👤 行人 (Person)
- 🚗 车辆 (Car, Bus, Truck, Motorcycle)

---

## 📋 依赖包

详见 `requirements.txt`（394 个包）

**主要依赖**：
- `ultralytics>=8.0.0` - YOLO 框架
- `opencv-python>=4.5.0` - 图像处理
- `PyQt6>=6.0.0` - GUI 框架
- `streamlit>=1.0.0` - Web 框架
- `numpy`, `pandas`, `matplotlib` - 数据科学

---

## 🎓 项目特点

✅ **完整的毕设质量**
- 数据标注 → 模型训练 → 推理系统 → 可视化展现

✅ **工程规范**
- 清晰的文件结构
- 完整的文档说明
- 依赖版本锁定

✅ **双界面支持**
- 桌面应用（PyQt6）
- Web 应用（Streamlit）

✅ **双模型融合**
- 结合专一性和通用性
- 全面的交通场景理解

---

## 🐛 常见问题

### Q1: 模型文件（.pt）下载失败
**A**: 模型文件已包含在项目中（`bestvvv.pt`, `yolo11n.pt` 等），无需额外下载。

### Q2: PyQt6 GUI 弹不出窗口
**A**: 检查：
1. Python 环境是否正确激活
2. 是否成功 `pip install PyQt6`
3. 尝试 `python main_system.py` 在命令行查看错误

### Q3: 推理速度慢（FPS 低）
**A**: 
- 考虑使用 GPU 加速（安装 CUDA）
- 降低 `imgsz` 参数（如改为 416）
- 关闭其他程序释放 CPU/显存

### Q4: 怎么改模型或置信度参数?
**A**: 
- 置信度：Web应用中有滑块，桌面应用需编辑源码（见 `main_system.py` 第 XX 行 `conf=0.25`）
- 模型路径：编辑各脚本中的 `YOLO('path/to/model.pt')`

---

## 📖 更多文档

- [`TRAINING_REPORT.md`](TRAINING_REPORT.md) - 完整的训练日志和性能分析
- [`train.py`](train.py) - 训练脚本详尽注释
- [`main_system.py`](main_system.py) - PyQt6 GUI 代码注释

---

## 📧 技术支持

如有问题或建议，请：
1. 检查上述常见问题
2. 查看各脚本的详细注释
3. 参考 `train/`  文件夹中的可视化结果

---

## 📝 许可证

本项目仅供学习和毕设展示使用。  
模型基于 Ultralytics YOLOv11，遵守其许可证。

---

## ✨ 项目成就

- ✅ **训练完成**：100 Epochs，mAP50 达到 94.9%
- ✅ **双界面**：PyQt6 + Streamlit 两种使用方式
- ✅ **可视化完整**：训练曲线、混淆矩阵、推理结果
- ✅ **工程规范**：文档齐全、结构清晰、便于复现

---

**Last Updated**: 2026-03-16  
**Version**: 1.0.0
