from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.courses.models import Assignment, CourseSelection
from apps.notifications.models import Notification
from datetime import timedelta

class Command(BaseCommand):
    help = '发送作业截止提醒'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # 提醒明天截止的作业 (24h - 25h window to avoid duplicates if run hourly, or just < 24h and not notified?)
        # 简单起见，假设每天运行一次，提醒明天截止的
        tomorrow = now + timedelta(days=1)
        start_range = tomorrow - timedelta(hours=1)
        end_range = tomorrow + timedelta(hours=1)
        
        # 查找即将截止的作业
        assignments = Assignment.objects.filter(
            deadline__gt=now,
            deadline__lte=tomorrow
        )
        
        count = 0
        for assignment in assignments:
            # 找到选了这门课的学生
            selections = CourseSelection.objects.filter(
                course=assignment.course,
                status='approved'
            )
            
            for selection in selections:
                student = selection.student
                # 检查是否已提交
                if not assignment.submissions.filter(student=student).exists():
                    # 发送通知
                    Notification.objects.create(
                        recipient=student.user,
                        title=f"作业即将截止: {assignment.title}",
                        message=f"您的课程《{assignment.course.course_name}》有作业将于 {assignment.deadline.strftime('%Y-%m-%d %H:%M')} 截止，请及时提交。（逾期可能扣分）",
                        level='warning',
                        related_link=f"/academic/assignments/{assignment.id}"
                    )
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully sent {count} reminders'))
