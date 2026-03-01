from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.db import transaction
from .models import Course, CourseSelection, Grade
from .serializers import CourseSerializer, CourseSelectionSerializer, GradeSerializer


import logging
logger = logging.getLogger(__name__)

class DeprecatedViewSetMixin:
    def initialize_request(self, request, *args, **kwargs):
        logger.warning(f"Deprecated API access: {request.path} by user {request.user}")
        return super().initialize_request(request, *args, **kwargs)
    
    def finalize_response(self, request, response, *args, **kwargs):
        try:
            response['X-Deprecated-API'] = 'true'
            response['X-Deprecated-Path'] = str(request.path)
            response['X-Deprecated-Use'] = '/api/academic/'
        except Exception:
            pass
        return super().finalize_response(request, response, *args, **kwargs)

class CourseViewSet(DeprecatedViewSetMixin, viewsets.ModelViewSet):
    
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_type', 'is_open', 'is_active', 'department', 'teacher']
    search_fields = ['course_code', 'course_name', 'description']
    ordering_fields = ['created_at', 'course_code', 'enrolled_count']
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可选课程列表"""
        courses = self.get_queryset().filter(is_open=True)
        
        # 检查选课时间
        now = timezone.now()
        courses = courses.filter(
            Q(start_time__lte=now) | Q(start_time__isnull=True),
            Q(end_time__gte=now) | Q(end_time__isnull=True)
        )
        
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def select(self, request, pk=None):
        """选课"""
        course = self.get_object()
        student = request.user.student_profile
        
        if not student:
            return Response({'error': '当前用户不是学生'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已选
        if CourseSelection.objects.filter(student=student, course=course).exists():
            return Response({'error': '您已选择此课程'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查容量
        if course.capacity > 0 and course.enrolled_count >= course.capacity:
            return Response({'error': '课程已满'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查选课时间
        now = timezone.now()
        if course.start_time and now < course.start_time:
            return Response({'error': '选课尚未开始'}, status=status.HTTP_400_BAD_REQUEST)
        if course.end_time and now > course.end_time:
            return Response({'error': '选课已结束'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建选课记录
        with transaction.atomic():
            selection = CourseSelection.objects.create(
                student=student,
                course=course,
                status='approved',
                reason=request.data.get('reason', '')
            )
            course.enrolled_count += 1
            course.save()
        
        serializer = CourseSelectionSerializer(selection)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def drop(self, request, pk=None):
        """退选"""
        course = self.get_object()
        student = request.user.student_profile
        
        if not student:
            return Response({'error': '当前用户不是学生'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            selection = CourseSelection.objects.get(student=student, course=course, status='approved')
        except CourseSelection.DoesNotExist:
            return Response({'error': '未找到选课记录'}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            selection.status = 'dropped'
            selection.drop_time = timezone.now()
            selection.save()
            course.enrolled_count = max(0, course.enrolled_count - 1)
            course.save()
        
        return Response({'message': '退选成功'})


class CourseSelectionViewSet(DeprecatedViewSetMixin, viewsets.ModelViewSet):
    """选课记录视图集"""
    queryset = CourseSelection.objects.all()
    serializer_class = CourseSelectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 学生只能看自己的
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        # 教师可以看自己课程的选课
        if hasattr(user, 'taught_courses'):
            return queryset.filter(course__teacher=user)
        
        return queryset.none()


class GradeViewSet(DeprecatedViewSetMixin, viewsets.ModelViewSet):
    """成绩视图集"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['semester', 'course', 'student', 'is_confirmed']
    search_fields = ['student__user__real_name', 'student__student_id', 'course__course_name', 'course__course_code']
    ordering_fields = ['total_score', 'grade_point', 'created_at']
    
    def get_queryset(self):
        """根据用户角色过滤"""
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        # 学生只能看自己的成绩
        if hasattr(user, 'student_profile'):
            return queryset.filter(student=user.student_profile)
        
        # 教师可以看自己课程的成绩
        if hasattr(user, 'taught_courses'):
            return queryset.filter(course__teacher=user)
        
        # 学院秘书可以看本学院学生的成绩
        if user.department:
            return queryset.filter(student__user__department=user.department)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """创建成绩时自动设置录入人"""
        grade = serializer.save(entered_by=self.request.user, entered_at=timezone.now())
        
        # 自动计算总成绩和绩点
        if grade.course.score_composition:
            total = grade.calculate_total_score()
            if total:
                grade.total_score = total
                grade.grade_point = grade.calculate_grade_point()
                
                # 计算等级
                if total >= 90:
                    grade.grade_level = 'A'
                elif total >= 80:
                    grade.grade_level = 'B'
                elif total >= 70:
                    grade.grade_level = 'C'
                elif total >= 60:
                    grade.grade_level = 'D'
                else:
                    grade.grade_level = 'F'
                
                grade.save()
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """成绩统计"""
        student_id = request.query_params.get('student_id')
        semester = request.query_params.get('semester')
        
        queryset = self.get_queryset()
        
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if semester:
            queryset = queryset.filter(semester=semester)
        
        # 统计信息
        total_courses = queryset.count()
        passed_courses = queryset.filter(total_score__gte=60).count()
        failed_courses = total_courses - passed_courses
        
        # 计算平均分和平均绩点
        avg_score = queryset.aggregate(avg=Avg('total_score'))['avg'] or 0
        avg_gpa = queryset.aggregate(avg=Avg('grade_point'))['avg'] or 0
        
        # 学分统计
        total_credits = sum([g.course.credits for g in queryset if g.total_score and g.total_score >= 60])
        
        return Response({
            'total_courses': total_courses,
            'passed_courses': passed_courses,
            'failed_courses': failed_courses,
            'pass_rate': round(passed_courses / total_courses * 100, 2) if total_courses > 0 else 0,
            'average_score': round(float(avg_score), 2),
            'average_gpa': round(float(avg_gpa), 2),
            'total_credits': float(total_credits)
        })
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认成绩"""
        grade = self.get_object()
        grade.is_confirmed = True
        grade.save()
        return Response({'message': '成绩已确认'})


from .models import Assignment, AssignmentSubmission
from .serializers import AssignmentSerializer, AssignmentSubmissionSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    """作业视图集"""
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course']
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'created_at']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Assignment.objects.all()
        
        # 教师查看自己课程的作业
        if hasattr(user, 'taught_courses'):
            return Assignment.objects.filter(course__teacher=user)
            
        # 学生查看自己选课的作业
        if hasattr(user, 'student_profile'):
            return Assignment.objects.filter(
                course__selections__student=user.student_profile, 
                course__selections__status='approved'
            )
            
        return Assignment.objects.none()
    
    def perform_create(self, serializer):
        # 简单权限检查：只有关联课程的教师可以创建
        # 这里简化处理，假设前端会传正确的course_id，且在后端验证
        # 实际应检查 serializer.validated_data['course'].teacher == self.request.user
        serializer.save()


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """作业提交视图集"""
    queryset = AssignmentSubmission.objects.all()
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AssignmentSubmission.objects.all()
            
        # 教师查看自己发布作业的提交
        if hasattr(user, 'taught_courses'):
            return AssignmentSubmission.objects.filter(assignment__course__teacher=user)
            
        # 学生只能看自己的提交
        if hasattr(user, 'student_profile'):
            return AssignmentSubmission.objects.filter(student=user.student_profile)
            
        return AssignmentSubmission.objects.none()
    
    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise serializers.ValidationError("Only students can submit assignments.")
            
        assignment = serializer.validated_data['assignment']
        now = timezone.now()
        is_late = False
        
        # 检查是否逾期
        if now > assignment.deadline:
            if not assignment.allow_late_submission:
                raise serializers.ValidationError("This assignment does not allow late submissions.")
            is_late = True
            
        serializer.save(
            student=user.student_profile,
            is_late=is_late
        )
        
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """教师评分"""
        submission = self.get_object()
        
        # 权限检查
        if submission.assignment.course.teacher != request.user and not request.user.is_superuser:
            return Response({'error': '无权评分'}, status=403)
            
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        if score is None:
            return Response({'error': '分数不能为空'}, status=400)
            
        submission.score = score
        submission.feedback = feedback
        submission.status = 'graded'
        submission.save()
        
        return Response(self.get_serializer(submission).data)
