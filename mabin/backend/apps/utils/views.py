"""
工具类视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
import os
import uuid
from .file_validator import validate_file


class FileUploadView(APIView):
    """文件上传视图"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'success': False, 'message': '没有上传文件'}, status=400)
        
        file = request.FILES['file']
        
        # 验证文件
        try:
            validate_file(file)
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=400)
        
        # 生成唯一文件名
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        file_path = os.path.join('uploads', filename)
        saved_path = default_storage.save(file_path, file)
        
        # 返回文件URL
        file_url = default_storage.url(saved_path)
        
        return Response({
            'success': True,
            'url': file_url,
            'name': file.name,
            'size': file.size
        })
