"""
通知工具模块 - 统一发送各类业务通知
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Notification, NotificationSetting

User = get_user_model()


def create_notification(
    title,
    content,
    sender,
    recipients=None,
    business_type='system',
    business_id='',
    business_model='',
    business_action='',
    link_url='',
    link_params=None,
    priority='normal',
    need_action=False,
    expire_days=None,
    notification_type='specific'
):
    """
    创建并发送通知
    
    Args:
        title: 通知标题
        content: 通知内容
        sender: 发送人（User对象）
        recipients: 接收人列表（User对象列表）
        business_type: 业务类型
        business_id: 业务ID
        business_model: 业务模型
        business_action: 业务动作
        link_url: 跳转链接
        link_params: 链接参数
        priority: 优先级（normal/important/urgent）
        need_action: 是否需要处理
        expire_days: 过期天数
        notification_type: 通知类型（all/role/department/specific）
    
    Returns:
        Notification对象
    """
    # 创建通知
    notification = Notification.objects.create(
        title=title,
        content=content,
        sender=sender,
        business_type=business_type,
        business_id=str(business_id) if business_id else '',
        business_model=business_model,
        business_action=business_action,
        link_url=link_url,
        link_params=link_params or {},
        priority=priority,
        need_action=need_action,
        notification_type=notification_type,
        status='sent',
        sent_at=timezone.now()
    )
    
    # 设置过期时间
    if expire_days:
        notification.expire_at = timezone.now() + timedelta(days=expire_days)
        notification.save()
    
    # 设置接收人
    if recipients:
        # 根据用户设置过滤接收人
        filtered_recipients = []
        for user in recipients:
            setting, _ = NotificationSetting.objects.get_or_create(user=user)
            # 检查该类型通知是否开启
            if setting.is_type_enabled(business_type):
                # 检查是否在免打扰时间段
                if not setting.is_in_dnd_period():
                    filtered_recipients.append(user)
        
        notification.recipients.set(filtered_recipients)
        notification.total_recipients = len(filtered_recipients)
        notification.save()
        
        # 创建阅读记录
        notification.create_read_records()
    
    return notification


def send_workflow_notification(action, workflow_instance, user, approver=None):
    """
    发送流程相关通知
    
    Args:
        action: 动作（submit/approve/reject/transfer/remind）
        workflow_instance: 流程实例
        user: 当前操作用户
        approver: 审批人（用于待办通知）
    """
    from apps.workflow.models import WorkflowInstance
    
    workflow = workflow_instance.workflow
    
    if action == 'submit':
        # 提交申请通知
        if approver:
            create_notification(
                title=f'待办提醒：{workflow.name}',
                content=f'{user.real_name}提交了"{workflow.name}"申请，需要您审批。',
                sender=user,
                recipients=[approver],
                business_type='workflow',
                business_id=workflow_instance.id,
                business_model='WorkflowInstance',
                business_action='todo',
                link_url='/workflow/todos',
                priority='important',
                need_action=True
            )
    
    elif action == 'approve':
        # 审批通过通知
        create_notification(
            title=f'审批通过：{workflow.name}',
            content=f'您的"{workflow.name}"申请已通过审批。',
            sender=user,
            recipients=[workflow_instance.applicant],
            business_type='workflow',
            business_id=workflow_instance.id,
            business_model='WorkflowInstance',
            business_action='approved',
            link_url='/approval',
            priority='normal'
        )
        
        # 通知下一个审批人
        next_approver = workflow_instance.get_next_approver()
        if next_approver:
            create_notification(
                title=f'待办提醒：{workflow.name}',
                content=f'{user.real_name}审批通过了"{workflow.name}"申请，需要您继续审批。',
                sender=user,
                recipients=[next_approver],
                business_type='workflow',
                business_id=workflow_instance.id,
                business_model='WorkflowInstance',
                business_action='todo',
                link_url='/workflow/todos',
                priority='important',
                need_action=True
            )
    
    elif action == 'reject':
        # 审批驳回通知
        create_notification(
            title=f'审批驳回：{workflow.name}',
            content=f'您的"{workflow.name}"申请被驳回，原因：{workflow_instance.reject_reason or "无"}',
            sender=user,
            recipients=[workflow_instance.applicant],
            business_type='workflow',
            business_id=workflow_instance.id,
            business_model='WorkflowInstance',
            business_action='rejected',
            link_url='/approval',
            priority='important'
        )
    
    elif action == 'transfer':
        # 转交通知
        if approver:
            create_notification(
                title=f'待办提醒：{workflow.name}',
                content=f'{user.real_name}将"{workflow.name}"申请转交给您审批。',
                sender=user,
                recipients=[approver],
                business_type='workflow',
                business_id=workflow_instance.id,
                business_model='WorkflowInstance',
                business_action='todo',
                link_url='/workflow/todos',
                priority='important',
                need_action=True
            )
    
    elif action == 'remind':
        # 催办通知
        if approver:
            create_notification(
                title=f'催办提醒：{workflow.name}',
                content=f'{user.real_name}催办"{workflow.name}"申请，请尽快处理。',
                sender=user,
                recipients=[approver],
                business_type='workflow',
                business_id=workflow_instance.id,
                business_model='WorkflowInstance',
                business_action='remind',
                link_url='/workflow/todos',
                priority='urgent',
                need_action=True
            )
    
    elif action == 'cc':
        # 抄送通知
        cc_users = workflow_instance.cc_users.all()
        if cc_users:
            create_notification(
                title=f'抄送：{workflow.name}',
                content=f'{user.real_name}抄送给您"{workflow.name}"申请。',
                sender=user,
                recipients=list(cc_users),
                business_type='workflow',
                business_id=workflow_instance.id,
                business_model='WorkflowInstance',
                business_action='cc',
                link_url='/approval'
            )


def send_file_notification(action, file_obj, user, recipients=None):
    """
    发送文件签章相关通知
    
    Args:
        action: 动作（send/verify/remind）
        file_obj: 电子文件对象
        user: 当前操作用户
        recipients: 接收人列表
    """
    if action == 'send':
        # 文件发送通知
        if recipients:
            create_notification(
                title=f'新文件：{file_obj.title}',
                content=f'{user.real_name}发送了文件"{file_obj.title}"给您，请查收。',
                sender=user,
                recipients=recipients,
                business_type='file',
                business_id=file_obj.id,
                business_model='ElectronicFile',
                business_action='received',
                link_url=f'/electronic-signature',
                link_params={'file_id': file_obj.id},
                priority='normal'
            )
    
    elif action == 'verify':
        # 需要验签通知
        create_notification(
            title=f'需要验签：{file_obj.title}',
            content=f'文件"{file_obj.title}"需要您进行签章验证。',
            sender=user,
            recipients=recipients or [],
            business_type='file',
            business_id=file_obj.id,
            business_model='ElectronicFile',
            business_action='verify',
            link_url=f'/electronic-signature',
            link_params={'file_id': file_obj.id, 'action': 'verify'},
            priority='important',
            need_action=True
        )
    
    elif action == 'remind':
        # 文件阅读提醒
        if recipients:
            create_notification(
                title=f'阅读提醒：{file_obj.title}',
                content=f'您有文件"{file_obj.title}"尚未阅读，请及时查看。',
                sender=user,
                recipients=recipients,
                business_type='file',
                business_id=file_obj.id,
                business_model='ElectronicFile',
                business_action='remind',
                link_url=f'/electronic-signature',
                link_params={'file_id': file_obj.id},
                priority='normal'
            )


def send_academic_notification(action, obj, user, recipients=None, **kwargs):
    """
    发送教务相关通知
    
    Args:
        action: 动作（grade_publish/attendance_warning/course_remind/exam_remind）
        obj: 相关对象
        user: 发送人
        recipients: 接收人列表
    """
    if action == 'grade_publish':
        # 成绩发布通知
        course_name = kwargs.get('course_name', '')
        create_notification(
            title=f'成绩发布：{course_name}',
            content=f'您的{course_name}课程成绩已发布，请查看。',
            sender=user,
            recipients=recipients or [],
            business_type='academic',
            business_id=obj.id if hasattr(obj, 'id') else '',
            business_model=obj.__class__.__name__,
            business_action='grade_publish',
            link_url='/academic/grades',
            priority='important'
        )
    
    elif action == 'attendance_warning':
        # 考勤预警通知
        course_name = kwargs.get('course_name', '')
        absence_count = kwargs.get('absence_count', 0)
        create_notification(
            title=f'考勤预警：{course_name}',
            content=f'您在{course_name}课程的缺勤次数已达到{absence_count}次，请注意。',
            sender=user,
            recipients=recipients or [],
            business_type='academic',
            business_id=obj.id if hasattr(obj, 'id') else '',
            business_model=obj.__class__.__name__,
            business_action='attendance_warning',
            link_url='/academic/attendance',
            priority='urgent'
        )
    
    elif action == 'course_remind':
        # 上课提醒
        course_name = kwargs.get('course_name', '')
        classroom = kwargs.get('classroom', '')
        start_time = kwargs.get('start_time', '')
        create_notification(
            title=f'上课提醒：{course_name}',
            content=f'您有{course_name}课程即将开始，地点：{classroom}，时间：{start_time}',
            sender=user,
            recipients=recipients or [],
            business_type='academic',
            business_id=obj.id if hasattr(obj, 'id') else '',
            business_model=obj.__class__.__name__,
            business_action='course_remind',
            link_url='/academic/courses',
            priority='normal',
            expire_days=1
        )
    
    elif action == 'exam_remind':
        # 考试提醒
        course_name = kwargs.get('course_name', '')
        exam_time = kwargs.get('exam_time', '')
        classroom = kwargs.get('classroom', '')
        create_notification(
            title=f'考试提醒：{course_name}',
            content=f'您有{course_name}考试，时间：{exam_time}，地点：{classroom}',
            sender=user,
            recipients=recipients or [],
            business_type='academic',
            business_id=obj.id if hasattr(obj, 'id') else '',
            business_model=obj.__class__.__name__,
            business_action='exam_remind',
            link_url='/academic/grades',
            priority='important',
            expire_days=7
        )


def send_warning_notification(warning_type, user, **kwargs):
    """
    发送预警通知
    
    Args:
        warning_type: 预警类型（grade/finance/registration/attendance）
        user: 接收人
        **kwargs: 其他参数
    """
    if warning_type == 'grade':
        # 成绩预警
        course_name = kwargs.get('course_name', '')
        grade = kwargs.get('grade', 0)
        create_notification(
            title='成绩预警',
            content=f'您的{course_name}课程成绩为{grade}分，请注意学习。',
            sender=User.objects.filter(is_staff=True).first(),
            recipients=[user],
            business_type='warning',
            business_action='grade_warning',
            link_url='/academic/grades',
            priority='urgent'
        )
    
    elif warning_type == 'finance':
        # 经费预警
        project_name = kwargs.get('project_name', '')
        remaining = kwargs.get('remaining', 0)
        create_notification(
            title='经费预警',
            content=f'项目"{project_name}"经费剩余{remaining}元，请注意使用。',
            sender=User.objects.filter(is_staff=True).first(),
            recipients=[user],
            business_type='warning',
            business_action='finance_warning',
            link_url='/research/projects',
            priority='important'
        )
    
    elif warning_type == 'registration':
        # 报到预警
        days_remaining = kwargs.get('days_remaining', 0)
        create_notification(
            title='报到提醒',
            content=f'距离报到截止日期还有{days_remaining}天，请及时完成报到。',
            sender=User.objects.filter(is_staff=True).first(),
            recipients=[user],
            business_type='warning',
            business_action='registration_warning',
            link_url='/students',
            priority='urgent'
        )
    
    elif warning_type == 'attendance':
        # 考勤预警
        absence_count = kwargs.get('absence_count', 0)
        threshold = kwargs.get('threshold', 0)
        create_notification(
            title='考勤预警',
            content=f'您本学期累计缺勤{absence_count}次，已达到预警阈值（{threshold}次），请注意出勤。',
            sender=User.objects.filter(is_staff=True).first(),
            recipients=[user],
            business_type='warning',
            business_action='attendance_warning',
            link_url='/academic/attendance',
            priority='urgent'
        )


def send_activity_notification(action, activity, user, recipients=None):
    """
    发送活动相关通知
    
    Args:
        action: 动作（publish/remind/start/end/result）
        activity: 活动对象
        user: 发送人
        recipients: 接收人列表
    """
    if action == 'publish':
        # 活动发布通知
        create_notification(
            title=f'新活动：{activity.title}',
            content=f'新活动"{activity.title}"已发布，欢迎报名参加。',
            sender=user,
            recipients=recipients or [],
            business_type='activity',
            business_id=activity.id,
            business_model=activity.__class__.__name__,
            business_action='publish',
            link_url=f'/activities/{activity.activity_type}',
            priority='normal'
        )
    
    elif action == 'remind':
        # 活动开始提醒
        create_notification(
            title=f'活动提醒：{activity.title}',
            content=f'您报名的活动"{activity.title}"即将开始，请准时参加。',
            sender=user,
            recipients=recipients or [],
            business_type='activity',
            business_id=activity.id,
            business_model=activity.__class__.__name__,
            business_action='remind',
            link_url=f'/activities/{activity.activity_type}',
            priority='important',
            expire_days=1
        )
    
    elif action == 'start':
        # 活动开始通知
        create_notification(
            title=f'活动开始：{activity.title}',
            content=f'活动"{activity.title}"已开始。',
            sender=user,
            recipients=recipients or [],
            business_type='activity',
            business_id=activity.id,
            business_model=activity.__class__.__name__,
            business_action='start',
            link_url=f'/activities/{activity.activity_type}',
            priority='normal',
            expire_days=1
        )
    
    elif action == 'result':
        # 活动结果通知
        result = kwargs.get('result', '')
        create_notification(
            title=f'活动结果：{activity.title}',
            content=f'活动"{activity.title}"结果已公布：{result}',
            sender=user,
            recipients=recipients or [],
            business_type='activity',
            business_id=activity.id,
            business_model=activity.__class__.__name__,
            business_action='result',
            link_url=f'/activities/{activity.activity_type}',
            priority='important'
        )


def send_repair_notification(action, repair_order, user, recipients=None):
    """
    发送报修相关通知
    
    Args:
        action: 动作（submit/assign/complete/cancel）
        repair_order: 报修单对象
        user: 发送人
        recipients: 接收人列表
    """
    if action == 'submit':
        # 报修提交通知
        create_notification(
            title='报修申请已提交',
            content=f'您的报修申请"{repair_order.title}"已提交，等待处理。',
            sender=user,
            recipients=[repair_order.applicant],
            business_type='repair',
            business_id=repair_order.id,
            business_model='RepairOrder',
            business_action='submit',
            link_url='/repair',
            priority='normal'
        )
    
    elif action == 'assign':
        # 报修分配通知
        create_notification(
            title='报修任务分配',
            content=f'您有新的报修任务"{repair_order.title}"需要处理。',
            sender=user,
            recipients=recipients or [],
            business_type='repair',
            business_id=repair_order.id,
            business_model='RepairOrder',
            business_action='assign',
            link_url='/repair',
            priority='normal',
            need_action=True
        )
    
    elif action == 'complete':
        # 报修完成通知
        create_notification(
            title='报修已完成',
            content=f'您的报修申请"{repair_order.title}"已处理完成。',
            sender=user,
            recipients=[repair_order.applicant],
            business_type='repair',
            business_id=repair_order.id,
            business_model='RepairOrder',
            business_action='complete',
            link_url='/repair',
            priority='normal'
        )


def send_resource_notification(action, reservation, user, recipients=None):
    """
    发送资源预约相关通知
    
    Args:
        action: 动作（submit/approve/reject/remind）
        reservation: 预约对象
        user: 发送人
        recipients: 接收人列表
    """
    resource_name = reservation.resource.name if reservation.resource else ''
    
    if action == 'submit':
        # 预约提交通知
        create_notification(
            title='预约申请已提交',
            content=f'您的"{resource_name}"预约申请已提交，等待审批。',
            sender=user,
            recipients=[reservation.applicant],
            business_type='resource',
            business_id=reservation.id,
            business_model='ResourceReservation',
            business_action='submit',
            link_url='/resources',
            priority='normal'
        )
    
    elif action == 'approve':
        # 预约通过通知
        create_notification(
            title='预约申请已通过',
            content=f'您的"{resource_name}"预约申请已通过。',
            sender=user,
            recipients=[reservation.applicant],
            business_type='resource',
            business_id=reservation.id,
            business_model='ResourceReservation',
            business_action='approve',
            link_url='/resources',
            priority='normal'
        )
    
    elif action == 'reject':
        # 预约驳回通知
        reason = kwargs.get('reason', '')
        create_notification(
            title='预约申请被驳回',
            content=f'您的"{resource_name}"预约申请被驳回，原因：{reason}',
            sender=user,
            recipients=[reservation.applicant],
            business_type='resource',
            business_id=reservation.id,
            business_model='ResourceReservation',
            business_action='reject',
            link_url='/resources',
            priority='normal'
        )
    
    elif action == 'remind':
        # 预约提醒
        start_time = kwargs.get('start_time', '')
        create_notification(
            title='预约提醒',
            content=f'您预约的"{resource_name}"即将开始，时间：{start_time}',
            sender=user,
            recipients=[reservation.applicant],
            business_type='resource',
            business_id=reservation.id,
            business_model='ResourceReservation',
            business_action='remind',
            link_url='/resources',
            priority='normal',
            expire_days=1
        )


def get_user_unread_count(user):
    """获取用户未读通知数量"""
    from .models import NotificationRead
    return NotificationRead.objects.filter(
        user=user,
        is_read=False,
        notification__status='sent'
    ).count()


def get_user_todo_count(user):
    """获取用户待办通知数量"""
    from .models import NotificationRead
    return NotificationRead.objects.filter(
        user=user,
        is_read=False,
        notification__status='sent',
        notification__need_action=True,
        is_handled=False
    ).count()


def mark_all_as_read(user):
    """标记用户所有通知为已读"""
    from .models import NotificationRead
    unread_records = NotificationRead.objects.filter(
        user=user,
        is_read=False
    )
    for record in unread_records:
        record.mark_as_read()
