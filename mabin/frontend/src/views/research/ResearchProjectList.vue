<template>
  <div class="research-projects container-padding">
    <el-card class="box-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><Opportunity /></el-icon>
            <span>科研项目管理</span>
          </div>
          <el-button type="primary" @click="handleCreate" v-if="isStaff">
            <el-icon><Plus /></el-icon>项目申报
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchQuery" size="default">
          <el-form-item label="项目名称">
            <el-input v-model="searchQuery.project_name" placeholder="输入项目名称" clearable style="width: 200px" />
          </el-form-item>
          <el-form-item label="项目类型">
            <el-select v-model="searchQuery.project_type" placeholder="全部类型" clearable style="width: 150px">
              <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchQuery.status" placeholder="全部状态" clearable style="width: 150px">
              <el-option v-for="(label, value) in statusMap" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchProjects">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 项目列表 -->
      <el-table :data="projects" v-loading="loading" style="width: 100%" border stripe>
        <el-table-column prop="project_code" label="项目编号" width="140" />
        <el-table-column prop="project_name" label="项目名称" min-width="250" show-overflow-tooltip />
        <el-table-column prop="project_type" label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.project_type)" effect="light" size="small">{{ typeMap[row.project_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="120">
          <template #default="{ row }">
            <div class="principal-cell">
              <el-avatar :size="24" :src="row.principal_info?.avatar" style="margin-right: 8px">
                {{ row.principal_info?.real_name?.[0] }}
              </el-avatar>
              <span>{{ row.principal_info?.real_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_budget" label="总经费" width="140">
          <template #default="{ row }">
            <span class="budget-text">¥{{ formatNumber(row.total_budget) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" effect="dark" size="small">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-divider direction="vertical" />
            <el-button link type="primary" @click="handleMilestones(row)">里程碑</el-button>
            <el-divider direction="vertical" v-if="isStaff" />
            <el-button link type="success" @click="handleBudget(row)" v-if="isStaff">经费</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 申报/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑项目' : '项目申报'" width="700px" destroy-on-close>
      <el-form :model="projectForm" :rules="rules" ref="projectFormRef" label-width="100px" status-icon>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目编号" prop="project_code">
              <el-input v-model="projectForm.project_code" placeholder="如：NSFC-2024-001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目类型" prop="project_type">
              <el-select v-model="projectForm.project_type" placeholder="请选择" style="width: 100%">
                <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="projectForm.project_name" placeholder="请输入完整项目名称" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="projectForm.description" type="textarea" :rows="4" placeholder="简述研究内容、目标及预期成果" maxlength="1000" show-word-limit />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker v-model="projectForm.start_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker v-model="projectForm.end_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="总经费" prop="total_budget">
          <el-input-number v-model="projectForm.total_budget" :precision="2" :step="1000" :min="0" style="width: 200px" />
        </el-form-item>
        <el-form-item label="申报书" prop="application_file">
          <el-upload
            class="upload-demo"
            action="/api/research/projects/upload/"
            :headers="uploadHeaders"
            :limit="1"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
          >
            <el-button type="primary"><el-icon><Upload /></el-icon>点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传 pdf/doc/docx 文件，且不超过 10MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="项目详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目编号">{{ currentProject.project_code }}</el-descriptions-item>
        <el-descriptions-item label="项目类型">
          <el-tag>{{ typeMap[currentProject.project_type] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="项目名称" :span="2">{{ currentProject.project_name }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ currentProject.principal_info?.real_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentProject.status)">{{ statusMap[currentProject.status] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentProject.start_date }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentProject.end_date }}</el-descriptions-item>
        <el-descriptions-item label="总经费">¥{{ formatNumber(currentProject.total_budget) }}</el-descriptions-item>
        <el-descriptions-item label="已使用经费">¥{{ formatNumber(currentProject.used_budget) }}</el-descriptions-item>
        <el-descriptions-item label="项目描述" :span="2">{{ currentProject.description }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="budget-progress" style="margin-top: 20px">
        <h4>经费使用进度</h4>
        <el-progress 
          :percentage="calculateProgress(currentProject.used_budget, currentProject.total_budget)" 
          :status="currentProject.used_budget > currentProject.total_budget ? 'exception' : ''"
        />
      </div>
    </el-dialog>

    <!-- 经费管理对话框 -->
    <el-dialog v-model="budgetVisible" title="经费明细管理" width="600px">
      <el-table :data="currentProject.budget_details || []" border style="width: 100%">
        <el-table-column prop="category" label="支出类别" />
        <el-table-column prop="amount" label="预算额度">
          <template #default="{ row }">¥{{ formatNumber(row.amount) }}</template>
        </el-table-column>
        <el-table-column prop="used" label="已使用">
          <template #default="{ row }">¥{{ formatNumber(row.used) }}</template>
        </el-table-column>
        <el-table-column label="进度">
          <template #default="{ row }">
            <el-progress :percentage="calculateProgress(row.used, row.amount)" />
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px">
        <el-form :model="budgetForm" inline size="small">
          <el-form-item label="新增支出">
            <el-select v-model="budgetForm.category" placeholder="选择类别" style="width: 120px">
              <el-option label="设备费" value="设备费" />
              <el-option label="材料费" value="材料费" />
              <el-option label="差旅费" value="差旅费" />
              <el-option label="劳务费" value="劳务费" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="金额">
            <el-input-number v-model="budgetForm.amount" :min="0" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitBudget">登记支出</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Opportunity, Upload } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

const loading = ref(false)
const projects = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const budgetVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const currentProject = ref({})
const projectFormRef = ref(null)

const searchQuery = reactive({
  project_name: '',
  project_type: '',
  status: ''
})

const resetSearch = () => {
  Object.assign(searchQuery, {
    project_name: '',
    project_type: '',
    status: ''
  })
  fetchProjects()
}

const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB!')
  }
  return isLt10M
}

const typeMap = {
  national: '国家级',
  provincial: '省级',
  municipal: '市级',
  university: '校级',
  enterprise: '企业合作'
}

const statusMap = {
  declared: '已申报',
  approved: '已立项',
  midterm: '中期检查',
  final: '结题验收',
  completed: '已完成',
  cancelled: '已取消'
}

const projectForm = reactive({
  project_code: '',
  project_name: '',
  project_type: '',
  description: '',
  start_date: '',
  end_date: '',
  total_budget: 0
})

const budgetForm = reactive({
  category: '',
  amount: 0
})

const rules = {
  project_code: [{ required: true, message: '请输入项目编号', trigger: 'blur' }],
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  project_type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

const fetchProjects = async () => {
  loading.value = true
  try {
    const params = { ...searchQuery }
    const response = await api.get('/research/projects/', { params })
    projects.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

const calculateProgress = (used, total) => {
  const t = Number(total)
  const u = Number(used)
  if (!t || t === 0) return 0
  const p = Math.round((u / t) * 100)
  return isNaN(p) ? 0 : Math.min(100, Math.max(0, p))
}

const handleCreate = () => {
  isEdit.value = false
  Object.assign(projectForm, {
    project_code: '',
    project_name: '',
    project_type: '',
    description: '',
    start_date: '',
    end_date: '',
    total_budget: 0
  })
  dialogVisible.value = true
}

const handleDetail = (row) => {
  currentProject.value = row
  detailVisible.value = true
}

const handleBudget = (row) => {
  currentProject.value = row
  budgetVisible.value = true
}

const handleMilestones = (row) => {
  // 跳转到里程碑管理或显示对话框
  ElMessage.info('里程碑管理功能开发中...')
}

const submitForm = async () => {
  if (!projectFormRef.value) return
  
  await projectFormRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/research/projects/${currentProject.value.id}/`, projectForm)
          ElMessage.success('更新成功')
        } else {
          await api.post('/research/projects/', projectForm)
          ElMessage.success('申报成功')
        }
        dialogVisible.value = false
        fetchProjects()
      } catch (error) {
        console.error('Submit error:', error)
        if (error.response?.data) {
          const data = error.response.data
          const msg = typeof data === 'string' ? data : 
                     data.detail ? data.detail :
                     Object.values(data).flat().join('; ')
          ElMessage.error(msg || (isEdit.value ? '更新失败' : '申报失败'))
        } else {
          ElMessage.error(isEdit.value ? '更新失败' : '申报失败')
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const submitBudget = async () => {
  if (!budgetForm.category || budgetForm.amount <= 0) {
    return ElMessage.warning('请填写完整的支出信息')
  }
  try {
    await api.post(`/research/projects/${currentProject.value.id}/update_budget/`, budgetForm)
    ElMessage.success('支出登记成功')
    budgetForm.category = ''
    budgetForm.amount = 0
    fetchProjects()
    // 更新当前详情显示
    const response = await api.get(`/research/projects/${currentProject.value.id}/`)
    currentProject.value = response.data
  } catch (error) {
    ElMessage.error('登记失败')
  }
}

const handleUploadSuccess = (response) => {
  projectForm.application_file = response.url
}

const getTypeTag = (type) => {
  const map = {
    national: 'danger',
    provincial: 'warning',
    municipal: 'primary',
    university: 'success',
    enterprise: 'info'
  }
  return map[type] || 'info'
}

const getStatusTag = (status) => {
  const map = {
    declared: 'info',
    approved: 'primary',
    midterm: 'warning',
    final: 'success',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const formatNumber = (num) => {
  return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.container-padding {
  padding: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}
.search-bar {
  margin-bottom: 20px;
  padding: 18px 18px 0;
  background-color: #fcfcfc;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}
.principal-cell {
  display: flex;
  align-items: center;
}
.budget-text {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-weight: 500;
  color: #f56c6c;
}
.budget-progress {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 20px;
}
.budget-progress h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
}
</style>
