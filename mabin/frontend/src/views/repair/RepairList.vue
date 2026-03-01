<template>
  <div class="repair-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报修管理</span>
          <el-button v-if="isStudent" type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            我要报修
          </el-button>
        </div>
      </template>
      
      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6" v-for="stat in stats" :key="stat.label">
          <el-card class="stat-card" shadow="hover">
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-form :inline="true" :model="filters">
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="全部" clearable>
              <el-option label="待受理" value="pending" />
              <el-option label="已受理" value="accepted" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="filters.priority" placeholder="全部" clearable>
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="filters.category" placeholder="全部" clearable>
              <el-option
                v-for="cat in categories"
                :key="cat.id"
                :label="cat.name"
                :value="cat.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 报修列表 -->
      <el-table :data="repairs" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="报修标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="location" label="地点" width="150" />
        <el-table-column prop="priority_display" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">
              {{ scope.row.priority_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="scope">
            <StatusTag :status="scope.row.status" type="default" />
          </template>
        </el-table-column>
        <el-table-column prop="handler_name" label="处理人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button
              v-if="scope.row.status === 'pending' && scope.row.applicant === currentUserId"
              type="danger"
              size="small"
              @click="handleCancel(scope.row)"
            >
              取消
            </el-button>
            <el-button
              v-if="scope.row.status === 'completed' && !scope.row.rating"
              type="success"
              size="small"
              @click="handleRate(scope.row)"
            >
              评价
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
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
    
    <!-- 报修详情对话框 -->
    <el-dialog v-model="detailVisible" title="报修详情" width="800px">
      <RepairDetail v-if="detailVisible" :repair-id="currentRepairId" />
    </el-dialog>
    
    <!-- 报修表单对话框 -->
    <el-dialog v-model="formVisible" title="我要报修" width="700px">
      <RepairForm v-if="formVisible" @success="handleFormSuccess" />
    </el-dialog>
    
    <!-- 评价对话框 -->
    <el-dialog v-model="rateVisible" title="评价报修" width="500px">
      <el-form :model="rateForm" label-width="100px">
        <el-form-item label="评分" required>
          <el-rate v-model="rateForm.rating" :max="5" />
        </el-form-item>
        <el-form-item label="评价">
          <el-input v-model="rateForm.comment" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rateVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitRate">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/format'
import StatusTag from '@/components/StatusTag.vue'
import RepairDetail from './RepairDetail.vue'
import RepairForm from './RepairForm.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.user?.id)
const isStudent = computed(() => userStore.user?.role === 'student')

const loading = ref(false)
const repairs = ref([])
const categories = ref([])
const stats = ref([
  { label: '全部', value: 0 },
  { label: '待受理', value: 0 },
  { label: '处理中', value: 0 },
  { label: '已完成', value: 0 }
])

const detailVisible = ref(false)
const formVisible = ref(false)
const rateVisible = ref(false)
const currentRepairId = ref(null)
const currentRepair = ref(null)

const filters = reactive({
  status: '',
  priority: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const rateForm = reactive({
  rating: 5,
  comment: ''
})

const fetchRepairs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '') delete params[key]
    })
    
    const response = await api.get('/repair/applications/', { params })
    repairs.value = response.data.results || response.data
    pagination.total = response.data.count || response.data.length || 0
  } catch (error) {
    ElMessage.error('获取报修列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/repair/categories/')
    categories.value = response.data.results || response.data
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

const fetchStatistics = async () => {
  try {
    const response = await api.get('/repair/applications/statistics/')
    const data = response.data
    stats.value = [
      { label: '全部', value: data.total || 0 },
      { label: '待受理', value: data.pending || 0 },
      { label: '处理中', value: data.processing || 0 },
      { label: '已完成', value: data.completed || 0 }
    ]
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRepairs()
}

const handleReset = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  handleSearch()
}

const handleCreate = () => {
  formVisible.value = true
}

const handleView = (row) => {
  currentRepairId.value = row.id
  detailVisible.value = true
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该报修吗？', '提示', {
      type: 'warning'
    })
    
    await api.post(`/repair/applications/${row.id}/cancel/`)
    ElMessage.success('取消成功')
    fetchRepairs()
    fetchStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const handleRate = (row) => {
  currentRepair.value = row
  rateForm.rating = 5
  rateForm.comment = ''
  rateVisible.value = true
}

const handleSubmitRate = async () => {
  if (!rateForm.rating) {
    ElMessage.warning('请选择评分')
    return
  }
  
  try {
    await api.post(`/repair/applications/${currentRepair.value.id}/rate/`, rateForm)
    ElMessage.success('评价成功')
    rateVisible.value = false
    fetchRepairs()
  } catch (error) {
    ElMessage.error('评价失败')
    console.error(error)
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  fetchRepairs()
  fetchStatistics()
}

const handleSizeChange = () => {
  fetchRepairs()
}

const handlePageChange = () => {
  fetchRepairs()
}

const getPriorityType = (priority) => {
  const map = {
    'low': 'info',
    'medium': '',
    'high': 'warning',
    'urgent': 'danger'
  }
  return map[priority] || ''
}

onMounted(() => {
  fetchCategories()
  fetchRepairs()
  fetchStatistics()
})
</script>

<style scoped>
.repair-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.filter-bar {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
