"""
自定义中间件
"""
import time
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse


class PerformanceMiddleware(MiddlewareMixin):
    """性能监控中间件"""
    
    def process_request(self, request):
        """请求开始时间"""
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """记录响应时间"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            # 记录慢查询（超过500ms）
            if duration > 0.5:
                print(f"Slow request: {request.path} took {duration:.2f}s")
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """API限流中间件"""
    
    def process_request(self, request):
        """检查请求频率"""
        # 只对API请求进行限流
        if not request.path.startswith('/api/'):
            return None
        
        # 获取客户端IP
        ip = self.get_client_ip(request)
        cache_key = f"rate_limit:{ip}"
        
        # 检查请求次数
        requests = cache.get(cache_key, 0)
        if requests >= 100:  # 每分钟最多100次请求
            return JsonResponse({
                'error': '请求过于频繁，请稍后再试'
            }, status=429)
        
        # 增加请求计数
        cache.set(cache_key, requests + 1, 60)  # 60秒过期
        return None
    
    def get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
