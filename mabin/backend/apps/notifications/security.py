"""
通知模块安全工具
包含频率限制、内容安全检查、敏感词过滤等功能
"""

import re
import hashlib
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


class RateLimiter:
    """频率限制器"""
    
    # 限制配置 (次数, 时间窗口秒数)
    LIMITS = {
        'send_notification': (10, 60),      # 发送通知：60秒内最多10次
        'create_draft': (30, 60),            # 创建草稿：60秒内最多30次
        'upload_attachment': (20, 60),       # 上传附件：60秒内最多20次
        'mark_as_read': (100, 60),           # 标记已读：60秒内最多100次
        'batch_operation': (5, 60),          # 批量操作：60秒内最多5次
    }
    
    @classmethod
    def get_key(cls, action, user_id):
        """生成缓存key"""
        return f"notification_rate_limit:{action}:{user_id}"
    
    @classmethod
    def check(cls, action, user_id):
        """
        检查是否超过频率限制
        返回: (是否允许, 剩余次数, 重置时间)
        """
        if action not in cls.LIMITS:
            return True, None, None
        
        max_count, window = cls.LIMITS[action]
        key = cls.get_key(action, user_id)
        
        # 获取当前计数
        data = cache.get(key)
        if data is None:
            # 首次请求
            cache.set(key, {'count': 1, 'reset_time': timezone.now() + timedelta(seconds=window)}, window)
            return True, max_count - 1, window
        
        count = data['count']
        reset_time = data['reset_time']
        
        if count >= max_count:
            # 超过限制
            remaining = int((reset_time - timezone.now()).total_seconds())
            return False, 0, max(0, remaining)
        
        # 增加计数
        data['count'] += 1
        cache.set(key, data, window)
        
        remaining = max_count - data['count']
        remaining_time = int((reset_time - timezone.now()).total_seconds())
        
        return True, remaining, remaining_time
    
    @classmethod
    def get_limit_response(cls, action, reset_seconds):
        """获取限制响应"""
        messages = {
            'send_notification': f'发送通知过于频繁，请{reset_seconds}秒后再试',
            'create_draft': f'创建草稿过于频繁，请{reset_seconds}秒后再试',
            'upload_attachment': f'上传附件过于频繁，请{reset_seconds}秒后再试',
            'mark_as_read': f'操作过于频繁，请{reset_seconds}秒后再试',
            'batch_operation': f'批量操作过于频繁，请{reset_seconds}秒后再试',
        }
        return Response(
            {'error': messages.get(action, '操作过于频繁'), 'retry_after': reset_seconds},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )


class ContentSecurityChecker:
    """内容安全检查器"""
    
    # 敏感词列表（实际应用中应该从数据库或配置文件加载）
    SENSITIVE_WORDS = [
        # 政治敏感
        '反动', '颠覆', '暴乱', '游行', '示威',
        # 暴力恐怖
        '恐怖', '爆炸', '炸弹', '枪支', '暴力',
        # 色情低俗
        '色情', '淫秽', '低俗', '赌博', '毒品',
        # 诈骗相关
        '诈骗', '传销', '洗钱', '假币', '套现',
        # 其他违规
        '黑客', '攻击', '病毒', '木马', '钓鱼',
    ]
    
    # 允许的文件类型
    ALLOWED_FILE_TYPES = {
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'],
        'document': [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
        ],
        'archive': ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'],
    }
    
    # 文件扩展名白名单
    ALLOWED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
        '.zip', '.rar', '.7z',
    }
    
    # 最大文件大小 (MB)
    MAX_FILE_SIZE = 50
    
    @classmethod
    def check_sensitive_words(cls, content):
        """
        检查敏感词
        返回: (是否通过, 发现的敏感词列表)
        """
        if not content:
            return True, []
        
        found_words = []
        content_lower = content.lower()
        
        for word in cls.SENSITIVE_WORDS:
            if word in content_lower:
                found_words.append(word)
        
        # 也检查拼音（简单实现）
        # 实际应用中可以使用更复杂的算法
        
        return len(found_words) == 0, found_words
    
    @classmethod
    def sanitize_content(cls, content):
        """
        清理内容中的危险标签和脚本
        """
        if not content:
            return content
        
        # 移除危险标签
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
        for tag in dangerous_tags:
            # 移除开始标签
            content = re.sub(f'<{tag}[^>]*>', '', content, flags=re.IGNORECASE)
            # 移除结束标签
            content = re.sub(f'</{tag}>', '', content, flags=re.IGNORECASE)
        
        # 移除事件处理器
        content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # 移除javascript:伪协议
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        return content
    
    @classmethod
    def check_file_type(cls, file):
        """
        检查文件类型是否允许
        """
        if not file:
            return False, '文件不存在'
        
        # 检查文件扩展名
        import os
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            return False, f'不支持的文件类型: {ext}'
        
        # 检查MIME类型
        content_type = file.content_type
        all_allowed_types = []
        for types in cls.ALLOWED_FILE_TYPES.values():
            all_allowed_types.extend(types)
        
        if content_type not in all_allowed_types:
            return False, f'不支持的文件格式: {content_type}'
        
        return True, None
    
    @classmethod
    def check_file_size(cls, file):
        """
        检查文件大小
        """
        if not file:
            return False, '文件不存在'
        
        max_size_bytes = cls.MAX_FILE_SIZE * 1024 * 1024
        if file.size > max_size_bytes:
            return False, f'文件大小超过限制，最大允许{cls.MAX_FILE_SIZE}MB'
        
        return True, None
    
    @classmethod
    def calculate_file_hash(cls, file):
        """
        计算文件哈希值（用于重复文件检测）
        """
        if not file:
            return None
        
        hash_md5 = hashlib.md5()
        for chunk in file.chunks():
            hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    @classmethod
    def get_file_category(cls, content_type):
        """
        获取文件分类
        """
        for category, types in cls.ALLOWED_FILE_TYPES.items():
            if content_type in types:
                return category
        return 'unknown'


