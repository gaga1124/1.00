# 学院OA系统功能代码文件映射表

本文档详细列出了系统各功能模块对应的其前端页面组件和后端代码文件位置。

> **文件路径说明：**
> - 前端文件路径基于项目根目录。
> - 后端文件路径基于 `backend/apps/` 目录。
> - 后端核心文件通常包含：`models.py` (数据模型), `serializers.py` (序列化器), `views.py` (视图/控制器), `urls.py` (路由)。

## 1. 认证与核心用户模块 (Authentication & Core Users)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 (models/serializers/views/urls) |
| :--- | :--- | :--- | :--- | :--- |
| **用户登录** | `/login` | `frontend/src/views/Login.vue` | `users` | `views.py` (LoginSerializer, UserViewSet) <br> `urls.py` |
| **仪表盘** | `/dashboard` | `frontend/src/views/Dashboard.vue` | - | - |
| **个人资料** | `/profile` | `frontend/src/views/Profile.vue` | `users` | `models.py` (UserProfile) <br> `serializers.py` (UserProfileSerializer) <br> `views.py` (UserProfileViewSet) |
| **用户管理** | `/rbac` | `frontend/src/views/rbac/UserList.vue` | `users` | `models.py` (User) <br> `serializers.py` (UserSerializer) <br> `views.py` (UserViewSet) |
| **教师管理** | `/teachers` | `frontend/src/views/teachers/TeacherList.vue` | `users` | `models.py` (User, UserProfile) <br> `serializers.py` (TeacherSerializer) <br> `views.py` (TeacherViewSet) |
| **权限/角色管理** | - | (集成在 RBAC 模块中) | `rbac` | `models.py` (Role, Permission, Department) <br> `serializers.py` <br> `views.py` (RoleViewSet, DepartmentViewSet) <br> `urls.py` |

## 2. 学生管理模块 (Student Management)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **学生列表** | `/students` | `frontend/src/views/students/StudentList.vue` | `students` | `models.py` (Student) <br> `serializers.py` (StudentSerializer) <br> `views.py` (StudentViewSet) <br> `urls.py` |
| **学生档案/记录** | `/students/records` | `frontend/src/views/students/StudentRecords.vue` | `students` | `models.py` (StudentRecord) <br> `serializers.py` (StudentRecordSerializer) <br> `views.py` (StudentRecordViewSet) |

## 3. 工作流模块 (Workflow)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **工作流配置** | `/workflow` | `frontend/src/views/workflow/WorkflowList.vue` | `workflow` | `models.py` (Workflow, WorkflowNode) <br> `serializers.py` <br> `views.py` (WorkflowViewSet, WorkflowNodeViewSet) <br> `urls.py` |
| **待办事项** | `/workflow/todos` | `frontend/src/views/workflow/TodoList.vue` | `workflow` | `models.py` (WorkflowInstance) <br> `serializers.py` <br> `views.py` (WorkflowInstanceViewSet) |

## 4. 审批模块 (Approval)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **审批列表** | `/approval` | `frontend/src/views/approval/ApprovalList.vue` | `approval` | `models.py` <br> `views.py` <br> `urls.py` |
| **请假申请** | `/approval/leave/create` | `frontend/src/views/approval/LeaveApplication.vue` | `approval` | `models.py` (LeaveApplication) <br> `serializers.py` <br> `views.py` (LeaveApplicationViewSet) |
| **报销申请** | `/approval/reimbursement/create` | `frontend/src/views/approval/ReimbursementApplication.vue` | `approval` | `models.py` (ReimbursementApplication) <br> `serializers.py` <br> `views.py` (ReimbursementApplicationViewSet) |

## 5. 资源管理模块 (Resources)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **资源列表** | `/resources` | `frontend/src/views/resources/ResourceList.vue` | `resources` | `models.py` (Resource) <br> `serializers.py` <br> `views.py` (ResourceViewSet) <br> `urls.py` |
| **资源日历** | `/resources/calendar` | `frontend/src/views/resources/ResourceCalendar.vue` | `resources` | `models.py` (ResourceBooking) <br> `serializers.py` <br> `views.py` (ResourceBookingViewSet) |

## 6. 报修模块 (Repair)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **报修列表** | `/repair` | `frontend/src/views/repair/RepairList.vue` | `repair` | `models.py` (RepairApplication) <br> `serializers.py` <br> `views.py` (RepairApplicationViewSet) <br> `urls.py` |
| **报修表单** | - | `frontend/src/views/repair/RepairForm.vue` | `repair` | `models.py` (RepairApplication) <br> `views.py` |
| **报修详情** | - | `frontend/src/views/repair/RepairDetail.vue` | `repair` | `models.py` (RepairRecord) <br> `views.py` (RepairRecordViewSet) |

