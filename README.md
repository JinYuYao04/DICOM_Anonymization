# DICOM Anonymization Tool

DICOM 医学影像脱敏工具，用于对 DICOM 文件进行去标识化处理。

## 主要功能

- **批量处理**：支持单个文件或整个文件夹的批量脱敏
- **自定义规则**：可配置每个标签的处理方式（匿名化或删除）
- **标签查看**：查看脱敏前后的标签对比
- **双语支持**：界面支持中英文切换
- **0010组标签**：自动处理所有患者信息相关标签
- **私有标签**：支持厂商私有标签的脱敏处理
- 
## 使用
```bash
cd dicom_deidentify_tool
pip install -r requirements.txt
python main.py
```



