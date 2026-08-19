"""
DICOM脱敏核心逻辑
只脱敏0010组标签和厂商私有标签
"""
import re
from pathlib import Path
from typing import Optional, Dict, List
from pydicom import dcmread
from pydicom.dataset import Dataset
from pydicom.tag import Tag
from pydicom.sequence import Sequence


class TagAction:
    """标签操作类型"""
    DELETE = "delete"  # 删除标签
    ANONYMIZE = "anonymize"  # 匿名化标签


class DicomDeidentifier:
    """DICOM脱敏处理器"""
    
    def __init__(self):
        # 默认配置：患者信息标签默认匿名化
        self.tag_actions = {}
        self._set_default_actions()
    
    def _set_default_actions(self):
        """设置默认操作"""
        # 0010组所有标签默认匿名化
        self.set_action_for_group(0x0010, TagAction.ANONYMIZE)
        # 私有标签默认删除
        self.set_action_for_private_tags(TagAction.DELETE)
    
    def set_action(self, tag: int, action: str):
        """
        设置单个标签的操作
        """
        self.tag_actions[tag] = action
    
    def set_action_for_group(self, group: int, action: str):
        """
        设置整个组的操作
        """
        self.tag_actions[f"group_{group:04X}"] = action
    
    def set_action_for_private_tags(self, action: str):
        """
        设置私有标签的操作
        """
        self.tag_actions["private_tags"] = action
    
    def get_action(self, tag: int) -> Optional[str]:
        """
        获取标签的操作类型
        """
        # 先检查是否有具体标签的配置
        if tag in self.tag_actions:
            return self.tag_actions[tag]
        
        # 检查是否为0010组
        group = tag >> 16
        if group == 0x0010:
            group_key = f"group_{group:04X}"
            if group_key in self.tag_actions:
                return self.tag_actions[group_key]
        
        # 检查是否为私有标签
        if self._is_private_tag(tag):
            if "private_tags" in self.tag_actions:
                return self.tag_actions["private_tags"]
        
        return None
    
    @staticmethod
    def _is_private_tag(tag: int) -> bool:
        """判断是否为私有标签"""
        group = tag >> 16
        return (group % 2) == 1
    
    @staticmethod
    def _is_patient_group_tag(tag: int) -> bool:
        """判断是否为0010组标签"""
        group = tag >> 16
        return group == 0x0010
    
    def should_process_tag(self, tag: int) -> bool:
        """
        判断标签是否需要处理
        """
        return self._is_patient_group_tag(tag) or self._is_private_tag(tag)
    
    @staticmethod
    def anonymize_value(value: str) -> str:
        """
        匿名化值：数字变0，其他字符变*
        """
        if not value:
            return ""
        
        result = []
        for char in str(value):
            if char.isdigit():
                result.append('0')
            elif char.isspace():
                result.append(char)  # 保留空格
            else:
                result.append('*')
        
        return ''.join(result)
    
    def process_dataset(self, dataset: Dataset, recursive: bool = True) -> int:
        """
        处理数据集
        """
        processed_count = 0
        tags_to_delete = []
        
        for elem in dataset:
            tag_int = int(elem.tag)
            
            # 只处理0010组和私有标签
            if not self.should_process_tag(tag_int):
                continue
            
            action = self.get_action(tag_int)
            
            if action == TagAction.DELETE:
                tags_to_delete.append(elem.tag)
                processed_count += 1
            elif action == TagAction.ANONYMIZE:
                # 匿名化处理
                if elem.VR == "SQ" and isinstance(elem.value, Sequence):
                    # 序列类型，递归处理
                    if recursive:
                        for item in elem.value:
                            if isinstance(item, Dataset):
                                processed_count += self.process_dataset(item, recursive=True)
                else:
                    # 普通值类型 - 使用简单匿名化
                    original_value = str(elem.value) if elem.value is not None else ""
                    anonymized_value = self.anonymize_value(original_value)
                    
                    # 处理数字类型的VR，避免类型转换错误
                    numeric_vrs = ['DS', 'IS', 'FL', 'FD', 'SL', 'SS', 'UL', 'US']
                    if elem.VR in numeric_vrs:
                        # 数字类型标签：设置为0或空值
                        if elem.VR in ['DS', 'IS']:
                            elem.value = '0'
                        elif elem.VR in ['FL', 'FD']:
                            elem.value = 0.0
                        else:  # SL, SS, UL, US
                            elem.value = 0
                    else:
                        # 文本类型标签：使用匿名化值
                        elem.value = anonymized_value
                    
                    processed_count += 1
        
        # 删除标记的标签
        for tag in tags_to_delete:
            del dataset[tag]
        
        return processed_count
    
    def deidentify_file(self, input_path: Path, output_path: Path) -> dict:
        """
        脱敏DICOM文件
        """
        try:
            # 读取DICOM文件
            dataset = dcmread(str(input_path), force=True)
            
            # 处理数据集
            processed_count = self.process_dataset(dataset, recursive=True)
            
            # 添加脱敏标记
            dataset.PatientIdentityRemoved = "YES"
            dataset.DeidentificationMethod = "DICOM Deidentify Tool"
            
            # 保存文件
            output_path.parent.mkdir(parents=True, exist_ok=True)
            dataset.save_as(str(output_path), write_like_original=False)
            
            return {
                "success": True,
                "processed_count": processed_count,
                "message": f"成功处理 {processed_count} 个标签",
                "output_path": str(output_path)
            }
        
        except Exception as e:
            return {
                "success": False,
                "processed_count": 0,
                "message": f"处理失败: {str(e)}",
                "output_path": None
            }
    
    def deidentify_folder(self, input_folder: Path, output_folder: Path) -> dict:
        """
        批量脱敏文件夹中的DICOM文件
        """
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "details": [],
            "output_folder": str(output_folder)
        }
        
        # 查找所有DICOM文件
        dicom_files = list(input_folder.rglob("*.dcm")) + list(input_folder.rglob("*.DCM"))
        
        # 也尝试没有扩展名的文件
        for file in input_folder.rglob("*"):
            if file.is_file() and not file.suffix:
                try:
                    dcmread(str(file), stop_before_pixels=True)
                    dicom_files.append(file)
                except:
                    pass
        
        results["total"] = len(dicom_files)
        
        for dicom_file in dicom_files:
            # 计算相对路径
            rel_path = dicom_file.relative_to(input_folder)
            output_path = output_folder / rel_path
            
            # 处理文件
            result = self.deidentify_file(dicom_file, output_path)
            
            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "file": str(rel_path),
                "success": result["success"],
                "message": result["message"]
            })
        
        return results
    
    def get_tag_info(self, dataset: Dataset, tag: int) -> dict:
        """
        获取标签信息
        
        """
        tag_obj = Tag(tag)
        
        if tag_obj not in dataset:
            return {
                "exists": False,
                "tag": f"({tag_obj.group:04X},{tag_obj.element:04X})",
                "vr": "",
                "value": "",
                "action": self.get_action(tag)
            }
        
        elem = dataset[tag_obj]
        value = str(elem.value) if elem.value is not None else ""
        
        action = self.get_action(tag)
        will_be_anonymized = None
        if action == TagAction.ANONYMIZE:
            will_be_anonymized = self.anonymize_value(value)
        
        return {
            "exists": True,
            "tag": f"({tag_obj.group:04X},{tag_obj.element:04X})",
            "vr": elem.VR,
            "value": value,
            "action": action,
            "will_be_anonymized": will_be_anonymized
        }


# 创建全局实例
deidentifier = DicomDeidentifier()
