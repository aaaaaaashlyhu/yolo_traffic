# 🎯 交通标志检测系统 - PyQt6 桌面应用

这是一个完整的计算机视觉毕设项目，采用 **PyQt6** 开发，支持多种实时检测场景和数据导出。

## ✨ 核心功能

### 1. 🔐 **用户认证系统**
- ✅ 用户注册/登录
- ✅ 密码加密存储 (PBKDF2-SHA256)
- ✅ Token 会话管理 (可设置过期时间)
- ✅ 用户统计 (检测次数、最后登录时间等)
- ✅ 演示账号: `demo` / `demo123`

### 2. 🖼️ **图片检测**
- ✅ 拖拽图片到窗口
- ✅ 文件浏览器选择
- ✅ 单张图片智能检测
- ✅ 检测结果可视化

### 3. 🎬 **视频逐帧处理**
- ✅ 支持 MP4/AVI/MOV 格式
- ✅ 播放/暂停/停止控制
- ✅ 进度条快进快退
- ✅ 实时 FPS 统计

### 4. 📹 **摄像头实时检测**
- ✅ 多摄像头支持
- ✅ 30+ FPS 实时检测
- ✅ 帧捕获功能
- ✅ 分辨率和FPS显示

### 5. 📊 **结果导出**
- ✅ 导出标注图片 (PNG)
- ✅ 导出检测CSV
  - 检测类型、置信度、时间戳
  - 用户信息、Token (脱敏)
- ✅ 一键打开结果文件夹

### 6. ⚙️ **智能参数调整**
- ✅ 实时修改置信度阈值 (0-0.95)
- ✅ 检测模式切换
- ✅ IOU 阈值自定义

## 🚀 快速开始

### 前置条件
- Python 3.8+
- CUDA 11.0+ (可选，用于加速推理)

### 安装

1. **克隆/进入项目目录**
```bash
cd d:\Pycharm\pythonProject1
```

2. **安装依赖**
```bash
# 安装基础依赖
pip install -r requirements_pyqt6.txt

# 或者使用 conda
conda install -c pytorch pytorch torchvision torchaudio pytorch-cuda=11.8
conda install ultralytics opencv-python PyQt6 pandas
```

3. **验证模型文件**
确保以下模型文件存在:
- `bestvvv.pt` (交通标志检测模型)
- `yolo11n.pt` 或 `yolov8n.pt` (通用检测模型)

### 运行应用

```bash
python app.py
```
conda activate pythonProject1
python run.py


## 📖 使用指南

### 首次登录
1. 点击 **注册** 标签页
2. 输入用户名 (≥3字符)
3. 输入密码 (≥6字符)
4. 点击 **注 册**
5. 切换到 **登 录** 标签页输入凭证

### 或使用演示账号
- 用户名: `demo`
- 密码: `demo123`

### 图片检测
1. **方式A**: 直接拖拽图片到显示区域
2. **方式B**: 点击 **选择图片** 按钮
3. 调整右侧 **检测参数**（置信度、检测模式等）
4. 点击 **开始检测**
5. 查看结果和统计信息

### 视频逐帧
1. 点击 **选择视频** 选择视频文件
2. 使用 **播放/暂停/停止** 控制
3. 也可拖动进度条
4. 实时查看检测结果

### 实时摄像头
1. 从下拉菜单选择摄像头 (通常默认为主摄像头)
2. 点击 **开启** 启动实时检测
3. 点击 **捕获当前帧** 保存当前检测结果
4. 点击 **关闭** 停止

### 结果导出
1. **导出结果图**: 保存标注后的检测图片
2. **导出检测CSV**: 导出检测统计数据
   ```csv
   timestamp,type,confidence,用户,Token
   2024-01-15T10:30:45.123456,Stop_Sign,0.95,demo,a7f4d2c8e9b1f3k...
   ```
3. **打开结果文件夹**: 查看所有导出文件

## 📁 项目结构

