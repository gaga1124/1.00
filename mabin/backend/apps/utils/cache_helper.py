"""
缓存辅助工具
"""
from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_result(timeout=300, key_prefix=''):
    """
    缓存函数结果装饰器
    
    Args:
        timeout: 缓存超时时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{_generate_key(args, kwargs)}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def _generate_key(args, kwargs):
    """生成缓存键"""
    key_data = {
        'args': str(args),
        'kwargs': json.dumps(kwargs, sort_keys=True)
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def invalidate_cache(pattern):
    """
    使匹配模式的缓存失效
    
    Args:
        pattern: 缓存键模式（支持通配符）
    """
    # 注意：Django的cache框架不支持通配符删除
    # 实际项目中可以使用Redis的keys命令或维护缓存键列表
    pass


def cache_user_permissions(user_id, timeout=3600):
    """缓存用户权限"""
    cache_key = f"user_permissions:{user_id}"
    return cache_key


def get_cached_user_permissions(user_id):
    """获取缓存的用户权限"""
    cache_key = cache_user_permissions(user_id)
    return cache.get(cache_key)


def set_cached_user_permissions(user_id, permissions, timeout=3600):
    """设置用户权限缓存"""
    cache_key = cache_user_permissions(user_id)
    cache.set(cache_key, permissions, timeout)
