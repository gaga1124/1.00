<template>
  <el-dialog
    :title="notification?.title || '通知详情'"
    v-model="dialogVisible"
    width="900px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="notification-detail" v-if="notification">
      <!-- 头部信息 -->
      <div class="detail-header">
        <div class="header-row">
          <el-tag :type="getBusinessTypeType(notification.business_type)" size="small" effect="plain">
            <el-icon v-if="notification.business_type === 'workflow'"><DocumentChecked /></el-icon>
            <el-icon v-else-if="notification.business_type === 'file'"><Document /></el-icon>
            <el-icon v-else-if="notification.business_type === 'warning'"><Warning /></el-icon>
            <el-icon v-else-if="notification.business_type === 'activity'"><Calendar /></el-icon>
            <el-icon v-else-if="notification.business_type === 'academic'"><Reading /></el-icon>
            <el-icon v-else><Bell /></el-icon>
            {{ notification.business_type_display || '系统通知' }}
          </el-tag>
          <el-tag :type="getPriorityType(notification.priority)" size="small" class="ml-2">
            {{ notification.priority_display }}
          </el-tag>
          <el-tag :type="getStatusType(notification.status)" size="small" class="ml-2">
            {{ notification.status_display }}
          </el-tag>
          <el-tag v-if="notification.need_action" type="warning" size="small" effect="plain" class="ml-2">
            <el-icon><CircleCheck /></el-icon> 待办
          </el-tag>
        </div>
        <div class="header-row mt-2">
          <span class="sender-info">
            <el-icon><User /></el-icon>
            发送人：{{ notification.sender?.real_name || notification.sender?.username }}
          </span>
          <span class="time-info">
            <el-icon><Clock /></el-icon>
            {{ formatDate(notification.sent_at || notification.created_at) }}
          </span>
        </div>
      </div>

      <!-- 内容 -->
      <div class="detail-content">
        <div class="content-text">{{ notification.content }}</div>
      </div>

      <!-- 跳转链接 -->
      <div class="detail-link" v-if="notification.link_url">
        <el-alert type="info" :closable="false">
          <template #title>
            <div class="link-section">
              <span>相关链接：</span>
              <el-button type="primary" link @click="handleNavigate">
                <el-icon><Link /></el-icon>
                点击查看详情
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>

      <!-- 附件 -->
      <div class="detail-attachments" v-if="notification.attachments?.length > 0">
        <div class="section-title">
          <el-icon><Paperclip /></el-icon>
          附件 ({{ notification.attachments.length }})
        </div>
        <div class="attachment-list">
          <div
            v-for="att in notification.attachments"
            :key="att.id"
            class="attachment-item"
            @click="downloadAttachment(att)"
          >
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name">{{ att.filename }}</span>
            <span class="file-size">{{ att.file_size_display }}</span>
            <el-icon class="download-icon"><Download /></el-icon>
          </div>
        </div>
      </div>

      <!-- 阅读统计（仅发送者和管理员可见） -->
      <div class="detail-stats" v-if="canViewStats">
        <div class="section-title">
          <el-icon><View /></el-icon>
          阅读统计
          <el-button
            type="primary"
            link
            size="small"
            @click="fetchStats"
            :loading="statsLoading"
            class="refresh-btn"
          >
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>

        <div class="stats-overview" v-if="stats">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total_recipients }}</div>
            <div class="stat-label">总接收人</div>
          </div>
          <div class="stat-item">
            <div class="stat-value text-success">{{ stats.read_count }}</div>
            <div class="stat-label">已读</div>
          </div>
          <div class="stat-item">
            <div class="stat-value text-danger">{{ stats.unread_count }}</div>
            <div class="stat-label">未读</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.read_rate }}%</div>
            <div class="stat-label">阅读率</div>
          </div>
        </div>

        <el-tabs v-model="activeStatTab" class="stats-tabs" v-if="stats">
          <el-tab-pane :label="`已读 (${stats.read_users?.length || 0})`" name="read">
            <div class="user-list">
              <div v-if="stats.read_users?.length === 0" class="empty-text">暂无已读用户</div>
              <div
                v-for="record in stats.read_users"
                :key="record.id"
                class="user-item"
              >
                <el-avatar :size="32" :src="record.user?.avatar">
                  {{ record.user?.real_name?.[0] || record.user?.username?.[0] || 'U' }}
                </el-avatar>
                <span class="user-name">{{ record.user?.real_name || record.user?.username }}</span>
                <span class="read-time">{{ formatDate(record.read_at) }}</span>
                <el-tag v-if="record.read_device" size="small" type="info">{{ record.read_device }}</el-tag>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane :label="`未读 (${stats.unread_users?.length || 0})`" name="unread">
            <div class="user-list">
              <div v-if="stats.unread_users?.length === 0" class="empty-text">暂无未读用户</div>
              <div
                v-for="user in stats.unread_users"
                :key="user.id"
                class="user-item"
              >
                <el-avatar :size="32" :src="user?.avatar">
                  {{ user?.real_name?.[0] || user?.username?.[0] || 'U' }}
                </el-avatar>
                <span class="user-name">{{ user?.real_name || user?.username }}</span>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">
        <el-icon><Close /></el-icon> 关闭
      </el-button>
      <el-button
        v-if="notification?.status === 'sent' && !notification?.is_read"
        type="primary"
        @click="handleMarkAsRead"
      >
        <el-icon><Check /></el-icon> 标记为已读
      </el-button>
      <el-button
        v-if="notification?.need_action && !notification?.is_handled"
        type="warning"
        @click="handleHandle"
      >
        <el-icon><CircleCheck /></el-icon> 标记为已处理
      </el-button>
      <el-button
        v-if="notification?.link_url"
        type="success"
        @click="handleNavigate"
      >
        <el-icon><Link /></el-icon> 跳转处理
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Paperclip, Document, Download, View, User, Clock, 
  Link, Check, CircleCheck, Close, Refresh, Bell,
  DocumentChecked, Calendar, Reading, Warning
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const props = defineProps({
  visible: Boolean,
  notification: Object
})

