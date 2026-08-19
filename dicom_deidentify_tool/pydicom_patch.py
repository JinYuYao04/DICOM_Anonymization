"""
PyInstaller 打包时的 pydicom 补丁模块
用于替代被排除的 pydicom.data 和 pydicom.examples 模块
"""

def get_palette_files(*args, **kwargs):
    """返回空列表，避免导入错误"""
    return []

def get_testdata_file(*args, **kwargs):
    """返回 None，避免导入错误"""
    return None

def get_testdata_files(*args, **kwargs):
    """返回空列表，避免导入错误"""
    return []

# 其他可能需要的函数
__all__ = ['get_palette_files', 'get_testdata_file', 'get_testdata_files']
