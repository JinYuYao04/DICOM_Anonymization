"""
主窗口GUI
支持DICOM文件上传、标签查看、脱敏前后对比
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QMessageBox, QComboBox, QCheckBox, QGroupBox, QProgressBar,
    QTextEdit, QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from pydicom import dcmread
from core.deidentifier import DicomDeidentifier, TagAction
from utils.tag_translations import get_tag_name, is_patient_tag, is_private_tag, DEIDENTIFY_TAGS_TRANSLATION


class DeidentifyThread(QThread):
    """脱敏处理线程"""
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(dict)
    
    def __init__(self, deidentifier, input_path, output_path, is_folder=False):
        super().__init__()
        self.deidentifier = deidentifier
        self.input_path = input_path
        self.output_path = output_path
        self.is_folder = is_folder
    
    def run(self):
        if self.is_folder:
            result = self.deidentifier.deidentify_folder(self.input_path, self.output_path)
        else:
            result = self.deidentifier.deidentify_file(self.input_path, self.output_path)
        
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.deidentifier = DicomDeidentifier()
        self.current_file = None
        self.current_dataset = None
        self.output_folder = None
        self.language = "zh"  # 默认中文
        self.patient_tag_combos = {}  # 存储每个患者标签的下拉框
        self.config_table = None  # 配置页标签表格引用
        
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("DICOM脱敏工具")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        
        # 文件选择按钮
        self.btn_select_file = QPushButton("选择DICOM文件")
        self.btn_select_file.clicked.connect(self.select_file)
        toolbar_layout.addWidget(self.btn_select_file)
        
        self.btn_select_folder = QPushButton("选择文件夹")
        self.btn_select_folder.clicked.connect(self.select_folder)
        toolbar_layout.addWidget(self.btn_select_folder)
        
        # 输出文件夹选择
        self.btn_select_output = QPushButton("选择输出文件夹")
        self.btn_select_output.clicked.connect(self.select_output_folder)
        toolbar_layout.addWidget(self.btn_select_output)
        
        self.label_output = QLabel("未选择输出文件夹")
        toolbar_layout.addWidget(self.label_output)
        
        toolbar_layout.addStretch()
        
        # 语言切换
        self.combo_language = QComboBox()
        self.combo_language.addItems(["中文", "English"])
        self.combo_language.currentIndexChanged.connect(self.change_language)
        toolbar_layout.addWidget(QLabel("语言:"))
        toolbar_layout.addWidget(self.combo_language)
        
        main_layout.addLayout(toolbar_layout)
        
        # 当前文件信息
        self.label_current_file = QLabel("未选择文件")
        self.label_current_file.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0;")
        main_layout.addWidget(self.label_current_file)
        
        # 标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 标签查看页
        self.create_tag_viewer_tab()
        
        # 配置页
        self.create_config_tab()
        
        # 处理页
        self.create_process_tab()
        
        # 底部状态栏
        self.statusBar().showMessage("就绪")
    
    def create_tag_viewer_tab(self):
        """创建标签查看页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 过滤器
        filter_layout = QHBoxLayout()
        self.checkbox_show_patient = QCheckBox("显示患者信息标签(0010)")
        self.checkbox_show_patient.setChecked(True)
        self.checkbox_show_patient.stateChanged.connect(self.refresh_tag_view)
        filter_layout.addWidget(self.checkbox_show_patient)
        
        self.checkbox_show_private = QCheckBox("显示私有标签")
        self.checkbox_show_private.setChecked(True)
        self.checkbox_show_private.stateChanged.connect(self.refresh_tag_view)
        filter_layout.addWidget(self.checkbox_show_private)
        
        self.checkbox_show_other = QCheckBox("显示其他标签")
        self.checkbox_show_other.setChecked(False)
        self.checkbox_show_other.stateChanged.connect(self.refresh_tag_view)
        filter_layout.addWidget(self.checkbox_show_other)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 标签表格
        self.table_tags = QTableWidget()
        self.table_tags.setColumnCount(6)
        self.table_tags.setHorizontalHeaderLabels([
            "标签", "VR", "标签名称", "原始值", "脱敏后值", "操作"
        ])
        self.table_tags.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_tags.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_tags)
        
        self.tab_widget.addTab(tab, "标签查看")
    
    def create_config_tab(self):
        """创建配置页"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        
        # 脱敏标签配置 - 每个标签单独配置
        group_patient = QGroupBox("脱敏标签配置 - 每个标签单独设置")
        patient_layout = QVBoxLayout()
        
        # 创建表格显示所有脱敏标签
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["标签", "标签名称", "操作"])
        self.config_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.config_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.config_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        # 添加所有脱敏标签
        sorted_tags = sorted(DEIDENTIFY_TAGS_TRANSLATION.keys())
        self.config_table.setRowCount(len(sorted_tags))
        
        for row, tag_int in enumerate(sorted_tags):
            # 标签列
            tag_group = tag_int >> 16
            tag_elem = tag_int & 0xFFFF
            tag_str = f"({tag_group:04X},{tag_elem:04X})"
            self.config_table.setItem(row, 0, QTableWidgetItem(tag_str))
            
            # 标签名称列：根据当前语言显示
            tag_name = DEIDENTIFY_TAGS_TRANSLATION[tag_int].get(self.language, "")
            item = QTableWidgetItem(tag_name)
            item.setData(Qt.UserRole, tag_int)  # 存储tag_int便于刷新
            self.config_table.setItem(row, 1, item)
            
            # 操作下拉框
            combo = QComboBox()
            if self.language == "zh":
                combo.addItems(["匿名化", "删除"])
            else:
                combo.addItems(["Anonymize", "Delete"])
            combo.setCurrentIndex(0)
            combo.currentIndexChanged.connect(lambda idx, t=tag_int: self.update_single_tag_action(t, idx))
            self.config_table.setCellWidget(row, 2, combo)
            self.patient_tag_combos[tag_int] = combo
        
        patient_layout.addWidget(self.config_table)
        group_patient.setLayout(patient_layout)
        layout.addWidget(group_patient)
        
        # 私有标签配置
        group_private = QGroupBox("私有标签配置 - 统一设置")
        private_layout = QVBoxLayout()
        
        private_info = QLabel("私有标签是厂商自定义标签，默认操作: 删除")
        private_layout.addWidget(private_info)
        
        self.combo_private_action = QComboBox()
        self.combo_private_action.addItems(["删除", "匿名化"])
        self.combo_private_action.currentIndexChanged.connect(self.update_private_action)
        private_layout.addWidget(self.combo_private_action)
        
        group_private.setLayout(private_layout)
        layout.addWidget(group_private)
        
        # 说明
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setHtml("""
        <h4>脱敏规则说明：</h4>
        <ul>
            <li><b>匿名化：</b>保留标签，将数字变为0，其他字符变为*</li>
            <li><b>删除：</b>完全删除该标签</li>
        </ul>
        """)
        layout.addWidget(info_text)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "配置")
    
    def create_process_tab(self):
        """创建处理页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 处理按钮
        btn_layout = QHBoxLayout()
        self.btn_process = QPushButton("开始脱敏处理")
        self.btn_process.clicked.connect(self.start_deidentify)
        self.btn_process.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_layout.addWidget(self.btn_process)
        layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 处理日志
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        layout.addWidget(self.text_log)
        
        self.tab_widget.addTab(tab, "处理")
    
    def select_file(self):
        """选择DICOM文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择DICOM文件",
            "",
            "DICOM Files (*.dcm *.DCM);;All Files (*)"
        )
        
        if file_path:
            self.load_dicom_file(Path(file_path))
    
    def select_folder(self):
        """选择文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择DICOM文件夹"
        )
        
        if folder_path:
            self.current_file = Path(folder_path)
            self.label_current_file.setText(f"当前文件夹: {folder_path}")
            self.log_message(f"已选择文件夹: {folder_path}")
    
    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出文件夹"
        )
        
        if folder_path:
            self.output_folder = Path(folder_path)
            self.label_output.setText(f"输出: {folder_path}")
            self.log_message(f"输出文件夹: {folder_path}")
    
    def load_dicom_file(self, file_path: Path):
        """加载DICOM文件"""
        try:
            self.current_dataset = dcmread(str(file_path), force=True)
            self.current_file = file_path
            self.label_current_file.setText(f"当前文件: {file_path.name}")
            self.refresh_tag_view()
            self.log_message(f"成功加载文件: {file_path}")
            self.tab_widget.setCurrentIndex(0)  # 切换到标签查看页
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取DICOM文件: {str(e)}")
            self.log_message(f"加载失败: {str(e)}", error=True)
    
    def refresh_tag_view(self):
        """刷新标签视图"""
        if self.current_dataset is None:
            return
        
        self.table_tags.setRowCount(0)
        
        show_patient = self.checkbox_show_patient.isChecked()
        show_private = self.checkbox_show_private.isChecked()
        show_other = self.checkbox_show_other.isChecked()
        
        row = 0
        for elem in self.current_dataset:
            tag_int = int(elem.tag)
            
            # 过滤
            is_patient = is_patient_tag(tag_int)
            is_priv = is_private_tag(tag_int)
            
            if is_patient and not show_patient:
                continue
            if is_priv and not show_private:
                continue
            if not is_patient and not is_priv and not show_other:
                continue
            
            self.table_tags.insertRow(row)
            
            # 标签
            tag_str = f"({elem.tag.group:04X},{elem.tag.element:04X})"
            self.table_tags.setItem(row, 0, QTableWidgetItem(tag_str))
            
            # VR
            self.table_tags.setItem(row, 1, QTableWidgetItem(elem.VR))
            
            # 标签名称
            tag_name = get_tag_name(tag_int, self.language)
            self.table_tags.setItem(row, 2, QTableWidgetItem(tag_name))
            
            # 原始值
            value_str = str(elem.value)[:100] if elem.value is not None else ""
            self.table_tags.setItem(row, 3, QTableWidgetItem(value_str))
            
            # 脱敏后值
            action = self.deidentifier.get_action(tag_int)
            if action == TagAction.DELETE:
                deidentified_value = "[删除]"
            elif action == TagAction.ANONYMIZE:
                deidentified_value = self.deidentifier.anonymize_value(value_str)
            else:
                deidentified_value = value_str
            
            self.table_tags.setItem(row, 4, QTableWidgetItem(deidentified_value))
            
            # 操作
            action_text = "删除" if action == TagAction.DELETE else ("匿名化" if action == TagAction.ANONYMIZE else "无操作")
            self.table_tags.setItem(row, 5, QTableWidgetItem(action_text))
            
            row += 1
    
    def update_single_tag_action(self, tag_int, index):
        """更新单个患者标签的操作"""
        action = TagAction.ANONYMIZE if index == 0 else TagAction.DELETE
        self.deidentifier.set_action(tag_int, action)
        self.refresh_tag_view()
        tag_name = get_tag_name(tag_int, self.language)
        self.log_message(f"标签 {tag_name} 操作已更新为: {'匿名化' if index == 0 else '删除'}")
    
    def update_private_action(self, index):
        """更新私有标签操作"""
        action = TagAction.DELETE if index == 0 else TagAction.ANONYMIZE
        self.deidentifier.set_action_for_private_tags(action)
        self.refresh_tag_view()
        self.log_message(f"私有标签操作已更新为: {'删除' if index == 0 else '匿名化'}")
    
    def change_language(self, index):
        """切换语言"""
        self.language = "zh" if index == 0 else "en"
        self.refresh_tag_view()
        self.refresh_config_table()
        self.log_message(f"语言已切换为: {'中文' if index == 0 else 'English'}")
    
    def refresh_config_table(self):
        """刷新配置表格的标签名称和操作下拉框文本"""
        if self.config_table is None:
            return
        
        for row in range(self.config_table.rowCount()):
            # 更新标签名称列
            name_item = self.config_table.item(row, 1)
            if name_item:
                tag_int = name_item.data(Qt.UserRole)
                if tag_int in DEIDENTIFY_TAGS_TRANSLATION:
                    tag_name = DEIDENTIFY_TAGS_TRANSLATION[tag_int].get(self.language, "")
                    name_item.setText(tag_name)
            
            # 更新操作下拉框的文本
            combo = self.config_table.cellWidget(row, 2)
            if combo and isinstance(combo, QComboBox):
                current_idx = combo.currentIndex()
                combo.blockSignals(True)
                combo.clear()
                if self.language == "zh":
                    combo.addItems(["匿名化", "删除"])
                else:
                    combo.addItems(["Anonymize", "Delete"])
                combo.setCurrentIndex(current_idx)
                combo.blockSignals(False)
    
    def start_deidentify(self):
        """开始脱敏处理"""
        if self.current_file is None:
            QMessageBox.warning(self, "警告", "请先选择要处理的文件或文件夹")
            return
        
        if self.output_folder is None:
            QMessageBox.warning(self, "警告", "请先选择输出文件夹")
            return
        
        # 切换到处理页
        self.tab_widget.setCurrentIndex(2)
        
        # 确定是文件还是文件夹
        is_folder = self.current_file.is_dir()
        
        if is_folder:
            output_path = self.output_folder / f"{self.current_file.name}_deidentified"
        else:
            output_path = self.output_folder / f"{self.current_file.stem}_deidentified{self.current_file.suffix}"
        
        self.log_message(f"开始处理: {self.current_file}")
        self.log_message(f"输出到: {output_path}")
        
        # 禁用按钮
        self.btn_process.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # 启动线程
        self.thread = DeidentifyThread(
            self.deidentifier,
            self.current_file,
            output_path,
            is_folder
        )
        self.thread.finished.connect(self.on_deidentify_finished)
        self.thread.start()
    
    def on_deidentify_finished(self, result):
        """脱敏完成"""
        self.btn_process.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if isinstance(result, dict) and "total" in result:
            # 文件夹处理结果
            self.log_message(f"\n处理完成!")
            self.log_message(f"总文件数: {result['total']}")
            self.log_message(f"成功: {result['success']}")
            self.log_message(f"失败: {result['failed']}")
            
            QMessageBox.information(
                self,
                "完成",
                f"处理完成!\n总文件数: {result['total']}\n成功: {result['success']}\n失败: {result['failed']}"
            )
        else:
            # 单文件处理结果
            if result.get("success"):
                self.log_message(f"\n{result['message']}")
                
                QMessageBox.information(
                    self, 
                    "完成", 
                    result['message']
                )
            else:
                self.log_message(f"\n错误: {result['message']}", error=True)
                QMessageBox.critical(self, "错误", result['message'])
    
    def log_message(self, message: str, error: bool = False):
        """添加日志消息"""
        if error:
            self.text_log.append(f'<span style="color: red;">{message}</span>')
        else:
            self.text_log.append(message)
        self.statusBar().showMessage(message)
