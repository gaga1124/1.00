<template>
  <div class="archive-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">文件留档</span>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出记录
            </el-button>
          </div>
        </div>
      </template>

      <div class="statistics-panel">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Files /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.total }}</div>
            <div class="stat-label">归档总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon archived">
            <el-icon><FolderOpened /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.archived }}</div>
            <div class="stat-label">已归档</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon pending">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.pending }}</div>
            <div class="stat-label">待归档</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon viewed">
            <el-icon><View /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.viewed }}</div>
            <div class="stat-label">已查阅</div>
          </div>
        </div>
      </div>

      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名或标题"
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="已归档" value="archived" />
          <el-option label="待归档" value="pending" />
          <el-option label="已查阅" value="viewed" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
          @change="handleDateChange"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="files" v-loading="loading" style="width: 100%">
        <el-table-column type="index" width="50" />
        <el-table-column prop="title" label="文件标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="filename" label="文件名" min-width="180" show-overflow-tooltip />
        <el-table-column prop="file_type" label="文件类型" width="100" />
        <el-table-column prop="file_size" label="文件大小" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="上传人" width="120" />
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button link type="success" size="small" @click="handleDownload(row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Files, 
  FolderOpened, 
  Clock, 
  View, 
  Download, 
  Search 
} from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const files = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const statusFilter = ref('')
const dateRange = ref(null)

const statistics = reactive({
  total: 156,
  archived: 142,
  pending: 8,
  viewed: 98
})

const statusMap = {
  archived: { type: 'success', text: '已归档' },
  pending: { type: 'warning', text: '待归档' },
  viewed: { type: 'info', text: '已查阅' }
}

const getStatusType = (status) => {
  return statusMap[status]?.type || ''
}

const getStatusText = (status) => {
  return statusMap[status]?.text || status
}

const loadFiles = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      status: statusFilter.value
    }
    const res = await api.get('/electronic-signature/files/', { params })
    files.value = res.data?.results || res.data || []
    total.value = res.data?.count || files.value.length
    
    statistics.value = {
      total: total.value,
      archived: files.value.filter(f => f.status === 'archived').length,
      pending: files.value.filter(f => f.status === 'pending').length,
      viewed: files.value.filter(f => f.is_signed).length
    }
  } catch (error) {
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadFiles()
}

const handleReset = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  dateRange.value = null
  handleSearch()
}

const handleDateChange = () => {
  handleSearch()
}

const handleSizeChange = () => {
  loadFiles()
}

const handleCurrentChange = () => {
  loadFiles()
}

const handleView = (row) => {
  ElMessage.info(`查看文件: ${row.title}`)
}

const handleDownload = (row) => {
  ElMessage.success(`下载文件: ${row.filename}`)
}

const handleExport = () => {
  ElMessage.success('开始导出归档记录')
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.archive-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.statistics-panel {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(64, 158, 255, 0.05));
  color: #409EFF;
}

.stat-icon.archived {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1), rgba(103, 194, 58, 0.05));
  color: #67C23A;
}

.stat-icon.pending {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.1), rgba(230, 162, 60, 0.05));
  color: #E6A23C;
}

.stat-icon.viewed {
  background: linear-gradient(135deg, rgba(144, 147, 153, 0.1), rgba(144, 147, 153, 0.05));
  color: #909399;
}

.stat-info .stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-info .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .statistics-panel {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .statistics-panel {
    grid-template-columns: 1fr;
  }
  
  .filter-bar {
    flex-wrap: wrap;
  }
}
</style>
