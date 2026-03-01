<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">{{ greeting }}，{{ getUserName }} 👋</h1>
        <p class="welcome-subtitle">今天是 {{ currentDate }}，祝您工作顺利！</p>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <div class="stat-card blue">
        <div class="stat-icon">
          <el-icon :size="24"><Document /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审批</div>
        </div>
      </div>
      
      <div class="stat-card green">
        <div class="stat-icon">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      
      <div class="stat-card amber">
        <div class="stat-icon">
          <el-icon :size="24"><Bell /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.notifications }}</div>
          <div class="stat-label">待处理通知</div>
        </div>
      </div>
      
      <div class="stat-card purple">
        <div class="stat-icon">
          <el-icon :size="24"><Flag /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.tasks }}</div>
          <div class="stat-label">进行中任务</div>
        </div>
      </div>
    </div>

    <!-- 信息列表区域 -->
    <div class="info-section">
      <div class="section-header">
        <div class="section-title">
          <h3>信息</h3>
        </div>
        <el-button link class="filter-btn">
          <el-icon><Filter /></el-icon>
          筛选
        </el-button>
      </div>
      
      <!-- 列表容器 -->
      <div class="info-list">
        <div 
          class="info-card" 
          v-for="item in workItems" 
          :key="item.id"
        >
          <div class="info-icon" :class="item.type">
            <el-icon :size="20">
              <Message v-if="item.type === 'notice'" />
              <Document v-else-if="item.type === 'file'" />
              <Warning v-else-if="item.type === 'alert'" />
              <Bell v-else />
            </el-icon>
          </div>
          
          <div class="info-content">
            <div class="info-header">
              <span class="info-title">{{ item.title }}</span>
              <el-tag :type="getPriorityType(item.priority)" size="small" effect="dark">{{ item.priority }}</el-tag>
            </div>
            <div class="info-desc">{{ item.description }}</div>
            <div class="info-meta">
              <span class="info-sender">{{ item.sender }}</span>
              <span class="info-time">{{ item.time }}</span>
            </div>
          </div>
          
          <div class="info-status">
            <el-tag :type="getStatusType(item.status)" size="small">{{ item.status }}</el-tag>
          </div>
        </div>
      </div>
      
      <div class="pagination-section">
        <el-pagination
          :current-page="1"
          :page-size="5"
          :total="workItems.length"
          layout="prev, pager, next"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { 
  Document, 
  CircleCheck, 
  Bell, 
  Flag,
  Message,
  Warning,
  Filter
} from '@element-plus/icons-vue'

const userStore = useUserStore()

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
})

const getUserName = computed(() => {
  return userStore.user?.real_name || '老师'
})

const greeting = computed(() => {
  const now = new Date()
  const hour = now.getHours()
  if (hour < 6) {
    return '夜深了'
  } else if (hour < 12) {
    return '上午好'
  } else if (hour < 14) {
    return '中午好'
  } else if (hour < 18) {
    return '下午好'
  } else {
    return '晚上好'
  }
})

const stats = ref({
  pending: 12,
  completed: 8,
  notifications: 5,
  tasks: 3
})

const workItems = ref([
  {
    id: 1,
    type: 'notice',
    title: '关于召开2026年春季学期教学工作会议的通知',
    description: '各学院、各部门请准时参加，会议重要，请务必出席。',
    sender: '教务处',
    time: '10分钟前',
    status: '未读',
    priority: '高'
  },
  {
    id: 2,
    type: 'file',
    title: '科研项目结题报告已提交',
    description: '人工智能与大数据研究中心提交的结题报告已通过初审。',
    sender: '科研处',
    time: '30分钟前',
    status: '待处理',
    priority: '中'
  },
  {
    id: 3,
    type: 'alert',
    title: '成绩录入预警提醒',
    description: '您负责的课程尚有12名学生成绩未录入系统，请尽快完成。',
    sender: '教务系统',
    time: '1小时前',
    status: '紧急',
    priority: '高'
  },
  {
    id: 4,
    type: 'notice',
    title: '教师培训报名通知',
    description: '2026年信息化教学能力提升培训现在开始报名。',
    sender: '人事处',
    time: '2小时前',
    status: '已读',
    priority: '低'
  },
  {
    id: 5,
    type: 'file',
    title: '学生实习审批表',
    description: '计算机学院提交了25名学生实习审批申请。',
    sender: '就业中心',
    time: '3小时前',
    status: '待处理',
    priority: '中'
  }
])

const getStatusType = (status) => {
  const map = {
    '未读': 'info',
    '待处理': 'warning',
    '紧急': 'danger',
    '已读': 'success'
  }
  return map[status] || ''
}

const getPriorityType = (priority) => {
  const map = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return map[priority] || ''
}
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  background-color: #F8FAFC;
  min-height: 100%;
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: 32px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

/* 统计卡片区域 */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.stat-card.blue::before {
  background: linear-gradient(90deg, #3B82F6, #2563EB);
}

.stat-card.green::before {
  background: linear-gradient(90deg, #10B981, #059669);
}

.stat-card.amber::before {
  background: linear-gradient(90deg, #F59E0B, #D97706);
}

.stat-card.purple::before {
  background: linear-gradient(90deg, #8B5CF6, #7C3AED);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.blue .stat-icon {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
  color: #2563EB;
}

.stat-card.green .stat-icon {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
  color: #059669;
}

.stat-card.amber .stat-icon {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
  color: #D97706;
}

.stat-card.purple .stat-icon {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.05));
  color: #7C3AED;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #64748B;
  margin-top: 4px;
}

/* 信息列表区域 */
.info-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  border: 1px solid #E2E8F0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1E293B;
  margin: 0;
}

.filter-btn {
  color: #64748B;
  font-size: 14px;
}

/* 信息列表 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  transition: all 0.2s;
  cursor: pointer;
}

.info-card:hover {
  background: #F8FAFC;
  border-color: #2563EB;
  box-shadow: 0 2px 12px rgba(37, 99, 235, 0.1);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-icon.notice {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
  color: #2563EB;
}

.info-icon.file {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
  color: #059669;
}

.info-icon.alert {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
  color: #DC2626;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.info-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-desc {
  font-size: 13px;
  color: #64748B;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #94A3B8;
}

.info-sender {
  display: flex;
  align-items: center;
  gap: 4px;
}

.info-time::before {
  content: '•';
  margin-right: 16px;
}

.info-status {
  flex-shrink: 0;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #F1F5F9;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .welcome-title {
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  .info-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-status {
    align-self: flex-end;
  }
}
</style>
