# 中国地图样式的省份选择对话框使用指南

## 概述

本项目已将原来的网格布局省份选择对话框升级为中国地图样式的交互式省份选择器。新的对话框提供了更直观、更美观的用户体验。

## 主要特性

### 🗺️ 中国地图轮廓
- 使用PyQt5的QPainterPath绘制真实的中国地图轮廓
- 包含海南岛和台湾岛的绘制
- 地图轮廓使用蓝色边框，浅蓝色填充

### 📍 省份精确定位
- 30个省份按钮按照地理位置精确放置在地图上
- 每个省份都有独立的按钮，支持点击选择
- 省份按钮使用蓝色背景，悬停时变为绿色

### 🎨 视觉反馈
- 选中的省份以红色高亮显示
- 不同地区用不同颜色的圆点标识
- 现代化的UI设计，圆角边框和渐变效果

### 🌍 地区分类
- 东北地区（红色标识）
- 华北地区（蓝色标识）
- 华东地区（绿色标识）
- 华中地区（黄色标识）
- 华南地区（橙色标识）
- 西南地区（紫色标识）
- 西北地区（粉色标识）

## 文件结构

```
ui/components/province_dialog.py    # 主要的省份选择对话框
ui/utils/provinces.py               # 省份数据导入
utils/data_factory.py               # 省份数据定义
test/test_province_dialog_*.py      # 测试文件
```

## 使用方法

### 基本用法

```python
from ui.components.province_dialog import ProvinceDialog

# 创建省份选择对话框
dialog = ProvinceDialog(parent_widget)

# 显示对话框并获取结果
result = dialog.exec_()

# 检查用户是否选择了省份
if result == ProvinceDialog.Accepted:
    selected_province = dialog.selected
    if selected_province:
        print(f"用户选择的省份: {selected_province}")
    else:
        print("用户未选择省份")
else:
    print("用户取消了选择")
```

### 在ETC申办界面中使用

```python
# 在您的UI组件中
def open_province_selection(self):
    """打开省份选择对话框"""
    dialog = ProvinceDialog(self)
    result = dialog.exec_()
    
    if result == ProvinceDialog.Accepted and dialog.selected:
        # 更新界面上的省份显示
        self.province_input.setText(dialog.selected)
        # 触发相关业务逻辑
        self.on_province_changed(dialog.selected)
```

## 技术实现

### 核心类

#### ChinaMapWidget
- 继承自QFrame
- 负责绘制中国地图轮廓
- 管理省份按钮的创建和布局
- 处理省份选择逻辑

#### ProvinceDialog
- 继承自QDialog
- 包含ChinaMapWidget实例
- 提供确定/取消按钮
- 处理对话框的确认和取消逻辑

### 地图绘制

```python
def paintEvent(self, event):
    """绘制中国地图轮廓"""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 创建中国地图轮廓路径
    path = QPainterPath()
    # ... 绘制地图轮廓
    painter.drawPath(path)
    
    # 绘制海南岛和台湾岛
    # ... 绘制岛屿
```

### 省份按钮管理

```python
def create_province_buttons(self):
    """创建省份按钮"""
    for x, y, w, h, province in self.province_positions:
        btn = QPushButton(province, self)
        btn.setGeometry(x, y, w, h)
        # ... 设置样式和事件
```

## 样式定制

### 修改省份按钮样式

```python
# 在ChinaMapWidget.create_province_buttons方法中修改
btn.setStyleSheet("""
    QPushButton {
        background-color: #87ceeb;  # 修改背景色
        border: 2px solid #4682b4;  # 修改边框
        border-radius: 5px;         # 修改圆角
        font-size: 14px;            # 修改字体大小
        font-weight: bold;
        color: #2f4f4f;             # 修改文字颜色
    }
    QPushButton:hover {
        background-color: #98fb98;  # 修改悬停颜色
        border-color: #32cd32;
    }
""")
```

### 修改地图颜色

```python
# 在ChinaMapWidget.paintEvent方法中修改
pen = QPen(QColor("#4682b4"), 3)    # 修改边框颜色
brush = QBrush(QColor("#f0f8ff"))   # 修改填充颜色
```

## 测试

### 运行测试

```bash
# 测试代码结构
python test/test_province_dialog_structure.py

# 测试完整功能（需要PyQt5环境）
python test/test_province_dialog.py
```

### 测试结果

所有测试都应该通过，包括：
- ✓ 文件结构检查
- ✓ 代码内容验证
- ✓ 省份数据结构验证
- ✓ 使用示例生成

## 兼容性

- Python 3.6+
- PyQt5 5.12+
- 支持Windows、macOS、Linux

## 注意事项

1. **依赖项**: 确保安装了PyQt5模块
2. **字体**: 建议使用Microsoft YaHei字体以获得最佳显示效果
3. **分辨率**: 对话框固定大小为650x600像素，适合大多数显示器
4. **性能**: 地图绘制使用抗锯齿渲染，确保平滑显示

## 更新日志

### v2.0.0 (当前版本)
- ✨ 新增中国地图样式的省份选择对话框
- 🎨 添加地图轮廓绘制功能
- 📍 实现省份精确定位
- 🎯 添加省份选择高亮功能
- 🌍 添加地区分类标识
- 🏝️ 添加海南岛和台湾岛绘制
- 🎨 现代化UI设计

### v1.0.0 (原版本)
- 基础的网格布局省份选择对话框

## 贡献

如果您想改进这个组件，请：
1. 确保代码符合项目的编码规范
2. 添加相应的测试用例
3. 更新文档说明

## 许可证

本项目遵循项目的整体许可证。 