class SecurityLogger:
    """安全日志记录器 - 全覆盖通知系统操作日志"""
    
    @staticmethod
    def _get_user_agent(request):
        """获取用户代理"""
        return request.META.get('HTTP_USER_AGENT', '') if request else ''
    
    @staticmethod
    def _create_log(action, user, notification=None, ip_address=None, user_agent='', details=None):
        """创建日志记录"""
        from .models import NotificationLog
        return NotificationLog.objects.create(
            action=action,
            notification=notification,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
    
    @classmethod
    def log_notification_create(cls, user, notification, ip_address=None, request=None):
        """记录通知创建日志"""
        return cls._create_log(
            'create',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'type': notification.notification_type,
                'business_type': notification.business_type,
                'priority': notification.priority
            }
        )
    
    @classmethod
    def log_notification_send(cls, user, notification, ip_address=None, request=None):
        """记录通知发送日志"""
        return cls._create_log(
            'send',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'recipient_count': notification.recipients.count(),
                'type': notification.notification_type,
                'business_type': notification.business_type
            }
        )
    
    @classmethod
    def log_notification_recall(cls, user, notification, ip_address=None, request=None):
        """记录通知撤回日志"""
        return cls._create_log(
            'recall',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type,
                'read_count': notification.read_count
            }
        )
    
    @classmethod
    def log_notification_delete(cls, user, notification, ip_address=None, request=None):
        """记录通知删除日志"""
        return cls._create_log(
            'delete',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type,
                'status': notification.status
            }
        )
    
    @classmethod
    def log_notification_update(cls, user, notification, ip_address=None, request=None, changes=None):
        """记录通知更新日志"""
        return cls._create_log(
            'update',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type,
                'changes': changes or {}
            }
        )
    
    @classmethod
    def log_mark_as_read(cls, user, notification, ip_address=None, request=None):
        """记录标记已读日志"""
        return cls._create_log(
            'mark_as_read',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type
            }
        )
    
    @classmethod
    def log_mark_as_handled(cls, user, notification, ip_address=None, request=None):
        """记录标记已处理日志"""
        return cls._create_log(
            'mark_as_handled',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type,
                'need_action': notification.need_action
            }
        )
    
    @classmethod
    def log_batch_mark_read(cls, user, count, ip_address=None, request=None):
        """记录批量标记已读日志"""
        return cls._create_log(
            'batch_mark_read',
            user,
            None,
            ip_address,
            cls._get_user_agent(request),
            {'count': count}
        )
    
    @classmethod
    def log_attachment_upload(cls, user, attachment, ip_address=None, request=None):
        """记录附件上传日志"""
        return cls._create_log(
            'upload_attachment',
            user,
            attachment.notification if hasattr(attachment, 'notification') else None,
            ip_address,
            cls._get_user_agent(request),
            {
                'filename': attachment.filename,
                'file_size': attachment.file_size,
                'notification_id': attachment.notification_id if hasattr(attachment, 'notification_id') else None
            }
        )
    
    @classmethod
    def log_attachment_download(cls, user, attachment, ip_address=None, request=None):
        """记录附件下载日志"""
        return cls._create_log(
            'download_attachment',
            user,
            attachment.notification if hasattr(attachment, 'notification') else None,
            ip_address,
            cls._get_user_agent(request),
            {
                'filename': attachment.filename,
                'file_size': attachment.file_size
            }
        )
    
    @classmethod
    def log_attachment_delete(cls, user, filename, notification=None, ip_address=None, request=None):
        """记录附件删除日志"""
        return cls._create_log(
            'delete_attachment',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {'filename': filename}
        )
    
    @classmethod
    def log_view_detail(cls, user, notification, ip_address=None, request=None):
        """记录查看详情日志"""
        return cls._create_log(
            'view_detail',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'business_type': notification.business_type
            }
        )
    
    @classmethod
    def log_view_stats(cls, user, notification, ip_address=None, request=None):
        """记录查看统计日志"""
        return cls._create_log(
            'view_stats',
            user,
            notification,
            ip_address,
            cls._get_user_agent(request),
            {
                'title': notification.title,
                'total_recipients': notification.total_recipients,
                'read_count': notification.read_count
            }
        )
    
    @classmethod
    def log_update_settings(cls, user, settings_data, ip_address=None, request=None):
        """记录更新设置日志"""
        return cls._create_log(
            'update_settings',
            user,
            None,
            ip_address,
            cls._get_user_agent(request),
            {'settings': settings_data}
        )
    
    @classmethod
    def log_suspicious_activity(cls, user, action_type, details, ip_address=None, request=None):
        """记录可疑活动日志"""
        return cls._create_log(
            'suspicious',
            user,
            None,
            ip_address,
            cls._get_user_agent(request),
            {
                'action_type': action_type,
                'details': details
            }
        )
    
    @classmethod
    def log_rate_limit(cls, user, action, ip_address=None, request=None):
        """记录频率限制日志"""
        return cls._create_log(
            'rate_limit',
            user,
            None,
            ip_address,
            cls._get_user_agent(request),
            {'action': action}
        )
    
    @classmethod
    def log_security_alert(cls, user, alert_type, details, ip_address=None, request=None):
        """记录安全警告日志"""
        return cls._create_log(
            'security_alert',
            user,
            None,
            ip_address,
            cls._get_user_agent(request),
            {
                'alert_type': alert_type,
                'details': details
            }
        )


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
