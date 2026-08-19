"""
DICOM标签的中英文翻译
"""

from pydicom.datadict import keyword_for_tag, tag_for_keyword

# 脱敏标签配置 - 根据脱敏标签.md
DEIDENTIFY_TAGS_TRANSLATION = {
    # 0008组标签
    0x00080050: {"en": "Accession Number", "zh": "检查号"},
    0x00080080: {"en": "Institution Name", "zh": "机构名称"},
    0x00080081: {"en": "Institution Address", "zh": "机构地址"},
    0x00080090: {"en": "Referring Physician's Name", "zh": "转诊医生姓名"},
    0x00081010: {"en": "Station Name", "zh": "工作站名称"},
    0x00081030: {"en": "Study Description", "zh": "检查描述"},
    0x0008103E: {"en": "Series Description", "zh": "序列描述"},
    0x00081040: {"en": "Institutional Department Name", "zh": "机构部门名称"},
    0x00081048: {"en": "Physician(s) of Record", "zh": "主管医生"},
    0x00081050: {"en": "Performing Physician's Name", "zh": "执行检查医生姓名"},
    0x00081060: {"en": "Name of Physician(s) Reading Study", "zh": "阅片医生姓名"},
    0x00081070: {"en": "Operators' Name", "zh": "操作者姓名"},
    0x00081090: {"en": "Manufacturer's Model Name", "zh": "制造商型号名称"},
    
    # 0010组标签 - 患者信息
    0x00100010: {"en": "Patient's Name", "zh": "患者姓名"},
    0x00100020: {"en": "Patient ID", "zh": "患者ID"},
    0x00100021: {"en": "Issuer of Patient ID", "zh": "患者ID发放机构"},
    0x00100022: {"en": "Type of Patient ID", "zh": "患者ID类型"},
    0x00100024: {"en": "Issuer of Patient ID Qualifiers Sequence", "zh": "患者ID发放机构限定符序列"},
    0x00100030: {"en": "Patient's Birth Date", "zh": "患者出生日期"},
    0x00100032: {"en": "Patient's Birth Time", "zh": "患者出生时间"},
    0x00100040: {"en": "Patient's Sex", "zh": "患者性别"},
    0x00100050: {"en": "Patient's Insurance Plan Code Sequence", "zh": "患者保险计划代码序列"},
    0x00101000: {"en": "Other Patient IDs", "zh": "其他患者ID"},
    0x00101001: {"en": "Other Patient Names", "zh": "其他患者姓名"},
    0x00101002: {"en": "Other Patient IDs Sequence", "zh": "其他患者ID序列"},
    0x00101005: {"en": "Patient's Birth Name", "zh": "患者出生姓名"},
    0x00101010: {"en": "Patient's Age", "zh": "患者年龄"},
    0x00101020: {"en": "Patient's Size", "zh": "患者身高/体型"},
    0x00101030: {"en": "Patient's Weight", "zh": "患者体重"},
    0x00101040: {"en": "Patient's Address", "zh": "患者地址"},
    0x00101060: {"en": "Patient's Mother's Birth Name", "zh": "患者母亲出生姓名"},
    0x00101080: {"en": "Military Rank", "zh": "军衔"},
    0x00101081: {"en": "Branch of Service", "zh": "服役军种"},
    0x00102110: {"en": "Allergies", "zh": "过敏"},
    0x00102150: {"en": "Country of Residence", "zh": "居住国家"},
    0x00102152: {"en": "Region of Residence", "zh": "居住地区"},
    0x00102154: {"en": "Patient's Telephone Numbers", "zh": "患者电话号码"},
    0x00102155: {"en": "Patient's Telecom Information", "zh": "患者电信信息"},
    0x00102160: {"en": "Ethnic Group", "zh": "种族/民族"},
    0x00102180: {"en": "Occupation", "zh": "职业"},
    0x001021A0: {"en": "Smoking Status", "zh": "吸烟状况"},
    0x001021B0: {"en": "Additional Patient History", "zh": "附加患者病史"},
    0x001021C0: {"en": "Pregnancy Status", "zh": "怀孕状况"},
    0x001021D0: {"en": "Last Menstrual Date", "zh": "末次月经日期"},
    0x001021F0: {"en": "Patient's Religious Preference", "zh": "患者宗教偏好"},
    
    # 0018组标签
    0x00181000: {"en": "Device Serial Number", "zh": "设备序列号"},
    0x00181020: {"en": "Software Versions", "zh": "软件版本"},
    0x00181030: {"en": "Protocol Name", "zh": "协议名称"},
    0x00181050: {"en": "Spatial Resolution", "zh": "空间分辨率"},
    
    # 0020组标签
    0x00200010: {"en": "Study ID", "zh": "检查ID"},
    
    # 0032组标签
    0x00321032: {"en": "Requesting Physician", "zh": "申请医生"},
    0x00321033: {"en": "Requesting Service", "zh": "申请科室/服务"},
    0x00321060: {"en": "Requested Procedure Description", "zh": "申请操作描述"},
    0x00321070: {"en": "Requested Contrast Agent", "zh": "请求使用的对比剂"},
    
    # 0040组标签
    0x00400254: {"en": "Performed Procedure Step Description", "zh": "已执行操作步骤描述"},
}

