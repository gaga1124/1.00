"""
评奖评优工具函数
"""
from django.db.models import Avg


def match_award_conditions(student, award_type):
    """
    匹配学生是否符合奖项评选条件
    
    Returns:
        dict: {
            'matched': bool,
            'conditions': dict,  # 条件检查结果
            'score': float,  # 匹配分数
            'details': list  # 详细信息
        }
    """
    criteria = award_type.criteria or {}
    result = {
        'matched': True,
        'conditions': {},
        'score': 100,
        'details': []
    }
    
    # 检查绩点
    if 'gpa_min' in criteria:
        gpa = calculate_gpa(student)
        is_matched = gpa >= float(criteria['gpa_min'])
        result['conditions']['gpa'] = gpa
        result['details'].append({'name': '绩点', 'matched': is_matched, 'value': gpa, 'required': criteria['gpa_min']})
        if not is_matched:
            result['matched'] = False
            result['score'] -= 20
    
    # 检查平均分
    if 'score_min' in criteria:
        avg_score = calculate_avg_score(student)
        is_matched = avg_score >= float(criteria['score_min'])
        result['conditions']['avg_score'] = avg_score
        result['details'].append({'name': '平均分', 'matched': is_matched, 'value': avg_score, 'required': criteria['score_min']})
        if not is_matched:
            result['matched'] = False
            result['score'] -= 20
    
    # 检查是否有不及格
    if criteria.get('no_fail', False) or criteria.get('no_failures', False):
        has_fail = check_has_fail(student)
        is_matched = not has_fail
        result['conditions']['no_fail'] = is_matched
        result['details'].append({'name': '无不及格科目', 'matched': is_matched})
        if not is_matched:
            result['matched'] = False
            result['score'] -= 30
    
    # 检查政治面貌
    if 'political_status' in criteria:
        required_statuses = criteria['political_status']
        if isinstance(required_statuses, str):
            required_statuses = [required_statuses]
        current_status = student.political_status
        is_matched = current_status in required_statuses
        result['conditions']['political_status'] = current_status
        result['details'].append({'name': '政治面貌', 'matched': is_matched})
        if not is_matched:
            result['matched'] = False
            result['score'] -= 15
    
    return result


def calculate_gpa(student):
    """计算学生绩点"""
    from apps.academic.models import Grade
    grades = Grade.objects.filter(student=student)
    
    if not grades.exists():
        return 0.0
    
    total_points = sum(float(g.grade_point or 0) * float(g.course.credit) for g in grades if g.grade_point)
    total_credits = sum(float(g.course.credit) for g in grades)
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0


def calculate_avg_score(student):
    """计算平均分"""
    from apps.academic.models import Grade
    grades = Grade.objects.filter(student=student)
    
    if not grades.exists():
        return 0.0
    
    avg = grades.aggregate(Avg('score'))['score__avg']
    return round(avg, 2) if avg else 0.0


def check_has_fail(student):
    """检查是否有不及格"""
    from apps.academic.models import Grade
    return Grade.objects.filter(student=student, score__lt=60).exists()
