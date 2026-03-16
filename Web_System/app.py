# app.py - 交通标志检测系统主程序

import streamlit as st  # 1. 导入 Streamlit，它是做网页的神器
from ultralytics import YOLO  # 2. 导入 YOLO，它是核心算法
from PIL import Image  # 3. 导入图片处理库，用来读取上传的图片

# --- 页面基础设置 ---
st.set_page_config(page_title="交通标志检测", layout="wide")
st.title("🚦 交通标志智能检测系统")  # 网页的大标题

# --- 侧边栏：用来调节参数 ---
st.sidebar.title("控制面板")
# 这是一个滑动条，范围 0.0 到 1.0。
# 作用：告诉模型“有多大把握你才敢画框？”
# 如果设为 0.5，说明模型认为只有 50% 以上概率是标志的，才画出来。
conf_threshold = st.sidebar.slider("置信度阈值 (Confidence)", 0.0, 1.0, 0.25, 0.01)

# --- 核心逻辑：加载模型 ---
# 这里有一个“容错机制”：
# 如果你的 best.pt 还没下载下来，我们先用官方的 yolov8n.pt 顶替一下，
# 这样你现在就能运行网页，看效果，不用等训练完。
#model_path = 'final_model_v3.pt'
model_path = 'bestvvv.pt'
try:
    model = YOLO(model_path)
    st.sidebar.success("✅ 已加载你是自训练模型 (best.pt)")
except:
    st.sidebar.warning("⚠️ 未找到 best.pt，暂时使用官方基础模型测试")
    model = YOLO('yolov8n.pt')  # 会自动下载官方模型

# --- 用户交互区 ---
uploaded_file = st.file_uploader("请上传一张包含交通标志的图片...", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # 1. 读取图片
    image = Image.open(uploaded_file)

    # 2. 界面布局：左边放原图，右边放结果
    col1, col2 = st.columns(2)

    with col1:
        st.header("原始图片")
        st.image(image, use_container_width=True)

    # 3. 开始检测
    # 这里加个按钮，防止一上传就自动运行，更有“系统感”
    if st.button("🚀 点击开始检测"):
        with st.spinner('正在调用 YOLOv8 模型进行分析...'):
            # --- 关键代码：模型推理 ---
            # source: 图片
            # conf: 我们刚才在侧边栏设定的阈值
            results = model.predict(source=image, conf=conf_threshold)

            # --- 结果处理 ---
            # plot() 是 YOLO 自带的画图功能，它会自动把框画在图上
            res_plotted = results[0].plot()

            # OpenCV/YOLO 默认是 BGR 颜色，网页显示需要 RGB，所以要转一下颜色
            res_rgb = res_plotted[:, :, ::-1]

        with col2:
            st.header("检测结果")
            st.image(res_rgb, use_container_width=True)

            # 4. 显示一些统计信息 (显得很专业)
            st.success("检测完成！")
            # 统计检测到了几个目标
            boxes = results[0].boxes
            st.write(f"📊 共检测到 **{len(boxes)}** 个目标")