# 为了兼容性，保留患者标签的引用
PATIENT_TAGS_TRANSLATION = {k: v for k, v in DEIDENTIFY_TAGS_TRANSLATION.items() if (k >> 16) == 0x0010}

# 其他常用标签翻译
COMMON_TAGS_TRANSLATION = {
    0x00080018: {"en": "SOP Instance UID", "zh": "SOP实例UID"},
    0x00080020: {"en": "Study Date", "zh": "检查日期"},
    0x00080030: {"en": "Study Time", "zh": "检查时间"},
    0x00080060: {"en": "Modality", "zh": "成像模式"},
    0x00080070: {"en": "Manufacturer", "zh": "制造商"},
    0x0020000D: {"en": "Study Instance UID", "zh": "检查实例UID"},
    0x0020000E: {"en": "Series Instance UID", "zh": "序列实例UID"},
    0x00200011: {"en": "Series Number", "zh": "序列号"},
    0x00200013: {"en": "Instance Number", "zh": "实例号"},
}

# 合并所有翻译
ALL_TAGS_TRANSLATION = {**DEIDENTIFY_TAGS_TRANSLATION, **COMMON_TAGS_TRANSLATION}


def get_tag_name(tag_int: int, language: str = "en") -> str:
    """
    获取标签名称 - 确保所有标签都能显示具体名称
    
    Args:
        tag_int: 标签的整数值
        language: 语言 ('en' 或 'zh')
    
    Returns:
        标签名称，优先返回中英文翻译，其次返回pydicom标准名称
    """
    # 首先检查自定义翻译字典（包含中文翻译）
    if tag_int in ALL_TAGS_TRANSLATION:
        return ALL_TAGS_TRANSLATION[tag_int].get(language, ALL_TAGS_TRANSLATION[tag_int]["en"])
    
    # 使用 pydicom 的标签字典获取标准 DICOM 标签名称
    try:
        # 将整数转换为标签格式 (group, element)
        group = (tag_int >> 16) & 0xFFFF
        element = tag_int & 0xFFFF
        
        # 获取标签的关键字（英文名称）
        keyword = keyword_for_tag((group, element))
        
        if keyword and keyword != "":
            # 将驼峰命名转换为可读格式
            # 例如: PatientName -> Patient Name
            # 例如: TableFeedPerRotation -> Table Feed Per Rotation
            readable_name = ""
            for i, char in enumerate(keyword):
                # 在大写字母前添加空格（除了首字母）
                if i > 0 and char.isupper():
                    # 检查前一个字符是否为小写字母或者下一个字符是否为小写字母
                    if keyword[i-1].islower() or (i < len(keyword) - 1 and keyword[i+1].islower()):
                        readable_name += " "
                readable_name += char
            
            return readable_name.strip()
    except Exception as e:
        pass
    
    # 对于私有标签或未知标签，返回描述性名称
    group = (tag_int >> 16) & 0xFFFF
    element = tag_int & 0xFFFF
    
    # 判断是否为私有标签（组号为奇数）
    if group % 2 == 1:
        if language == "zh":
            return f"私有标签 ({group:04X},{element:04X})"
        else:
            return f"Private Tag ({group:04X},{element:04X})"
    
    # 其他未知的标准标签
    if language == "zh":
        return f"未知标签 ({group:04X},{element:04X})"
    else:
        return f"Unknown Tag ({group:04X},{element:04X})"


def is_patient_tag(tag_int: int) -> bool:
    """
    判断是否为患者信息标签 (0010,xxxx)
    
    Args:
        tag_int: 标签的整数值
    
    Returns:
        是否为患者信息标签
    """
    return (tag_int >> 16) == 0x0010


def is_private_tag(tag_int: int) -> bool:
    """
    判断是否为私有标签
    
    Args:
        tag_int: 标签的整数值
    
    Returns:
        是否为私有标签
    """
    group = tag_int >> 16
    element = tag_int & 0xFFFF
    return (group % 2) == 1 or (element >= 0x0010 and (group % 2) == 1)