const emit = defineEmits(['update:visible', 'read', 'handle'])

const router = useRouter()
const userStore = useUserStore()
const stats = ref(null)
const statsLoading = ref(false)
const activeStatTab = ref('read')

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 判断是否可以查看统计（发送者或管理员）
const canViewStats = computed(() => {
  if (!props.notification) return false
  return props.notification.sender?.id === userStore.user?.id || userStore.user?.is_superuser
})

const getBusinessTypeType = (type) => {
  const map = {
    system: 'info',
    workflow: 'primary',
    file: 'success',
    academic: 'warning',
    warning: 'danger',
    activity: 'primary',
    repair: 'info',
    resource: 'success',
    award: 'warning',
    career: 'info',
    party: 'danger',
    research: 'primary'
  }
  return map[type] || 'info'
}

const getPriorityType = (priority) => {
  const map = {
    normal: 'info',
    important: 'warning',
    urgent: 'danger'
  }
  return map[priority] || 'info'
}

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    sent: 'success',
    recalled: 'warning',
    deleted: 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const fetchStats = async () => {
  if (!props.notification?.id) return
  statsLoading.value = true
  try {
    const res = await api.get(`/notifications/${props.notification.id}/stats/`)
    stats.value = res.data
  } catch (e) {
    ElMessage.error('获取阅读统计失败')
  } finally {
    statsLoading.value = false
  }
}

const downloadAttachment = (attachment) => {
  if (!attachment.file_url) {
    ElMessage.error('附件链接不存在')
    return
  }
  
  // 创建临时链接下载
  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const handleMarkAsRead = () => {
  if (!props.notification?.id) return
  emit('read', props.notification.id)
  dialogVisible.value = false
}

const handleHandle = () => {
  if (!props.notification?.id) return
  emit('handle', props.notification)
  dialogVisible.value = false
}

const handleNavigate = () => {
  if (!props.notification?.link_url) return
  
  // 如果有链接参数，构建完整URL
  let url = props.notification.link_url
  if (props.notification.link_params && Object.keys(props.notification.link_params).length > 0) {
    const params = new URLSearchParams(props.notification.link_params)
    url += (url.includes('?') ? '&' : '?') + params.toString()
  }
  
  dialogVisible.value = false
  router.push(url)
}

// 监听对话框打开时获取统计
watch(() => props.visible, (val) => {
  if (val && props.notification && canViewStats.value) {
    fetchStats()
  }
})
</script>

<style scoped>
.notification-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.mt-2 {
  margin-top: 8px;
}

.ml-2 {
  margin-left: 8px;
}

.sender-info {
  color: #606266;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-info {
  color: #909399;
  font-size: 14px;
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-content {
  padding: 16px 0;
  min-height: 100px;
}

.content-text {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-link {
  margin-top: 16px;
}

.link-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-attachments {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 12px;
}

.refresh-btn {
  margin-left: auto;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.attachment-item:hover {
  background-color: #e4e7ed;
}

.file-icon {
  font-size: 20px;
  color: #409eff;
  margin-right: 12px;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.file-size {
  font-size: 12px;
  color: #909399;
  margin-right: 12px;
}

.download-icon {
  font-size: 16px;
  color: #409eff;
}

.detail-stats {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.stats-overview {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.text-success {
  color: #67c23a;
}

.stat-value.text-danger {
  color: #f56c6c;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stats-tabs :deep(.el-tabs__content) {
  max-height: 300px;
  overflow-y: auto;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-text {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.user-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

.read-time {
  font-size: 12px;
  color: #909399;
}
</style>