## 7. 教务管理模块 (Academic)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **课程管理** | `/academic/courses` | `frontend/src/views/academic/CourseList.vue` | `academic` | `models.py` (Course) <br> `serializers.py` (CourseSerializer) <br> `views.py` (CourseViewSet) <br> `urls.py` |
| **成绩管理** | `/academic/grades` | `frontend/src/views/academic/GradeList.vue` | `academic` | `models.py` (Grade) <br> `serializers.py` (GradeSerializer) <br> `views.py` (GradeViewSet) |
| **考勤管理** | `/academic/attendance` | `frontend/src/views/academic/AttendanceList.vue` | `academic` | `models.py` (Attendance) <br> `serializers.py` (AttendanceSerializer) <br> `views.py` (AttendanceViewSet) |
| **作业列表** | `/academic/assignments` | `frontend/src/views/academic/AssignmentList.vue` | `academic` | `models.py` (Assignment - 若存在) <br> `views.py` |
| **作业详情** | `/academic/assignments/:id` | `frontend/src/views/academic/AssignmentDetail.vue` | `academic` | `views.py` |

## 8. 科研管理模块 (Research)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **科研项目** | `/research/projects` | `frontend/src/views/research/ResearchProjectList.vue` | `research` | `models.py` (ResearchProject) <br> `serializers.py` <br> `views.py` (ResearchProjectViewSet) <br> `urls.py` |
| **科研成果** | `/research/achievements` | `frontend/src/views/research/ResearchAchievementList.vue` | `research` | `models.py` (ResearchAchievement) <br> `views.py` (ResearchAchievementViewSet) |
| **科研团队** | `/research/team` | `frontend/src/views/research/ResearchTeam.vue` | `research` | `models.py` (ResearchTeam, TeamTask) <br> `views.py` (ResearchTeamViewSet) |

## 9. 评奖评优模块 (Awards)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **奖项列表** | `/awards` | `frontend/src/views/awards/AwardList.vue` | `awards` | `models.py` (AwardType, AwardApplication) <br> `serializers.py` <br> `views.py` (AwardApplicationViewSet) <br> `urls.py` |

## 10. 就业服务模块 (Career)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **职位列表** | `/career/jobs` | `frontend/src/views/career/JobList.vue` | `career` | `models.py` (JobPosting, Company) <br> `views.py` (JobPostingViewSet) <br> `urls.py` |
| **申请记录** | `/career/applications` | `frontend/src/views/career/ApplicationList.vue` | `career` | `models.py` (JobApplication) <br> `views.py` (JobApplicationViewSet) |
| **招聘会** | `/career/job-fairs` | `frontend/src/views/career/JobFairList.vue` | `career` | `models.py` (JobFair) <br> `views.py` (JobFairViewSet) |
| **就业统计** | `/career/stats` | `frontend/src/views/career/EmploymentStats.vue` | `career` | `views.py` (EmploymentStatisticsViewSet) |

## 11. 党团建设模块 (Party)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **党员列表** | `/party/members` | `frontend/src/views/party/MemberList.vue` | `party` | `models.py` (PartyMember, PartyBranch) <br> `views.py` (PartyMemberViewSet) <br> `urls.py` |
| **党团活动** | `/party/activities` | `frontend/src/views/party/ActivityList.vue` | `party` | `models.py` (PartyActivity) <br> `views.py` (PartyActivityViewSet) |

## 12. 活动实践模块 (Activities)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **社会实践** | `/activities/social` | `frontend/src/views/activities/SocialPracticeList.vue` | `activities` | `models.py` (SocialPractice) <br> `views.py` (SocialPracticeViewSet) <br> `urls.py` |
| **学科竞赛** | `/activities/competitions` | `frontend/src/views/activities/CompetitionList.vue` | `activities` | `models.py` (Competition) <br> `views.py` (CompetitionViewSet) |
| **动态活动** | `/activities/dynamic` | `frontend/src/views/activities/DynamicActivityList.vue` | `activities` | `models.py` (DynamicActivity) <br> `views.py` (DynamicActivityInstanceViewSet) |

## 13. 数据分析模块 (Analysis)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **数据大屏** | `/analysis` | `frontend/src/views/analysis/AnalysisDashboard.vue` | `analysis` | `views.py` (DashboardStatsView) <br> `urls.py` |

## 14. 系统通知模块 (Notifications)

| 功能名称 | 前端路由 | 前端组件文件 | 后端应用 | 后端核心文件 |
| :--- | :--- | :--- | :--- | :--- |
| **通知列表** | `/notifications` | `frontend/src/views/system/NotificationList.vue` | `notifications` | `models.py` (Notification) <br> `serializers.py` (NotificationSerializer) <br> `views.py` (NotificationViewSet) <br> `urls.py` |
| **通知模板** | `/notifications/templates` | `frontend/src/views/system/NotificationTemplateList.vue` | `notifications` | `models.py` (NotificationTemplate) <br> `views.py` (NotificationTemplateViewSet) |
| **发送通知** | `/notifications/send` | `frontend/src/views/system/NotificationSend.vue` | `notifications` | `views.py` (NotificationViewSet) |

---
*注：后端文件路径均基于 `backend/apps/` 目录；前端文件路径基于项目根目录。*
