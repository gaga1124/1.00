<template>
  <div class="notification-list-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通知中心</span>
          <div class="header-actions">
            <el-radio-group v-model="filter" size="small" @change="handleFilterChange">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="unread">未读</el-radio-button>
            </el-radio-group>
            
            <el-button 
              type="primary" 
              link 
              :disabled="selectedIds.length === 0"
              @click="handleBatchMarkRead"
            >
              批量已读
            </el-button>
            <el-button 
              type="danger" 
              link 
              :disabled="selectedIds.length === 0"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
            
            <el-button type="primary" link @click="notificationStore.markAllAsRead">全部已读</el-button>
          </div>
        </div>
        
        <div class="batch-toolbar" v-if="notifications.length > 0">
          <el-checkbox 
            v-model="allSelected" 
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >
            全选本页
          </el-checkbox>
        </div>
      </template>
      
      <div v-loading="loading" class="notification-list">
        <el-empty v-if="notifications.length === 0" description="暂无通知" />
        <div 
          v-else 
          v-for="item in notifications" 
          :key="item.id" 
          class="notification-item"
          :class="{ 'unread': !item.is_read }"
          @click="handleClick(item)"
        >
          <div class="notification-checkbox" @click.stop>
            <el-checkbox 
              v-model="item.selected" 
              @change="(val) => handleSelectionChange(val, item)"
            />
          </div>
          <div class="notification-icon">
            <el-icon v-if="item.type === 'system'" class="system-icon"><Bell /></el-icon>
            <el-icon v-else-if="item.type === 'approval'" class="approval-icon"><Check /></el-icon>
            <el-icon v-else class="info-icon"><InfoFilled /></el-icon>
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ item.title }}
              <el-tag v-if="!item.is_read" size="small" type="danger" effect="dark" class="new-tag">NEW</el-tag>
            </div>
            <div class="notification-body">{{ item.message }}</div>
            <div class="notification-time">{{ formatTime(item.created_at) }}</div>
          </div>
          <div class="notification-actions">
            <el-button link type="danger" size="small" @click.stop="handleDelete(item)">删除</el-button>
          </div>
        </div>
      </div>
      
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Check, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useNotificationStore } from '@/stores/notification'
import api from '@/utils/api'

const router = useRouter()
const notificationStore = useNotificationStore()

const loading = ref(false)
const filter = ref('all')
const notifications = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedIds = ref([])
const allSelected = ref(false)
const isIndeterminate = ref(false)

const fetchData = async () => {
  loading.value = true
  selectedIds.value = []
  allSelected.value = false
  isIndeterminate.value = false
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      unread: filter.value === 'unread' ? true : undefined
    }
    const response = await api.get('/notifications/', { params })
    notifications.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    console.error(error)
    ElMessage.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchData()
}

const handleClick = (item) => {
  if (!item.is_read) {
    notificationStore.markAsRead(item.id)
    item.is_read = true
  }
  if (item.related_link) {
    router.push(item.related_link)
  }
}

const handleDelete = (item) => {
  ElMessageBox.confirm('确定要删除这条通知吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    await notificationStore.deleteNotification(item.id)
    fetchData()
    ElMessage.success('删除成功')
  }).catch((err) => {
    if (err !== 'cancel') {
      console.error(err)
      ElMessage.error('删除失败')
    }
  })
}

// 批量操作相关逻辑
const updateSelectAllState = () => {
  const selectedCount = selectedIds.value.length
  const totalCount = notifications.value.length
  allSelected.value = totalCount > 0 && selectedCount === totalCount
  isIndeterminate.value = selectedCount > 0 && selectedCount < totalCount
}

const handleSelectionChange = (val, item) => {
  if (val) {
    selectedIds.value.push(item.id)
  } else {
    selectedIds.value = selectedIds.value.filter(id => id !== item.id)
  }
  updateSelectAllState()
}

const handleSelectAll = (val) => {
  notifications.value.forEach(item => {
    item.selected = val
  })
  selectedIds.value = val ? notifications.value.map(item => item.id) : []
  isIndeterminate.value = false
}

const handleBatchMarkRead = async () => {
  if (selectedIds.value.length === 0) return
  
  try {
    const promises = selectedIds.value.map(id => notificationStore.markAsRead(id))
    await Promise.all(promises)
    
    notifications.value.forEach(item => {
      if (selectedIds.value.includes(item.id)) {
        item.is_read = true
      }
    })
    
    ElMessage.success('批量标记已读成功')
    selectedIds.value = []
    allSelected.value = false
    isIndeterminate.value = false
    notifications.value.forEach(item => item.selected = false)
    
  } catch (error) {
    console.error(error)
    ElMessage.error('批量操作失败')
  }
}

const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) return

  ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条通知吗？`, '批量删除', {
    type: 'warning',
    confirmButtonText: '确定删除',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      const promises = selectedIds.value.map(id => notificationStore.deleteNotification(id))
      await Promise.all(promises)
      ElMessage.success('批量删除成功')
      fetchData() // 重新获取数据
    } catch (error) {
      console.error(error)
      ElMessage.error('批量删除部分失败')
      fetchData()
    }
  }).catch(() => {})
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.notification-list-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.batch-toolbar {
  padding: 10px 15px;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.notification-list {
  min-height: 400px;
}

.notification-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #f0f9eb;
}

.notification-icon {
  margin-right: 15px;
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.notification-checkbox {
  display: flex;
  align-items: center;
  padding-right: 15px;
} 

.notification-icon .el-icon {
  font-size: 20px;
  padding: 8px;
  border-radius: 50%;
  background-color: #f2f6fc;
  color: #909399;
}

.approval-icon {
  color: #67c23a !important;
  background-color: #e1f3d8 !important;
}

.system-icon {
  color: #409eff !important;
  background-color: #ecf5ff !important;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 16px;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-tag {
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
}

.notification-body {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
  line-height: 1.5;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.notification-actions {
  display: flex;
  align-items: center;
  padding-left: 15px;
  opacity: 0;
  transition: opacity 0.2s;
}

.notification-item:hover .notification-actions {
  opacity: 1;
}

.pagination-container {
  margin-top: 20px;
  justify-content: flex-end;
}

.batch-toolbar {
  padding: 10px 15px;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.notification-checkbox {
  display: flex;
  align-items: center;
  padding-right: 15px;
}
</style>
