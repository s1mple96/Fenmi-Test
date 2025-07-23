from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QLinearGradient

class RealChinaMapWidget(QFrame):
    """真实中国地图绘制组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(700, 600)
        self.setStyleSheet("background-color: #f8f9fa; border: 2px solid #dee2e6; border-radius: 15px;")
        
        # 省份位置映射 (x, y, width, height, 省份简称, 全名, 颜色)
        self.province_positions = [
            # 东北地区 - 绿色
            (450, 80, 60, 40, "黑", "黑龙江", "#90EE90"),
            (420, 120, 50, 35, "吉", "吉林", "#90EE90"),
            (390, 140, 50, 35, "辽", "辽宁", "#90EE90"),
            
            # 华北地区 - 粉色
            (350, 120, 50, 35, "蒙", "内蒙古", "#FFB6C1"),
            (320, 140, 50, 35, "冀", "河北", "#FFB6C1"),
            (290, 160, 50, 35, "京", "北京", "#FFB6C1"),
            (260, 160, 50, 35, "津", "天津", "#FFB6C1"),
            (230, 180, 50, 35, "晋", "山西", "#FFB6C1"),
            
            # 华东地区 - 橙色
            (380, 200, 50, 35, "鲁", "山东", "#FFA500"),
            (350, 220, 50, 35, "苏", "江苏", "#FFA500"),
            (320, 240, 50, 35, "沪", "上海", "#FFA500"),
            (290, 260, 50, 35, "浙", "浙江", "#FFA500"),
            (260, 280, 50, 35, "皖", "安徽", "#FFA500"),
            (230, 300, 50, 35, "闽", "福建", "#FFA500"),
            (200, 320, 50, 35, "赣", "江西", "#FFA500"),
            
            # 华中地区 - 绿色
            (290, 320, 50, 35, "鄂", "湖北", "#90EE90"),
            (260, 340, 50, 35, "湘", "湖南", "#90EE90"),
            (230, 360, 50, 35, "豫", "河南", "#90EE90"),
            
            # 华南地区 - 深橙色
            (200, 380, 50, 35, "粤", "广东", "#FF8C00"),
            (170, 400, 50, 35, "桂", "广西", "#FF8C00"),
            (140, 420, 50, 35, "琼", "海南", "#FF8C00"),
            
            # 西南地区 - 黄色
            (170, 320, 50, 35, "贵", "贵州", "#FFFF00"),
            (140, 340, 50, 35, "云", "云南", "#FFFF00"),
            (110, 360, 50, 35, "川", "四川", "#FFFF00"),
            (80, 380, 50, 35, "藏", "西藏", "#FFFF00"),
            (50, 400, 50, 35, "渝", "重庆", "#FFFF00"),
            
            # 西北地区 - 浅蓝色
            (200, 200, 50, 35, "陕", "陕西", "#87CEEB"),
            (170, 220, 50, 35, "甘", "甘肃", "#87CEEB"),
            (140, 240, 50, 35, "青", "青海", "#87CEEB"),
            (110, 260, 50, 35, "宁", "宁夏", "#87CEEB"),
            (80, 280, 50, 35, "新", "新疆", "#87CEEB"),
        ]
        
        self.province_buttons = {}
        self.selected_province = None
        self.create_province_buttons()
    
    def create_province_buttons(self):
        """创建省份按钮"""
        for x, y, w, h, province, full_name, color in self.province_positions:
            btn = QPushButton(province, self)
            btn.setGeometry(x, y, w, h)
            btn.setToolTip(full_name)  # 添加工具提示显示全名
            
            # 设置按钮样式
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 2px solid #4682b4;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #2f4f4f;
                }}
                QPushButton:hover {{
                    background-color: #98fb98;
                    border-color: #32cd32;
                    transform: scale(1.1);
                }}
                QPushButton:pressed {{
                    background-color: #90ee90;
                }}
            """)
            btn.clicked.connect(lambda checked, p=province: self.select_province(p))
            self.province_buttons[province] = btn
    
    def select_province(self, province):
        """选择省份"""
        self.selected_province = province
        # 重置所有按钮样式
        for btn in self.province_buttons.values():
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #87ceeb;
                    border: 2px solid #4682b4;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #2f4f4f;
                }
                QPushButton:hover {
                    background-color: #98fb98;
                    border-color: #32cd32;
                }
                QPushButton:pressed {
                    background-color: #90ee90;
                }
            """)
        
        # 高亮选中的省份
        if province in self.province_buttons:
            self.province_buttons[province].setStyleSheet("""
                QPushButton {
                    background-color: #ff6347;
                    border: 3px solid #dc143c;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }
            """)
    
    def paintEvent(self, event):
        """绘制真实的中国地图轮廓"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 700, 600)
        gradient.setColorAt(0, QColor("#f0f8ff"))
        gradient.setColorAt(1, QColor("#e6f3ff"))
        painter.fillRect(self.rect(), gradient)
        
        # 绘制地图轮廓
        pen = QPen(QColor("#4682b4"), 4)
        painter.setPen(pen)
        
        # 创建中国地图轮廓路径
        path = QPainterPath()
        
        # 中国地图轮廓坐标点（更真实的地图形状）
        china_outline = [
            (450, 100),  # 东北角
            (465, 105),  # 东北部
            (480, 110),  # 东北部
            (490, 115),  # 东部
            (500, 125),  # 东部
            (510, 140),  # 东部沿海
            (515, 160),  # 东部沿海
            (513, 180),  # 东部
            (510, 200),  # 东部
            (505, 220),  # 东南部
            (500, 240),  # 东南沿海
            (495, 260),  # 东南沿海
            (490, 280),  # 南部沿海
            (485, 300),  # 南部沿海
            (475, 320),  # 南部
            (450, 340),  # 南部
            (420, 350),  # 西南部
            (380, 355),  # 西南
            (320, 360),  # 西部
            (250, 358),  # 西北部
            (180, 350),  # 西北
            (120, 335),  # 西北部
            (80, 320),   # 西部
            (60, 300),   # 西部
            (50, 280),   # 西部
            (45, 260),   # 西部
            (50, 240),   # 西北部
            (60, 220),   # 西北部
            (80, 200),   # 西北部
            (120, 180),  # 北部
            (180, 165),  # 东北部
            (250, 155),  # 东北
            (320, 145),  # 东北
            (380, 135),  # 东北
            (420, 125),  # 东北
            (450, 100),  # 回到起点
        ]
        
        # 绘制主要轮廓
        path.moveTo(china_outline[0][0], china_outline[0][1])
        for x, y in china_outline[1:]:
            path.lineTo(x, y)
        path.closeSubpath()
        
        # 绘制地图轮廓
        painter.drawPath(path)
        
        # 绘制海南岛
        hainan_path = QPainterPath()
        hainan_points = [
            (140, 420), (160, 425), (175, 430), (180, 435), (175, 440),
            (160, 445), (145, 440), (140, 435), (140, 420)
        ]
        hainan_path.moveTo(hainan_points[0][0], hainan_points[0][1])
        for x, y in hainan_points[1:]:
            hainan_path.lineTo(x, y)
        painter.drawPath(hainan_path)
        
        # 绘制台湾岛
        taiwan_path = QPainterPath()
        taiwan_points = [
            (480, 280), (490, 285), (495, 290), (495, 295), (490, 300),
            (485, 300), (480, 295), (480, 280)
        ]
        taiwan_path.moveTo(taiwan_points[0][0], taiwan_points[0][1])
        for x, y in taiwan_points[1:]:
            taiwan_path.lineTo(x, y)
        painter.drawPath(taiwan_path)
        
        # 绘制标题
        painter.setPen(QColor("#2f4f4f"))
        font = QFont("Microsoft YaHei", 18, QFont.Bold)
        painter.setFont(font)
        painter.drawText(QRect(0, 20, 700, 50), Qt.AlignCenter, "中国地图 - 点击省份进行选择")
        
        # 绘制图例
        legend_font = QFont("Microsoft YaHei", 12)
        painter.setFont(legend_font)
        painter.setPen(QColor("#333"))
        
        # 绘制地区标识
        regions = [
            ("东北", 480, 80, "#90EE90"),
            ("华北", 320, 120, "#FFB6C1"),
            ("华东", 380, 220, "#FFA500"),
            ("华中", 280, 320, "#90EE90"),
            ("华南", 180, 380, "#FF8C00"),
            ("西南", 120, 340, "#FFFF00"),
            ("西北", 150, 200, "#87CEEB")
        ]
        
        for region, x, y, color in regions:
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor("#333"), 2))
            painter.drawEllipse(x, y, 10, 10)
            painter.setPen(QColor("#333"))
            painter.drawText(x + 15, y + 8, region)

class RealChinaMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择省份 - 真实中国地图")
        self.setFixedSize(750, 700)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建地图组件
        self.map_widget = RealChinaMapWidget()
        layout.addWidget(self.map_widget, alignment=Qt.AlignCenter)
        
        # 添加说明文字
        info_label = QLabel("点击地图上的省份进行选择，鼠标悬停可查看省份全名")
        info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 15px;
                background-color: #e9ecef;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 添加按钮区域
        button_layout = QHBoxLayout()
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.selected = None

    def accept(self):
        """确认选择"""
        self.selected = self.map_widget.selected_province
        if self.selected:
            super().accept()
        else:
            QMessageBox.warning(self, "提示", "请先选择一个省份！")

    def select_province(self, prov):
        self.selected = prov
        self.accept() 