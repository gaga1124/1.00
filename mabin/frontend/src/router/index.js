import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      { 
        path: 'summary',
        name: 'SummaryDashboard',
        component: () => import('@/views/summary/SummaryDashboard.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('@/views/students/StudentList.vue')
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('@/views/teachers/TeacherList.vue')
      },
      {
        path: 'students/records',
        name: 'StudentRecords',
        component: () => import('@/views/students/StudentRecords.vue')
      },
      {
        path: 'workflow',
        name: 'Workflow',
        component: () => import('@/views/workflow/WorkflowList.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'workflow/todos',
        name: 'WorkflowTodos',
        component: () => import('@/views/workflow/TodoList.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'resources',
        name: 'Resources',
        component: () => import('@/views/resources/ResourceList.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'resources/calendar',
        name: 'ResourceCalendar',
        component: () => import('@/views/resources/ResourceCalendar.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'approval',
        name: 'Approval',
        component: () => import('@/views/approval/ApprovalList.vue')
      },
      {
        path: 'repair',
        name: 'Repair',
        component: () => import('@/views/repair/RepairList.vue')
      },
      {
        path: 'approval/leave/create',
        name: 'LeaveApplication',
        component: () => import('@/views/approval/LeaveApplication.vue')
      },
      {
        path: 'approval/reimbursement/create',
        name: 'ReimbursementApplication',
        component: () => import('@/views/approval/ReimbursementApplication.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'approval/party/create',
        name: 'PartyMembershipApplication',
        component: () => import('@/views/approval/PartyMembershipApplication.vue'),
        meta: { allowedRoles: ['student'] }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue')
      },
      // 教务管理
      {
        path: 'academic/courses',
        name: 'CourseList',
        component: () => import('@/views/academic/CourseList.vue')
      },
      {
        path: 'academic/grades',
        name: 'GradeList',
        component: () => import('@/views/academic/GradeList.vue')
      },
      {
        path: 'academic/attendance',
        name: 'AttendanceList',
        component: () => import('@/views/academic/AttendanceList.vue')
      },
      {
        path: 'academic/live-checkin',
        name: 'LiveCheckIn',
        component: () => import('@/views/academic/LiveCheckIn.vue')
      },
      {
        path: 'academic/assignments',
        name: 'AssignmentList',
        component: () => import('@/views/academic/AssignmentList.vue')
      },
      {
        path: 'academic/assignments/:id',
        name: 'AssignmentDetail',
        component: () => import('@/views/academic/AssignmentDetail.vue')
      },
      // 科研管理
      {
        path: 'research/projects',
        name: 'ResearchProjectList',
        component: () => import('@/views/research/ResearchProjectList.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'research/achievements',
        name: 'ResearchAchievementList',
        component: () => import('@/views/research/ResearchAchievementList.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      {
        path: 'research/team',
        name: 'ResearchTeam',
        component: () => import('@/views/research/ResearchTeam.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      // 评奖评优
      {
        path: 'awards',
        name: 'AwardList',
        component: () => import('@/views/awards/AwardList.vue')
      },
      // 就业服务
      {
        path: 'career/jobs',
        name: 'JobList',
        component: () => import('@/views/career/JobList.vue')
      },
      {
        path: 'career/applications',
        name: 'CareerApplications',
        component: () => import('@/views/career/ApplicationList.vue')
      },
      {
        path: 'career/job-fairs',
        name: 'JobFairList',
        component: () => import('@/views/career/JobFairList.vue')
      },
      {
        path: 'career/stats',
        name: 'EmploymentStats',
        component: () => import('@/views/career/EmploymentStats.vue'),
        meta: { allowedRoles: ['admin', 'teacher'] }
      },
      // 党建团建
      {
        path: 'party/members',
        name: 'PartyMembers',
        component: () => import('@/views/party/MemberList.vue')
      },
      {
        path: 'party/activities',
        name: 'PartyActivities',
        component: () => import('@/views/party/ActivityList.vue')
      },
      // 活动实践
      {
        path: 'activities/social',
        name: 'SocialPractice',
        component: () => import('@/views/activities/SocialPracticeList.vue')
      },
      {
        path: 'activities/competitions',
        name: 'CompetitionList',
        component: () => import('@/views/activities/CompetitionList.vue')
      },
      {
        path: 'activities/dynamic',
        name: 'DynamicActivity',
        component: () => import('@/views/activities/DynamicActivityList.vue')
      },
      // 数据分析
      {
        path: 'analysis',
        name: 'AnalysisDashboard',
        component: () => import('@/views/analysis/AnalysisDashboard.vue')
      },
      // 权限管理
      {
        path: 'rbac',
        name: 'RBAC',
        component: () => import('@/views/rbac/UserList.vue'),
        meta: { requiresAdmin: true }
      },
      // 通知管理
      {
        path: 'notifications',
        name: 'NotificationList',
        component: () => import('@/views/notifications/NotificationList.vue')
      },
      // 文件系统 - 签章
      {
        path: 'electronic-signature/signature',
        name: 'ElectronicSignature',
        component: () => import('@/views/electronic-signature/FileList.vue')
      },
      // 文件系统 - 留档
      {
        path: 'electronic-signature/archive',
        name: 'ElectronicArchive',
        component: () => import('@/views/electronic-signature/ArchiveList.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 已登录但用户信息未加载时，先拉取用户信息
  if (userStore.isAuthenticated && !userStore.user) {
    try {
      await userStore.fetchUserInfo()
    } catch (e) {
      userStore.logout()
    }
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/')
  } else if (to.meta.requiresAdmin && userStore.user?.role !== 'admin') {
    next({ name: 'Dashboard' })
  } else if (to.meta.allowedRoles && !to.meta.allowedRoles.includes(userStore.user?.role)) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
