from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Course(models.Model):
    """课程"""
    course_code = models.CharField('课程代码', max_length=50, unique=True)
    name = models.CharField('课程名称', max_length=200)
    credit = models.DecimalField('学分', max_digits=3, decimal_places=1)
    hours = models.IntegerField('学时', default=0)
    course_type = models.CharField(
        '课程类型',
        max_length=20,
        choices=[
            ('required', '必修'),
            ('elective', '选修'),
            ('public', '公选'),
        ],
        default='required'
    )
    assessment_method = models.CharField('考核方式', max_length=50, blank=True)
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
    description = models.TextField('课程描述', blank=True)
    max_students = models.IntegerField('最大选课人数', default=50)
    current_students = models.IntegerField('当前选课人数', default=0)
    semester = models.CharField('学期', max_length=20)  # 如：2024-2025-1
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = '课程'
        verbose_name_plural = '课程'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course_code} - {self.name}"


class CourseSelection(models.Model):
    """选课记录"""
    STATUS_CHOICES = [
        ('selected', '已选'),
        ('dropped', '已退'),
        ('completed', '已完成'),
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
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='selected')
    selected_at = models.DateTimeField('选课时间', auto_now_add=True)
    dropped_at = models.DateTimeField('退课时间', null=True, blank=True)
    
    class Meta:
        db_table = 'course_selections'
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        unique_together = ['student', 'course']
        ordering = ['-selected_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.course.name}"


class Grade(models.Model):
    """成绩"""
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
    score = models.DecimalField('成绩', max_digits=5, decimal_places=2, null=True, blank=True)
    grade_point = models.DecimalField('绩点', max_digits=3, decimal_places=2, null=True, blank=True)
    grade_level = models.CharField(
        '等级',
        max_length=10,
        choices=[
            ('A+', 'A+'),
            ('A', 'A'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B', 'B'),
            ('B-', 'B-'),
            ('C+', 'C+'),
            ('C', 'C'),
            ('C-', 'C-'),
            ('D', 'D'),
            ('F', 'F'),
        ],
        blank=True
    )
    semester = models.CharField('学期', max_length=20)
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_grades',
        verbose_name='录入教师'
    )
    recorded_at = models.DateTimeField('录入时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    remark = models.TextField('备注', blank=True)
    
    class Meta:
        db_table = 'grades'
        verbose_name = '成绩'
        verbose_name_plural = '成绩'
        unique_together = ['student', 'course', 'semester']
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.course.name}: {self.score}"

class AttendanceSession(models.Model):
    """签到会话"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendance_sessions',
        verbose_name='课程'
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_attendance_sessions',
        verbose_name='发起教师'
    )
    date = models.DateField('日期', auto_now_add=True)
    time_slot = models.CharField('时间段', max_length=50, blank=True)
    check_in_code = models.CharField('签到码', max_length=10, blank=True)
    is_active = models.BooleanField('是否开启', default=True)
    expire_at = models.DateTimeField('过期时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'attendance_sessions'
        verbose_name = '签到会话'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.name} - {self.date} - {self.check_in_code}"


class Attendance(models.Model):
    """课堂签到"""
    STATUS_CHOICES = [
        ('present', '出勤'),
        ('absent', '缺勤'),
        ('late', '迟到'),
        ('early_leave', '早退'),
        ('excused', '请假'),
    ]
    
    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='签到会话',
        null=True,
        blank=True
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='课程'
    )
    date = models.DateField('签到日期')
    time_slot = models.CharField('时间段', max_length=50, blank=True)  # 如：第一节课
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='present')
    remark = models.TextField('备注', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'attendances'
        verbose_name = '课堂签到'
        verbose_name_plural = '课堂签到'
        ordering = ['-date', '-created_at']
        unique_together = ['student', 'course', 'date', 'time_slot']

    def __str__(self):
        return f"{self.student.user.real_name} - {self.course.name} - {self.date} - {self.get_status_display()}"
    
    def calculate_grade_point(self):
        """计算绩点"""
        if not self.score:
            return None
        score = float(self.score)
        if score >= 95:
            return 4.0
        elif score >= 90:
            return 3.7
        elif score >= 85:
            return 3.3
        elif score >= 80:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 70:
            return 2.3
        elif score >= 65:
            return 2.0
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
    
    file = models.FileField('作业附件', upload_to='assignments/tasks/%Y/%m/', blank=True, null=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'assignments'
        verbose_name = '课程作业'
        verbose_name_plural = verbose_name
        ordering = ['-deadline']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


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
    
    file = models.FileField('提交附件', upload_to='assignments/submissions/%Y/%m/', blank=True, null=True)
    content = models.TextField('作业内容', blank=True)
    
    submitted_at = models.DateTimeField('提交时间', auto_now_add=True)
    is_late = models.BooleanField('是否逾期', default=False)
    
    score = models.DecimalField('得分', max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField('教师评语', blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    class Meta:
        db_table = 'assignment_submissions'
        verbose_name = '作业提交'
        verbose_name_plural = verbose_name
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.assignment.title} - {self.student.user.real_name}"


class StudentStatus(models.Model):
    """学籍状态"""
    STATUS_CHOICES = [
        ('enrolled', '在校'),
        ('suspended', '休学'),
        ('transferred', '转学'),
        ('graduated', '毕业'),
        ('dropped', '退学'),
        ('expelled', '开除'),
    ]
    
    student = models.OneToOneField(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='status',
        verbose_name='学生'
    )
    status = models.CharField('学籍状态', max_length=20, choices=STATUS_CHOICES, default='enrolled')
    admission_date = models.DateField('入学日期')
    expected_graduation_date = models.DateField('预计毕业日期', null=True, blank=True)
    actual_graduation_date = models.DateField('实际毕业日期', null=True, blank=True)
    student_type = models.CharField(
        '学生类型',
        max_length=20,
        choices=[
            ('undergraduate', '本科生'),
            ('graduate', '研究生'),
            ('doctor', '博士生'),
        ],
        default='undergraduate'
    )
    enrollment_type = models.CharField(
        '招生类型',
        max_length=20,
        choices=[
            ('normal', '普通'),
            ('art', '艺术'),
            ('sports', '体育'),
            ('autonomous', '自主招生'),
        ],
        default='normal'
    )
    status_changes = models.JSONField('状态变更记录', default=list, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'student_status'
        verbose_name = '学籍状态'
        verbose_name_plural = '学籍状态'
    
    def __str__(self):
        return f"{self.student.user.real_name} - {self.get_status_display()}"
