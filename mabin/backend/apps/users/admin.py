from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.admin.helpers import ActionForm
from django.contrib.admin.helpers import ActionForm
from .models import User, UserProfile
from apps.rbac.models import Role, UserRole


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    raw_id_fields = ['role']


class RoleActionForm(ActionForm):
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True), required=True, label='角色')
    mode = forms.ChoiceField(
        choices=[('add', '添加到角色'), ('remove', '从角色移除'), ('set', '设为唯一角色')],
        required=True,
        label='操作方式'
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'real_name', 'email', 'department', 'roles_display', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'department', 'created_at']
    search_fields = ['username', 'real_name', 'email', 'phone']
    ordering = ['-created_at']
    inlines = [UserRoleInline]
    action_form = RoleActionForm
    actions = ['bulk_modify_role']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('real_name', 'gender', 'phone', 'avatar', 'department')
        }),
    )
    
    def roles_display(self, obj):
        roles = Role.objects.filter(user_roles__user=obj).values_list('name', flat=True)
        return '、'.join(roles) if roles else '-'
    roles_display.short_description = '角色'
    
    def bulk_modify_role(self, request, queryset):
        role_id = request.POST.get('role')
        mode = request.POST.get('mode')
        try:
            role = Role.objects.get(pk=role_id)
        except (Role.DoesNotExist, ValueError, TypeError):
            self.message_user(request, '请选择有效的角色', level='error')
            return
        
        added, removed, set_count = 0, 0, 0
        if mode == 'set':
            for user in queryset:
                UserRole.objects.filter(user=user).delete()
            set_count = queryset.count()
            for user in queryset:
                UserRole.objects.get_or_create(user=user, role=role)
        elif mode == 'add':
            for user in queryset:
                _, created = UserRole.objects.get_or_create(user=user, role=role)
                if created:
                    added += 1
        elif mode == 'remove':
            for user in queryset:
                removed += UserRole.objects.filter(user=user, role=role).delete()[0]
        else:
            self.message_user(request, '无效的操作方式', level='error')
            return
        
        if mode == 'set':
            self.message_user(request, f'已为 {set_count} 位用户设置唯一角色：{role.name}')
        elif mode == 'add':
            self.message_user(request, f'已为 {added} 位用户添加角色：{role.name}')
        elif mode == 'remove':
            self.message_user(request, f'已为 {removed} 条用户-角色关系移除角色：{role.name}')
    bulk_modify_role.short_description = '批量修改角色（选择角色与操作方式）'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'job_title', 'employee_id', 'created_at']
    search_fields = ['user__username', 'user__real_name', 'employee_id']
    raw_id_fields = ['user']
