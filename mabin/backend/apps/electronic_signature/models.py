"""
电子签章模块模型
包含文件、签章、操作日志等核心模型
"""

import os
import uuid
import hashlib
from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings

User = get_user_model()


def electronic_file_path(instance, filename):
    """生成电子文件上传路径"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('electronic_signature/files/', filename)


def signature_image_path(instance, filename):
    """生成签章图片存储路径"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('electronic_signature/signatures/', filename)


class DepartmentSignature(models.Model):
    """部门签章模型"""
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.CASCADE,
        related_name='signatures',
        verbose_name='所属部门'
    )
    name = models.CharField('签章名称', max_length=100)
    signature_image = models.ImageField('签章图片', upload_to=signature_image_path)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'department_signatures'
        verbose_name = '部门签章'
        verbose_name_plural = '部门签章'
        unique_together = ['department']  # 每个部门只能有一个签章
    
    def __str__(self):
        return f"{self.department.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        # 确保每个部门只有一个签章
        if not self.pk:
            existing = DepartmentSignature.objects.filter(department=self.department).first()
            if existing:
                existing.is_active = False
                existing.save()
        super().save(*args, **kwargs)


class ElectronicFile(models.Model):
    """电子文件模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('signed', '已签章'),
        ('sent', '已发送'),
        ('revoked', '已撤回'),
    ]
    
    FILE_TYPE_CHOICES = [
        ('document', '文档'),
        ('image', '图片'),
        ('pdf', 'PDF'),
        ('other', '其他'),
    ]
    
    title = models.CharField('文件标题', max_length=255)
    description = models.TextField('文件描述', blank=True)
    file = models.FileField('文件', upload_to=electronic_file_path)
    file_name = models.CharField('原始文件名', max_length=255)
    file_size = models.PositiveIntegerField('文件大小', default=0)
    file_type = models.CharField('文件类型', max_length=20, choices=FILE_TYPE_CHOICES, default='other')
    content_type = models.CharField('MIME类型', max_length=100, blank=True)
    
    # 部门信息
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.CASCADE,
        related_name='electronic_files',
        verbose_name='所属部门'
    )
    
    # 签章信息
    signature = models.ForeignKey(
        DepartmentSignature,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_files',
        verbose_name='使用的签章'
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_files',
        verbose_name='签章人'
    )
    signed_at = models.DateTimeField('签章时间', null=True, blank=True)
    signature_hash = models.CharField('签章哈希值', max_length=256, blank=True)  # 用于防篡改
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'electronic_files'
        verbose_name = '电子文件'
        verbose_name_plural = '电子文件'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # 保存文件大小和类型
        if self.file:
            self.file_size = self.file.size
            if not self.file_name:
                self.file_name = self.file.name
            if not self.content_type:
                # 从文件对象获取content type
                from django.core.files.images import ImageFile
                if isinstance(self.file, ImageFile):
                    self.content_type = 'image/' + self.file.name.split('.')[-1]
                else:
                    # 尝试从文件名推断
                    ext = self.file.name.split('.')[-1].lower()
                    content_type_map = {
                        'pdf': 'application/pdf',
                        'doc': 'application/msword',
                        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'xls': 'application/vnd.ms-excel',
                        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        'ppt': 'application/vnd.ms-powerpoint',
                        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                        'txt': 'text/plain',
                        'png': 'image/png',
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'gif': 'image/gif',
                    }
                    self.content_type = content_type_map.get(ext, 'application/octet-stream')
        super().save(*args, **kwargs)
    
    def calculate_file_hash(self):
        """计算文件哈希值"""
        if not self.file:
            return None
        
        hasher = hashlib.sha256()
        with default_storage.open(self.file.name, 'rb') as f:
            for chunk in f.chunks():
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def generate_signature_hash(self):
        """生成签章哈希值（文件内容 + 部门信息 + 时间戳）"""
        if not self.file or not self.signature or not self.signed_at:
            return None
        
        # 计算文件哈希
        file_hash = self.calculate_file_hash()
        if not file_hash:
            return None
        
        # 构建哈希内容
        hash_content = f"{file_hash}:{self.department.id}:{self.signature.id}:{self.signer.id}:{self.signed_at.isoformat()}"
        hasher = hashlib.sha256()
        hasher.update(hash_content.encode('utf-8'))
        return hasher.hexdigest()
    
    def sign(self, signature, signer):
        """签章操作"""
        self.signature = signature
        self.signer = signer
        self.signed_at = timezone.now()
        self.status = 'signed'
        self.signature_hash = self.generate_signature_hash()
        self.save()
    
    def verify_signature(self):
        """验证签章真伪"""
        if not self.signature_hash:
            return False, '文件未签章'
        
        # 重新计算哈希值
        current_hash = self.generate_signature_hash()
        if current_hash != self.signature_hash:
            return False, '文件已被篡改'
        
        # 检查签章是否存在且有效
        if not self.signature or not self.signature.is_active:
            return False, '签章无效或已被禁用'
        
        # 检查签章人是否有权限
        if not self.signer:
            return False, '签章人信息缺失'
        
        # 检查部门权限
        from apps.rbac.models import UserDepartment
        user_dept = UserDepartment.objects.filter(
            user=self.signer,
            department=self.department
        ).first()
        if not user_dept:
            return False, '签章人无此部门权限'
        
        return True, '签章有效，文件未被篡改'
    
    @property
    def file_size_display(self):
        """格式化文件大小显示"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"


class FileRecipient(models.Model):
    """文件接收人模型"""
    file = models.ForeignKey(
        ElectronicFile,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='文件'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_files',
        verbose_name='接收人'
    )
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'file_recipients'
        verbose_name = '文件接收人'
        verbose_name_plural = '文件接收人'
        unique_together = ['file', 'recipient']  # 每个文件对每个用户只记录一次
    
    def __str__(self):
        return f"{self.recipient} - {self.file.title}"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class SignatureOperationLog(models.Model):
    """签章操作日志模型"""
    OPERATION_CHOICES = [
        ('upload', '上传文件'),
        ('sign', '签章'),
        ('send', '发送文件'),
        ('view', '查看文件'),
        ('verify', '验签'),
        ('revoke', '撤回文件'),
        ('delete', '删除文件'),
        ('download', '下载文件'),
    ]
    
    operation = models.CharField('操作类型', max_length=20, choices=OPERATION_CHOICES)
    file = models.ForeignKey(
        ElectronicFile,
        on_delete=models.CASCADE,
        related_name='operation_logs',
        verbose_name='文件',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signature_logs',
        verbose_name='操作用户'
    )
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.CASCADE,
        related_name='signature_logs',
        verbose_name='操作部门'
    )
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    details = models.JSONField('详细信息', default=dict, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        db_table = 'signature_operation_logs'
        verbose_name = '签章操作日志'
        verbose_name_plural = '签章操作日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['operation', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['department', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_operation_display()} - {self.created_at}"
