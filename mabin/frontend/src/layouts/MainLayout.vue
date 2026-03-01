<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
      <div class="logo">
        <div class="logo-content">
          <div class="logo-icon">
            <el-icon :size="isCollapse ? 28 : 32"><School /></el-icon>
          </div>
          <h2 v-if="!isCollapse" class="logo-text">学院OA</h2>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#1E40AF"
        text-color="#94A3B8"
        active-text-color="#FFFFFF"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        
        <el-sub-menu index="students" v-if="isStaff">
          <template #title>
            <el-icon><User /></el-icon>
            <span>学生管理</span>
          </template>
          <el-menu-item index="/students">学生列表</el-menu-item>
          <el-menu-item index="/students/records">档案记录</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/teachers" v-if="isAdmin">
          <el-icon><Avatar /></el-icon>
          <span>教师管理</span>
        </el-menu-item>
        
        <el-sub-menu index="workflow" v-if="isStaff">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>申请审批</span>
          </template>
          <el-menu-item index="/workflow" v-if="isAdmin">流程配置</el-menu-item>
          <el-menu-item index="/workflow/todos">我的待办</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/repair" v-if="isStaff">
          <el-icon><Tools /></el-icon>
          <span>报修服务</span>
        </el-menu-item>
        
        <el-sub-menu index="resources" v-if="isStaff">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>资源预约</span>
          </template>
          <el-menu-item index="/resources">资源列表</el-menu-item>
          <el-menu-item index="/resources/calendar">预约日历</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="approval">
          <template #title>
            <el-icon><Check /></el-icon>
            <span>申请审批</span>
          </template>
          <el-menu-item index="/approval">我的申请</el-menu-item>
          <el-menu-item index="/awards">评奖评优</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="academic">
          <template #title>
            <el-icon><Reading /></el-icon>
            <span>教务管理</span>
          </template>
          <el-menu-item index="/academic/courses">课程管理</el-menu-item>
          <el-menu-item index="/academic/grades">成绩查询</el-menu-item>
          <el-menu-item index="/academic/attendance" v-if="isStaff">课堂签到</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="research" v-if="isStaff">
          <template #title>
            <el-icon><Opportunity /></el-icon>
            <span>活动实践</span>
          </template>
          <el-menu-item index="/research/projects">项目管理</el-menu-item>
          <el-menu-item index="/research/achievements">科研成果</el-menu-item>
          <el-menu-item index="/research/team">团队协作</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="career">
          <template #title>
            <el-icon><Briefcase /></el-icon>
            <span>就业服务</span>
          </template>
          <el-menu-item index="/career/jobs">招聘信息</el-menu-item>
          <el-menu-item index="/career/applications">我的投递</el-menu-item>
          <el-menu-item index="/career/job-fairs">招聘会</el-menu-item>
          <el-menu-item index="/career/stats" v-if="isStaff">就业统计</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="party">
          <template #title>
            <el-icon><Flag /></el-icon>
            <span>党建团建</span>
          </template>
          <el-menu-item index="/party/members">成员管理</el-menu-item>
          <el-menu-item index="/party/activities">组织生活</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="activities">
          <template #title>
            <el-icon><Star /></el-icon>
            <span>校园活动</span>
          </template>
          <el-menu-item index="/activities/social">社会实践</el-menu-item>
          <el-menu-item index="/activities/competitions">学科竞赛</el-menu-item>
          <el-menu-item index="/activities/dynamic">校内活动</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <span>信息通知</span>
        </el-menu-item>

        <el-sub-menu index="filesystem" v-if="isStaff">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>文件系统</span>
          </template>
          <el-menu-item index="/electronic-signature/signature">签章</el-menu-item>
          <el-menu-item index="/electronic-signature/archive">留档</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/analysis" v-if="isAdmin">
          <el-icon><DataLine /></el-icon>
          <span>数据分析</span>
        </el-menu-item>

        <el-menu-item index="/rbac" v-if="isAdmin">
          <el-icon><Setting /></el-icon>
          <span>权限管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container class="main-container">
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <div class="search-box">
            <el-input
              v-model="searchText"
              placeholder="快捷搜索 (Ctrl + K)"
              prefix-icon="Search"
              class="search-input"
            />
          </div>
        </div>
        <div class="header-right">
          <div class="notification-item" @click="$router.push('/notifications')">
            <el-badge :value="notificationStore.unreadCount" :hidden="notificationStore.unreadCount === 0" :max="99">
              <el-icon class="header-icon"><Bell /></el-icon>
            </el-badge>
          </div>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="36" :src="userStore.user?.avatar">
                {{ userStore.user?.real_name?.[0] || 'U' }}
              </el-avatar>
              <div class="user-details">
                <span class="username">{{ userStore.user?.real_name || '用户' }}</span>
                <span class="user-role">{{ getUserRole }}</span>
              </div>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <keep-alive>
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { School, Expand, Fold, Bell, User, SwitchButton, Folder, House, Avatar, Document, Tools, OfficeBuilding, Check, Reading, Opportunity, Briefcase, Flag, Star, DataLine, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const notificationStore = useNotificationStore()
const searchText = ref('')

const isCollapse = ref(false)

const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.is_staff === true || userStore.user?.is_superuser === true)
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStudent = computed(() => userStore.user?.role === 'student')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const activeMenu = computed(() => route.path)

const getUserRole = computed(() => {
  const role = userStore.user?.role
  const roleMap = {
    'admin': '管理员',
    'teacher': '教师',
    'student': '学生',
    'staff': '职工'
  }
  return roleMap[role] || '用户'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  notificationStore.fetchUnreadCount()
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background-color: #1E40AF;
  overflow-x: hidden;
  transition: width 0.3s;
  border-right: none;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 20px;
  background-color: #1E40AF;
}

.logo-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #2563EB;
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

.logo-text {
  margin: 0;
  color: #FFFFFF;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  border: none;
  padding-top: 16px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  margin: 4px 12px !important;
  border-radius: 8px;
  height: 44px !important;
  line-height: 44px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  box-sizing: border-box;
}

.sidebar-menu .el-menu-item > .el-icon,
.sidebar-menu .el-menu-item > .el-icon + span,
.sidebar-menu .el-sub-menu__title > .el-icon,
.sidebar-menu .el-sub-menu__title > span {
  display: inline-flex !important;
  align-items: center !important;
}

.sidebar-menu .el-menu-item .el-icon,
.sidebar-menu .el-sub-menu__title .el-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 24px;
  height: 44px;
  margin-right: 8px;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-menu .el-menu-item.is-active,
.sidebar-menu .el-sub-menu .el-menu-item.is-active {
  background-color: #2563EB;
  color: #FFFFFF;
}

.sidebar-menu .el-sub-menu.is-active > .el-sub-menu__title {
  background-color: #2563EB;
  color: #FFFFFF;
}

.main-container {
  background-color: #F8FAFC;
}

.header {
  background-color: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  color: #64748B;
  transition: color 0.2s;
}

.collapse-icon:hover {
  color: #1E40AF;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.search-input :deep(.el-input__wrapper) {
  background-color: #F1F5F9;
  border-radius: 8px;
  box-shadow: none;
  padding: 6px 12px;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #2563EB inset;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #2563EB inset;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-item {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  transition: all 0.2s;
}

.notification-item:hover {
  background-color: #F8FAFC;
  border-color: #2563EB;
}

.header-icon {
  font-size: 22px;
  color: #64748B;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #F1F5F9;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  color: #1E293B;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.2;
}

.user-role {
  color: #64748B;
  font-size: 12px;
  line-height: 1.2;
}

.main {
  background-color: #F8FAFC;
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
