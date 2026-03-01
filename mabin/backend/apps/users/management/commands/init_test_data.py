from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rbac.models import Role, UserRole, Department
from apps.students.models import Student
from apps.academic.models import Course, Grade, CourseSelection
from apps.research.models import ResearchProject
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试用户及关联数据'

    def handle(self, *args, **options):
        # 1. 创建部门
        dept, _ = Department.objects.get_or_create(code='cs_dept', defaults={'name': '计算机科学系'})
        
        # 2. 创建用户
        username = 'test_student_01'
        email = 'test@example.com'
        password = 'password123'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'real_name': '张测试',
                'department': dept,
                'is_active': True
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"成功创建用户: {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"用户已存在: {username}"))

        # 3. 分配角色
        student_role, _ = Role.objects.get_or_create(
            code='student', 
            defaults={'name': '学生', 'role_type': 'student'}
        )
        UserRole.objects.get_or_create(user=user, role=student_role)
        
        # 4. 创建学生档案
        student, s_created = Student.objects.get_or_create(
            user=user,
            defaults={
                'student_id': '2024001',
                'major': '计算机科学与技术',
                'class_name': '计科2401',
                'grade': '2024级',
                'political_status': 'member'
            }
        )
        if s_created:
            self.stdout.write(self.style.SUCCESS(f"创建学生档案: {student.student_id}"))

        # 5. 测试数据 - 课程与成绩
        course, _ = Course.objects.get_or_create(
            course_code='CS101',
            defaults={
                'name': 'Python程序设计',
                'credit': 4.0,
                'hours': 64,
                'course_type': 'required',
                'semester': '2024-2025-1'
            }
        )
        
        CourseSelection.objects.get_or_create(student=student, course=course, defaults={'status': 'completed'})
        Grade.objects.get_or_create(student=student, course=course, defaults={'score': 95, 'grade_point': 4.5})

        # 6. 测试数据 - 科研项目
        from datetime import timedelta
        ResearchProject.objects.get_or_create(
            project_code='PRJ2024001',
            defaults={
                'project_name': 'AI校园助手开发',
                'project_type': 'university',
                'principal': user,
                'description': '开发一个基于大模型的校园助手',
                'total_budget': 5000.0,
                'used_budget': 1200.0,
                'status': 'approved',
                'start_date': datetime.now().date(),
                'end_date': (datetime.now() + timedelta(days=365)).date()
            }
        )
        
        self.stdout.write(self.style.SUCCESS("测试数据添加完成！"))
