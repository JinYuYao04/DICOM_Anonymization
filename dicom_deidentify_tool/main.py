"""
DICOM脱敏工具 - 主程序
支持DICOM文件的标签查看和脱敏处理
"""
import sys
import os
from pathlib import Path

# 在导入pydicom之前先打补丁，避免PyInstaller打包时的导入错误
import pydicom_patch
sys.modules['pydicom.data'] = pydicom_patch
sys.modules['pydicom.examples'] = pydicom_patch

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow


def main():
    # 启用高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("DICOM脱敏工具")
    app.setOrganizationName("DicomVision")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
