#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实中国地图样式的省份选择对话框
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append('.')

def test_real_china_map():
    """测试真实中国地图对话框"""
    print("=" * 60)
    print("测试真实中国地图样式的省份选择对话框")
    print("=" * 60)
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QMessageBox
        from PyQt5.QtCore import Qt
        from ui.components.real_china_map_dialog import RealChinaMapDialog
        
        print("✓ PyQt5 导入成功")
        print("✓ 真实中国地图对话框导入成功")
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = QMainWindow()
        main_window.setWindowTitle("真实中国地图省份选择演示")
        main_window.setGeometry(100, 100, 600, 400)
        
        # 创建中央部件
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title_label = QLabel("真实中国地图样式省份选择对话框演示")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                padding: 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #f0f8ff, stop:1 #e6f3ff);
                border: 3px solid #4682b4;
                border-radius: 15px;
                margin: 15px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加说明
        desc_label = QLabel("""
        新功能特性：
        🗺️ 更真实的中国地图轮廓
        🎨 按地区分色的省份按钮（东北绿、华北粉、华东橙、华中绿、华南深橙、西南黄、西北浅蓝）
        💡 鼠标悬停显示省份全名
        🎯 选中省份红色高亮显示
        🌊 渐变背景效果
        🏝️ 海南岛和台湾岛绘制
        📍 地区标识图例
        """)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555;
                padding: 20px;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin: 15px;
                line-height: 1.6;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 添加按钮区域
        button_layout = QHBoxLayout()
        
        # 打开真实地图对话框按钮
        open_btn = QPushButton("打开真实中国地图选择器")
        open_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #45a049, stop:1 #3d8b40);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
        """)
        
        def open_real_map_dialog():
            dialog = RealChinaMapDialog(main_window)
            result = dialog.exec_()
            
            if result == RealChinaMapDialog.Accepted:
                selected_province = dialog.selected
                if selected_province:
                    QMessageBox.information(
                        main_window, 
                        "选择结果", 
                        f"您选择的省份是：{selected_province}\n\n"
                        f"这是一个更真实的中国地图样式选择器！"
                    )
                else:
                    QMessageBox.warning(main_window, "提示", "未选择任何省份")
            else:
                QMessageBox.information(main_window, "提示", "您取消了选择")
        
        open_btn.clicked.connect(open_real_map_dialog)
        button_layout.addWidget(open_btn)
        
        # 退出按钮
        exit_btn = QPushButton("退出演示")
        exit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f44336, stop:1 #da190b);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #da190b, stop:1 #c62828);
            }
        """)
        exit_btn.clicked.connect(main_window.close)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        
        # 显示窗口
        main_window.show()
        print("✓ 演示窗口已创建并显示")
        print("💡 提示: 点击'打开真实中国地图选择器'按钮查看效果")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"✗ PyQt5 导入失败: {e}")
        print("请安装 PyQt5: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"✗ 创建演示应用失败: {e}")
        return 1

def main():
    """主函数"""
    print("真实中国地图样式省份选择对话框演示")
    print("=" * 60)
    
    # 检查文件是否存在
    required_files = [
        'ui/components/real_china_map_dialog.py'
    ]
    
    print("检查文件结构...")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - 文件不存在")
            return 1
    
    print("\n启动演示程序...")
    return test_real_china_map()

if __name__ == "__main__":
    sys.exit(main()) 