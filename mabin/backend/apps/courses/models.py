from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    """课程"""
    COURSE_TYPES = [
        ('required', '必修课'),
        ('elective', '选修课'),
        ('public', '公选课'),
    ]
    
    course_code = models.CharField('课程代码', max_length=50, unique=True)
    course_name = models.CharField('课程名称', max_length=200)
    course_type = models.CharField('课程类型', max_length=20, choices=COURSE_TYPES)
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        verbose_name='开课学院'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='taught_courses',
        verbose_name='授课教师'
    )
    credits = models.DecimalField('学分', max_digits=3, decimal_places=1)
    hours = models.IntegerField('学时', default=0)
    capacity = models.IntegerField('容量', default=0)  # 选课容量
    enrolled_count = models.IntegerField('已选人数', default=0)
    
    # 上课信息
    classroom = models.CharField('教室', max_length=100, blank=True)
    schedule = models.JSONField('上课时间', default=list, blank=True)
    # 示例：[{"day": "周一", "time": "1-2节", "location": "A101"}]
    
    # 课程信息
    description = models.TextField('课程描述', blank=True)
    syllabus = models.FileField('教学大纲', upload_to='courses/syllabus/', blank=True, null=True)
    
    # 选课设置
    is_open = models.BooleanField('是否开放选课', default=True)
    start_time = models.DateTimeField('选课开始时间', null=True, blank=True)
    end_time = models.DateTimeField('选课结束时间', null=True, blank=True)
    
    # 成绩设置
    assessment_method = models.CharField('考核方式', max_length=50, blank=True)  # 考试/考查
    score_composition = models.JSONField('成绩构成', default=dict, blank=True)
    # 示例：{"平时": 30, "期中": 20, "期末": 50}
    
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course_name} ({self.course_code})"


class CourseSelection(models.Model):
    """选课记录"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已选上'),
        ('rejected', '已拒绝'),
        ('dropped', '已退选'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='course_selections',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='selections',
        verbose_name='课程'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    selection_time = models.DateTimeField('选课时间', auto_now_add=True)
    drop_time = models.DateTimeField('退选时间', null=True, blank=True)
    reason = models.TextField('选课理由', blank=True)
    
    class Meta:
        db_table = 'course_selections'
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        unique_together = ['student', 'course']
        ordering = ['-selection_time']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.course.course_name}"


class Grade(models.Model):
    """成绩"""
    GRADE_TYPES = [
        ('normal', '正常'),
        ('makeup', '补考'),
        ('retake', '重修'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='课程'
    )
    selection = models.OneToOneField(
        CourseSelection,
        on_delete=models.CASCADE,
        related_name='grade',
        verbose_name='选课记录',
        null=True,
        blank=True
    )
    
    # 成绩组成
    usual_score = models.DecimalField('平时成绩', max_digits=5, decimal_places=2, null=True, blank=True)
    midterm_score = models.DecimalField('期中成绩', max_digits=5, decimal_places=2, null=True, blank=True)
    final_score = models.DecimalField('期末成绩', max_digits=5, decimal_places=2, null=True, blank=True)
    total_score = models.DecimalField('总成绩', max_digits=5, decimal_places=2, null=True, blank=True)
    
    # 等级
    grade_point = models.DecimalField('绩点', max_digits=3, decimal_places=2, null=True, blank=True)
    grade_level = models.CharField('等级', max_length=10, blank=True)  # A/B/C/D/F
    
    grade_type = models.CharField('成绩类型', max_length=20, choices=GRADE_TYPES, default='normal')
    semester = models.CharField('学期', max_length=20)  # 如：2024-2025-1
    academic_year = models.CharField('学年', max_length=20)  # 如：2024-2025
    
    # 录入信息
    entered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_grades',
        verbose_name='录入人'
    )
    entered_at = models.DateTimeField('录入时间', null=True, blank=True)
    is_confirmed = models.BooleanField('已确认', default=False)
    
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = '成绩'
        verbose_name_plural = '成绩'
        unique_together = ['student', 'course', 'semester']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'semester']),
            models.Index(fields=['course', 'semester']),
        ]
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.course.course_name} - {self.total_score}"
    
    def calculate_total_score(self):
        """计算总成绩"""
        if not self.course.score_composition:
            return None
        
        total = 0
        composition = self.course.score_composition
        
        if '平时' in composition and self.usual_score:
            total += float(self.usual_score) * composition['平时'] / 100
        if '期中' in composition and self.midterm_score:
            total += float(self.midterm_score) * composition['期中'] / 100
        if '期末' in composition and self.final_score:
            total += float(self.final_score) * composition['期末'] / 100
        
        return round(total, 2) if total > 0 else None
    
    def calculate_grade_point(self):
        """计算绩点"""
        if not self.total_score:
            return None
        
        score = float(self.total_score)
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 82:
            return 3.3
        elif score >= 78:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 72:
            return 2.3
        elif score >= 68:
            return 2.0
        elif score >= 64:
            return 1.5
        elif score >= 60:
            return 1.0
        else:
            return 0.0


class Assignment(models.Model):
    """课程作业"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='课程'
    )
    title = models.CharField('作业标题', max_length=200)
    description = models.TextField('作业描述')
    deadline = models.DateTimeField('截止时间')
    
    allow_late_submission = models.BooleanField('允许补交', default=True)
    late_penalty = models.IntegerField('逾期扣分百分比', default=10, help_text='百分比，如10代表扣除10%')
    weight_in_score = models.IntegerField('占平时成绩权重', default=0, help_text='百分比，0-100')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'course_assignments'
        verbose_name = '课程作业'
        verbose_name_plural = verbose_name
        ordering = ['-deadline']

    def __str__(self):
        return f"{self.course.course_name} - {self.title}"


class AssignmentSubmission(models.Model):
    """作业提交"""
    STATUS_CHOICES = [
        ('submitted', '已提交'),
        ('graded', '已评分'),
        ('returned', '已退回'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='作业'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        verbose_name='学生'
    )
    
    file = models.FileField('作业附件', upload_to='assignments/%Y/%m/', blank=True, null=True)
    content = models.TextField('作业内容', blank=True)
    
    submitted_at = models.DateTimeField('提交时间', auto_now=True)
    is_late = models.BooleanField('是否逾期', default=False)
    
    score = models.DecimalField('得分', max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField('教师评语', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    class Meta:
        db_table = 'course_assignment_submissions'
        verbose_name = '作业提交'
        verbose_name_plural = verbose_name
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.assignment.title} - {self.student.user.real_name}"
