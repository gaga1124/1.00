<template>
  <div class="notification-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">通知中心</span>
            <div class="badge-group">
              <el-badge :value="unreadCount" v-if="unreadCount > 0" class="unread-badge">
                <el-tag type="danger" effect="plain" size="small">未读</el-tag>
              </el-badge>
              <el-badge :value="todoCount" v-if="todoCount > 0" class="todo-badge">
                <el-tag type="warning" effect="plain" size="small">待办</el-tag>
              </el-badge>
            </div>
          </div>
          <div class="header-right">
            <el-radio-group v-model="activeTab" size="small" @change="handleTabChange">
              <el-radio-button label="received">
                <el-icon><Message /></el-icon> 我收到的
              </el-radio-button>
              <el-radio-button label="todos">
                <el-icon><Bell /></el-icon> 待办事项
              </el-radio-button>
              <el-radio-button label="sent">
                <el-icon><Promotion /></el-icon> 我发送的
              </el-radio-button>
              <el-radio-button label="draft">
                <el-icon><Document /></el-icon> 草稿箱
              </el-radio-button>
            </el-radio-group>
            <el-button type="primary" @click="handleCreate" v-if="canSend">
              <el-icon><Plus /></el-icon>
              发送通知
            </el-button>
          </div>
        </div>
      </template>

      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索通知标题或内容"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="businessTypeFilter" placeholder="业务类型" clearable style="width: 140px">
          <el-option label="系统通知" value="system" />
          <el-option label="流程审批" value="workflow" />
          <el-option label="文件签章" value="file" />
          <el-option label="教务通知" value="academic" />
          <el-option label="预警提醒" value="warning" />
          <el-option label="活动通知" value="activity" />
          <el-option label="报修服务" value="repair" />
          <el-option label="资源预约" value="resource" />
          <el-option label="评奖评优" value="award" />
          <el-option label="就业服务" value="career" />
          <el-option label="党建团建" value="party" />
          <el-option label="科研管理" value="research" />
        </el-select>
        
        <el-select v-model="priorityFilter" placeholder="重要等级" clearable style="width: 120px">
          <el-option label="普通" value="normal" />
          <el-option label="重要" value="important" />
          <el-option label="紧急" value="urgent" />
        </el-select>
        
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px" v-if="activeTab === 'received' || activeTab === 'todos'">
          <el-option label="未读" value="unread" />
          <el-option label="已读" value="read" />
        </el-select>
        
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          clearable
          style="width: 260px"
        />
        
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <el-button @click="handleReset">
          <el-icon><RefreshRight /></el-icon> 重置
        </el-button>
        
        <el-button type="success" link @click="handleMarkAllAsRead" v-if="activeTab === 'received' && unreadCount > 0">
          <el-icon><Check /></el-icon> 全部已读
        </el-button>
      </div>

      <div class="batch-actions" v-if="selectedRows.length > 0">
        <span class="selected-info">已选择 {{ selectedRows.length }} 项</span>
        <el-button type="primary" link size="small" @click="handleBatchMarkAsRead" v-if="activeTab === 'received' || activeTab === 'todos'">
          <el-icon><Check /></el-icon> 批量标记已读
        </el-button>
        <el-button type="danger" link size="small" @click="handleBatchDelete" v-if="activeTab !== 'received' && activeTab !== 'todos'">
          <el-icon><Delete /></el-icon> 批量删除
        </el-button>
        <el-button link size="small" @click="selectedRows = []">
          <el-icon><Close /></el-icon> 取消选择
        </el-button>
      </div>

      <el-table
        :data="notifications"
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        :empty-text="emptyText"
        :row-class-name="getRowClassName"
      >
        <el-table-column type="selection" width="55" v-if="activeTab !== 'received' && activeTab !== 'todos'" />
        <el-table-column type="index" width="50" />
        
        <el-table-column label="业务类型" width="100">
          <template #default="{ row }">
            <span>{{ row.business_type_display || '系统' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span v-if="row.status === 'sent' && !row.is_read">未读</span>
            <span v-else-if="row.status === 'sent' && row.is_read">已读</span>
            <span v-else-if="row.status === 'recalled'">已撤回</span>
            <span v-else-if="row.status === 'draft'">草稿</span>
            <span v-if="row.need_action && !row.is_handled">待办</span>
          </template>
        </el-table-column>
        
        <el-table-column label="重要等级" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small" effect="plain">
              {{ row.priority_display }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="title-cell" @click="handleView(row)" style="cursor: pointer;">
              <el-icon v-if="row.priority === 'urgent'" class="urgent-icon" color="#f56c6c"><WarningFilled /></el-icon>
              <span :class="{ 'unread-title': (activeTab === 'received' || activeTab === 'todos') && !row.is_read }">
                {{ row.title }}
              </span>
              <el-icon v-if="row.attachment_count > 0" class="attachment-icon"><Paperclip /></el-icon>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="sender.real_name" label="发送人" width="100" v-if="activeTab === 'received' || activeTab === 'todos'" />
        
        <el-table-column label="接收人数" width="100" v-if="activeTab !== 'received' && activeTab !== 'todos'">
          <template #default="{ row }">
            <span v-if="row.total_recipients > 0">
              {{ row.read_count }}/{{ row.total_recipients }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="已读率" width="120" v-if="activeTab !== 'received' && activeTab !== 'todos'">
          <template #default="{ row }">
            <div class="progress-cell">
              <el-progress
                v-if="row.total_recipients > 0"
                :percentage="Math.round((row.read_count / row.total_recipients) * 100)"
                :stroke-width="6"
                :show-text="true"
                :color="getProgressColor(row.read_count, row.total_recipients)"
              />
              <span v-else>-</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">
            <div class="time-cell">
              <div class="date-text">{{ formatDate(row.created_at) }}</div>
              <div class="time-text">{{ formatTime(row.created_at) }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              <el-icon><View /></el-icon> 查看
            </el-button>
            
            <el-button 
              v-if="(activeTab === 'received' || activeTab === 'todos') && !row.is_read" 
              type="success" 
              link 
              size="small" 
              @click="handleMarkAsRead(row.id)"
            >
              <el-icon><Check /></el-icon> 标记已读
            </el-button>
            
            <el-button 
              v-if="activeTab === 'todos' && row.need_action && !row.is_handled" 
              type="warning" 
              link 
              size="small" 
              @click="handleHandle(row)"
            >
              <el-icon><CircleCheck /></el-icon> 处理
            </el-button>
            
            <el-button 
              v-if="row.link_url" 
              type="info" 
              link 
              size="small" 
              @click="handleNavigate(row)"
            >
              <el-icon><Link /></el-icon> 跳转
            </el-button>
            
            <el-button 
              v-if="activeTab === 'draft'" 
              type="primary" 
              link 
              size="small" 
              @click="handleEdit(row)"
            >
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            
            <el-button 
              v-if="activeTab === 'draft'" 
              type="success" 
              link 
              size="small" 
              @click="handleSend(row)"
            >
              <el-icon><Promotion /></el-icon> 发送
            </el-button>
            
            <el-button 
              v-if="activeTab === 'sent' && row.can_recall" 
              type="warning" 
              link 
              size="small" 
              @click="handleRecall(row)"
            >
              <el-icon><RefreshLeft /></el-icon> 撤回
            </el-button>
            
            <el-button 
              v-if="(activeTab === 'draft' || row.can_delete) && activeTab !== 'received' && activeTab !== 'todos'" 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑通知对话框 -->
    <NotificationFormDialog
      v-model:visible="formVisible"
      :edit-data="editData"
      @success="handleFormSuccess"
    />

    <!-- 通知详情对话框 -->
    <NotificationDetailDialog
      v-model:visible="detailVisible"
      :notification="currentNotification"
      @read="handleMarkAsRead"
      @handle="handleDetailHandle"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Paperclip, WarningFilled, Message, Bell, Promotion, 
  Document, DocumentChecked, Calendar, Reading, View, Check, 
  CircleCheck, Link, Edit, RefreshLeft, Delete, Close, RefreshRight 
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import NotificationFormDialog from './NotificationFormDialog.vue'
import NotificationDetailDialog from './NotificationDetailDialog.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const activeTab = ref('received')
const searchQuery = ref('')
const businessTypeFilter = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const unreadCount = ref(0)
const todoCount = ref(0)

const notifications = ref([])
const selectedRows = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const formVisible = ref(false)
const detailVisible = ref(false)
const editData = ref(null)
const currentNotification = ref(null)

// 判断是否可以发送通知（管理员、教师、职工）
const canSend = computed(() => {
  const role = userStore.user?.role
  return ['admin', 'teacher', 'staff'].includes(role)
})

// 空数据提示
const emptyText = computed(() => {
  if (loading.value) return '加载中...'
  if (searchQuery.value || priorityFilter.value || businessTypeFilter.value || dateRange.value?.length > 0) {
    return '暂无符合条件的通知'
  }
  const map = {
    received: '暂无收到的通知',
    todos: '暂无待办事项',
    sent: '暂无发送的通知',
    draft: '暂无草稿'
  }
  return map[activeTab.value] || '暂无数据'
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

const getProgressColor = (read, total) => {
  if (total === 0) return '#409eff'
  const rate = read / total
  if (rate < 0.3) return '#f56c6c'
  if (rate < 0.7) return '#e6a23c'
  return '#67c23a'
}

const getRowClassName = ({ row }) => {
  if ((activeTab.value === 'received' || activeTab.value === 'todos') && !row.is_read) {
    return 'unread-row'
  }
  return ''
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatTime = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    let url = '/notifications/'
    if (activeTab.value === 'sent') {
      url = '/notifications/sent/'
    } else if (activeTab.value === 'draft') {
      url = '/notifications/draft/'
    } else if (activeTab.value === 'todos') {
      url = '/notifications/todos/'
    }
    
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: searchQuery.value,
      ordering: '-created_at'
    }
    
    if (businessTypeFilter.value) {
      params.business_type = businessTypeFilter.value
    }
    
    if (priorityFilter.value) {
      params.priority = priorityFilter.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 状态筛选（仅针对收到的通知和待办）
    if ((activeTab.value === 'received' || activeTab.value === 'todos') && statusFilter.value) {
      if (statusFilter.value === 'unread') {
        params.is_read = false
      } else if (statusFilter.value === 'read') {
        params.is_read = true
      }
    }
    
    const res = await api.get(url, { params })
    notifications.value = res.data?.results || res.data || []
    pagination.total = res.data?.count || 0
    selectedRows.value = []
  } catch (e) {
    ElMessage.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

const fetchUnreadCount = async () => {
  try {
    const res = await api.get('/notifications/unread_count/')
    unreadCount.value = res.data?.unread_count || 0
    todoCount.value = res.data?.todo_count || 0
  } catch (e) {
    console.error('获取未读数量失败', e)
  }
}

const handleTabChange = () => {
  pagination.page = 1
  searchQuery.value = ''
  businessTypeFilter.value = ''
  priorityFilter.value = ''
  statusFilter.value = ''
  dateRange.value = []
  fetchNotifications()
}

const handleSearch = () => {
  pagination.page = 1
  fetchNotifications()
}

const handleReset = () => {
  searchQuery.value = ''
  businessTypeFilter.value = ''
  priorityFilter.value = ''
  statusFilter.value = ''
  dateRange.value = []
  pagination.page = 1
  fetchNotifications()
}

const handleSizeChange = () => {
  fetchNotifications()
}

const handlePageChange = () => {
  fetchNotifications()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleMarkAllAsRead = async () => {
  try {
    await ElMessageBox.confirm('确定要将所有通知标记为已读吗？', '全部已读', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await api.post('/notifications/mark_all_as_read/')
    ElMessage.success(res.data?.message || '已全部标记为已读')
    fetchNotifications()
    fetchUnreadCount()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleBatchMarkAsRead = async () => {
  if (selectedRows.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(`确定要将选中的 ${selectedRows.value.length} 条通知标记为已读吗？`, '批量操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const notificationIds = selectedRows.value.map(row => row.id)
    const res = await api.post('/notifications/batch_mark_as_read/', {
      notification_ids: notificationIds
    })
    
    ElMessage.success(res.data?.message || `已将 ${selectedRows.value.length} 条通知标记为已读`)
    selectedRows.value = []
    fetchNotifications()
    fetchUnreadCount()
  } catch (e) {
    if (e !== 'cancel') {
      const errorMsg = e.response?.data?.error || '批量标记已读失败'
      ElMessage.error(errorMsg)
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条通知吗？`, '批量操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    })
    
    const promises = selectedRows.value.map(row => 
      api.delete(`/notifications/${row.id}/`)
    )
    
    await Promise.all(promises)
    ElMessage.success(`已删除 ${selectedRows.value.length} 条通知`)
    selectedRows.value = []
    fetchNotifications()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleCreate = () => {
  editData.value = null
  formVisible.value = true
}

const handleEdit = (row) => {
  editData.value = row
  formVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await api.get(`/notifications/${row.id}/`)
    currentNotification.value = res.data
    detailVisible.value = true
    
    // 如果是收到的未读通知，标记为已读
    if ((activeTab.value === 'received' || activeTab.value === 'todos') && !row.is_read) {
      await handleMarkAsRead(row.id)
    }
  } catch (e) {
    ElMessage.error('获取通知详情失败')
  }
}

const handleMarkAsRead = async (id) => {
  try {
    await api.post(`/notifications/${id}/mark_as_read/`)
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value[index].is_read = true
    }
    fetchUnreadCount()
  } catch (e) {
    console.error('标记已读失败', e)
  }
}

const handleHandle = async (row) => {
  try {
    await api.post(`/notifications/${row.id}/handle/`)
    ElMessage.success('已标记为已处理')
    const index = notifications.value.findIndex(n => n.id === row.id)
    if (index !== -1) {
      notifications.value[index].is_handled = true
    }
    fetchUnreadCount()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '处理失败')
  }
}

const handleDetailHandle = async (notification) => {
  try {
    await api.post(`/notifications/${notification.id}/handle/`)
    ElMessage.success('已标记为已处理')
    const index = notifications.value.findIndex(n => n.id === notification.id)
    if (index !== -1) {
      notifications.value[index].is_handled = true
    }
    // 如果通知有跳转链接，自动跳转
    if (notification.link_url) {
      handleNavigate(notification)
    }
    fetchUnreadCount()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '处理失败')
  }
}

const handleNavigate = (row) => {
  if (row.link_url) {
    // 如果有链接参数，构建完整URL
    let url = row.link_url
    if (row.link_params && Object.keys(row.link_params).length > 0) {
      const params = new URLSearchParams(row.link_params)
      url += (url.includes('?') ? '&' : '?') + params.toString()
    }
    router.push(url)
  }
}

const handleSend = async (row) => {
  try {
    await ElMessageBox.confirm('确定要发送此通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.post(`/notifications/${row.id}/send/`)
    ElMessage.success('发送成功')
    fetchNotifications()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '发送失败')
    }
  }
}

const handleRecall = async (row) => {
  try {
    await ElMessageBox.confirm('确定要撤回此通知吗？撤回后接收人将无法查看。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.post(`/notifications/${row.id}/recall/`)
    ElMessage.success('撤回成功')
    fetchNotifications()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '撤回失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    })
    await api.delete(`/notifications/${row.id}/`)
    ElMessage.success('删除成功')
    fetchNotifications()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  fetchNotifications()
}

onMounted(() => {
  fetchNotifications()
  fetchUnreadCount()
})
</script>

<style scoped>
.notification-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.badge-group {
  display: flex;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
  padding: 10px 15px;
  background-color: #ecf5ff;
  border-radius: 4px;
}

.selected-info {
  color: #409eff;
  font-weight: bold;
}

.status-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.todo-tag {
  align-self: flex-start;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.unread-title {
  font-weight: bold;
  color: #303133;
}

.urgent-icon {
  color: #f56c6c;
}

.attachment-icon {
  color: #909399;
  font-size: 14px;
}

.progress-cell {
  width: 80px;
}

.time-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-cell .date-text {
  font-size: 13px;
  color: #606266;
}

.time-cell .time-text {
  font-size: 12px;
  color: #909399;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.unread-row) {
  background-color: #f0f9ff;
}

:deep(.unread-row:hover) {
  background-color: #e6f7ff !important;
}
</style>
