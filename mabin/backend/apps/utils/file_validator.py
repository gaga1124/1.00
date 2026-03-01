"""
文件上传验证工具
用于验证文件类型、大小等，防止恶意文件上传
"""
import os
from django.conf import settings
from django.core.exceptions import ValidationError
import magic


def validate_file(file, allowed_extensions=None, allowed_mime_types=None, max_size=None):
    """
    验证上传文件
    
    Args:
        file: Django UploadedFile 对象
        allowed_extensions: 允许的文件扩展名列表，如 ['.pdf', '.jpg']
        allowed_mime_types: 允许的MIME类型列表
        max_size: 最大文件大小（字节），如 10 * 1024 * 1024 (10MB)
    
    Returns:
        bool: 验证通过返回True
    
    Raises:
        ValidationError: 验证失败时抛出异常
    """
    if allowed_extensions is None:
        allowed_extensions = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', [])
    
    if allowed_mime_types is None:
        allowed_mime_types = getattr(settings, 'ALLOWED_MIME_TYPES', [])
    
    if max_size is None:
        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
    
    # 检查文件大小
    if file.size > max_size:
        raise ValidationError(f'文件大小超过限制（最大 {max_size / 1024 / 1024:.1f}MB）')
    
    # 检查文件扩展名
    file_ext = os.path.splitext(file.name)[1].lower()
    if allowed_extensions and file_ext not in allowed_extensions:
        raise ValidationError(f'不允许的文件类型：{file_ext}')
    
    # 检查MIME类型
    try:
        # 读取文件内容的前1024字节进行MIME类型检测
        file.seek(0)
        file_content = file.read(1024)
        file.seek(0)  # 重置文件指针
        
        mime_type = magic.Magic(mime=True).from_buffer(file_content)
        
        if allowed_mime_types and mime_type not in allowed_mime_types:
            raise ValidationError(f'不允许的MIME类型：{mime_type}')
    except Exception as e:
        # 如果magic库不可用，跳过MIME检查
        pass
    
    return True
