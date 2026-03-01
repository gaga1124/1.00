import os
import django
import sys
from datetime import date, timedelta

# 设置 Django 环境
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_oa.settings')
django.setup()

from apps.research.models import ResearchProject, ResearchAchievement, ResearchTeam, TeamTask, TeamMeeting
from django.contrib.auth import get_user_model

User = get_user_model()

def create_research_data():
    print("正在创建科研模块测试数据...")
    
    # 获取用户
    admin = User.objects.filter(role='admin').first()
    teacher = User.objects.filter(role='teacher').first()
    student = User.objects.filter(role='student').first()
    
    if not admin or not teacher:
        print("缺少必要的用户（admin 或 teacher），请先运行初始数据脚本。")
        return

    # 1. 创建科研项目
    p1, created = ResearchProject.objects.get_or_create(
        project_code='NSFC-2024-001',
        defaults={
            'project_name': '基于深度学习的高校智慧校园管理系统研究',
            'project_type': 'national',
            'principal': teacher,
            'description': '本项目旨在利用深度学习技术优化高校行政管理流程，提升办公效率。',
            'start_date': date(2024, 1, 1),
            'end_date': date(2026, 12, 31),
            'status': 'approved',
            'total_budget': 500000.00,
            'used_budget': 50000.00,
            'budget_details': [
                {'category': '设备费', 'amount': 200000, 'used': 30000},
                {'category': '材料费', 'amount': 100000, 'used': 10000},
                {'category': '劳务费', 'amount': 100000, 'used': 10000},
                {'category': '差旅费', 'amount': 100000, 'used': 0}
            ]
        }
    )
    if created:
        p1.members.add(student)
        print(f"创建项目: {p1.project_name}")

    p2, created = ResearchProject.objects.get_or_create(
        project_code='PROV-2024-023',
        defaults={
            'project_name': '大数据背景下学生就业去向精准预测模型',
            'project_type': 'provincial',
            'principal': teacher,
            'description': '分析历史就业数据，建立多维度预测模型，为学生提供精准就业指导。',
            'start_date': date(2024, 3, 1),
            'end_date': date(2025, 2, 28),
            'status': 'midterm',
            'total_budget': 150000.00,
            'used_budget': 80000.00,
            'budget_details': [
                {'category': '数据采集费', 'amount': 50000, 'used': 45000},
                {'category': '劳务费', 'amount': 100000, 'used': 35000}
            ]
        }
    )
    if created:
        print(f"创建项目: {p2.project_name}")

    # 2. 创建科研成果
    a1, created = ResearchAchievement.objects.get_or_create(
        title='A Survey of Intelligent Campus Management Systems',
        defaults={
            'project': p1,
            'achievement_type': 'paper',
            'first_author': teacher,
            'journal': 'IEEE Transactions on Education',
            'publish_date': date(2024, 5, 20),
            'volume': 'Vol. 67, No. 3',
            'is_verified': True,
            'reward_amount': 5000.00
        }
    )
    if created:
        a1.authors.add(teacher, student)
        print(f"创建成果: {a1.title}")

    # 3. 创建科研团队
    t1, created = ResearchTeam.objects.get_or_create(
        name='智慧校园研发组',
        defaults={
            'leader': teacher,
            'description': '专注于高校信息化、智慧化建设的研究团队。'
        }
    )
    if created:
        t1.members.add(teacher, student, admin)
        print(f"创建团队: {t1.name}")

    # 4. 创建团队任务
    if created:
        TeamTask.objects.create(
            team=t1,
            title='系统原型设计',
            assignee=student,
            description='完成智慧校园OA系统的UI/UX原型设计',
            due_date=date.today() + timedelta(days=7),
            status='doing'
        )
        TeamTask.objects.create(
            team=t1,
            title='文献综述撰写',
            assignee=teacher,
            description='整理国内外智慧校园研究现状',
            due_date=date.today() + timedelta(days=14),
            status='todo'
        )
        print("创建团队任务完成")

    # 5. 创建会议纪要
    if created:
        TeamMeeting.objects.create(
            team=t1,
            title='项目启动会议',
            meeting_date=date.today() - timedelta(days=2),
            location='学院办公楼 302 会议室',
            content='1. 确定项目分工；\n2. 讨论技术选型；\n3. 制定第一季度里程碑。'
        )
        print("创建会议纪要完成")

if __name__ == '__main__':
    try:
        create_research_data()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
