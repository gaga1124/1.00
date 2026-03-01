"""
学生管理测试用例
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Student

User = get_user_model()


class StudentAPITestCase(TestCase):
    """学生API测试"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='teacher',
            password='testpass123',
            real_name='测试教师'
        )
        self.student_user = User.objects.create_user(
            username='student001',
            password='testpass123',
            real_name='测试学生'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='2021001',
            major='计算机科学',
            class_name='2021级1班',
            grade='2021级',
            political_status='member'
        )
    
    def test_get_student_list(self):
        """测试获取学生列表"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_student_detail(self):
        """测试获取学生详情"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/students/{self.student.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], '2021001')
    
    def test_get_student_records(self):
        """测试获取学生档案记录"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/students/{self.student.id}/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