```
pythonProject1/
├── app.py                      # 应用启动入口
├── login_dialog.py             # 登录窗口
├── main_window.py              # 主应用窗口
├── 
├── core/
│   ├── __init__.py
│   ├── auth_manager.py         # ✨ 用户认证系统
│   ├── model_manager.py        # 模型管理
│   ├── resource_manager.py     # 资源管理
│   └── exceptions.py           # 异常定义
│
├── detection_results/          # 导出结果目录 (自动创建)
│   ├── detection_20240115_103045.png
│   ├── detection_20240115_103045.csv
│   └── capture_20240115_103100.png
│
├── requirements_pyqt6.txt      # PyQt6 依赖
├── bestvvv.pt                  # 交通标志检测模型
├── yolo11n.pt                  # 或 yolov8n.pt
└── users_db.json               # 用户数据库 (自动创建)
```

## 🔐 安全特性

### 密码安全
- 使用 **PBKDF2-SHA256** 加密
- 10 万次迭代 + 随机 Salt
- 数据库中存储的是哈希值，不是明文

### Token 管理
- 生成 **256-bit** 密码学安全 Token
- 可设置过期时间 (默认24小时)
- 自动清理过期 Token
- Token 在导出 CSV 时脱敏

### 数据存储
- 用户数据存储在本地 JSON 文件
- 支持备份和恢复
- 完整的登录历史记录

## 📊 CSV 导出格式

```csv
timestamp,type,confidence,用户,Token
2024-01-15T10:30:45.123456,Stop_Sign,0.95,demo,a7f4d2c8e9b1f3...
2024-01-15T10:30:46.234567,Person,0.87,demo,a7f4d2c8e9b1f3...
2024-01-15T10:30:47.345678,Car,0.92,demo,a7f4d2c8e9b1f3...
```

## 🎨 UI 特点

- 🎨 现代 Fusion 风格
- 📱 响应式布局
- 🌈 彩色按钮 (绿-执行, 红-取消, 蓝-选择)
- 📊 实时统计信息板
- 🎯 直观的标签页导航

## 🔧 高级配置

### 修改 Token 过期时间
编辑 `login_dialog.py`:
```python
success, msg, token = self.auth_manager.login(username, password, token_expiry_hours=48)  # 改为 48 小时
```

### 修改默认检测参数
在 `main_window.py` 中:
```python
self.conf_slider.setValue(60)  # 改为 0.60 置信度
self.iou_spin.setValue(50)     # 改为 0.50 IOU
```

### 自定义模型
在 `core/model_manager.py` 中修改:
```python
def load_sign_model(self, primary: str = 'your_model.pt', ...):
```

## 📈 应答辩时的展示

1. **架构展示**
   - 分离的认证层 (auth_manager.py)
   - 可扩展的模型管理 (model_manager.py)
   - 完整的异常处理

2. **功能演示**
   - 现场注册新账号
   - 使用演示账号登录
   - 拖拽图片完整检测流程
   - 视频实时处理
   - 摄像头检测

3. **数据展示**
   - 导出 CSV 数据
   - 展示标注图片
   - 用户统计信息

4. **代码质量**
   - 类型提示完整
   - 文档字符串详细
   - 异常处理完善
   - 模块化设计

## 🐛 常见问题

**Q: 模型不存在？**
A: 确保 `bestvvv.pt` 或 `yolo11n.pt` 在项目根目录

**Q: 摄像头无法打开？**
A: 检查系统权限，或尝试 `camera_combo.addItems(["0", "1", "2"])`

**Q: Token 总是过期？**
A: 在 `auth_manager.py` 中增加 `token_expiry_hours`

**Q: CSV 无法打开？**
A: 尝试用记事本打开，确保编码为 UTF-8

## 📞 技术支持

项目采用以下技术栈:
- **PyQt6**: GUI 框架
- **YOLOv8/v11**: 目标检测
- **OpenCV**: 图像处理
- **PyTorch**: 深度学习


---

**v1.0.0** | 2024年1月 | 交通标志检测系统
