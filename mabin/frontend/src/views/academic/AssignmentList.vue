<template>
  <div class="assignment-list page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>教务管理</el-breadcrumb-item>
        <el-breadcrumb-item>作业管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="header-actions">
        <el-button v-if="isStaff" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>发布作业
        </el-button>
      </div>
    </div>

    <el-card class="stats-card" v-if="isStaff">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="发布作业总数" :value="assignments.length" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="待截止作业" :value="assignments.filter(a => !isExpired(a)).length">
            <template #suffix>
              <el-icon><Timer /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="平均提交率" :value="averageSubmissionRate" :precision="2">
            <template #suffix>%</template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="list-card mt-20">
      <div class="search-bar">
        <div class="search-left">
          <el-input
            v-model="searchQuery.search"
            placeholder="搜索作业标题..."
            class="filter-item"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-if="!isStudent" v-model="searchQuery.course" placeholder="全部课程" clearable @change="handleSearch" class="filter-item">
            <el-option v-for="item in courses" :key="item.id" :label="item.course_name" :value="item.id" />
          </el-select>

          <el-radio-group v-if="isStudent" v-model="activeTab" @change="handleSearch" class="filter-item">
            <el-radio-button label="pending">进行中</el-radio-button>
            <el-radio-button label="history">历史作业</el-radio-button>
          </el-radio-group>

          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
      </div>

      <el-table :data="assignments" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="作业标题" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="assignment-title" @click="handleDetail(row)">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="course_name" label="所属课程" width="160" />
        <el-table-column prop="deadline" label="截止时间" width="180">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isRisk(row) }">
              <el-icon v-if="isRisk(row)"><Timer /></el-icon>
              {{ formatDateTime(row.deadline) }}
            </span>
          </template>
        </el-table-column>
        
        <!-- 教师/管理 视角列 -->
        <template v-if="isStaff">
          <el-table-column label="提交进度" width="150">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.total_students ? Math.round((row.submission_count / row.total_students) * 100) : 0" 
                :status="row.submission_count === row.total_students ? 'success' : ''"
              />
              <div class="progress-text">{{ row.submission_count }} / {{ row.total_students }}</div>
            </template>
          </el-table-column>
        </template>

        <!-- 学生 视角列 -->
        <template v-else>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.student_status)">
                {{ getStatusText(row.student_status) }}
              </el-tag>
            </template>
          </el-table-column>
        </template>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">
              {{ isStudent && canSubmit(row) ? '去提交' : '查看详情' }}
            </el-button>
            <template v-if="isStaff">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-popconfirm title="确定删除该作业吗？" @confirm="handleDelete(row)">
                <template #reference>
                  <el-button link type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 发布/编辑作业弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑作业' : '发布作业'"
      width="600px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="所属课程" prop="course">
          <el-select v-model="form.course" placeholder="请选择课程" style="width: 100%" :disabled="!!form.id">
            <el-option v-for="item in courses" :key="item.id" :label="item.course_name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入作业标题" />
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="form.deadline"
            type="datetime"
            placeholder="请选择截止时间"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="允许补交" prop="allow_late_submission">
          <el-switch v-model="form.allow_late_submission" />
          <span class="switch-tip">允许在截止时间后提交</span>
        </el-form-item>
        <el-form-item v-if="form.allow_late_submission" label="逾期扣分" prop="late_penalty">
          <el-input-number v-model="form.late_penalty" :min="0" :max="100" />
          <span class="unit-tip">% (扣除总分的百分比)</span>
        </el-form-item>
        <el-form-item label="成绩权重" prop="weight_in_score">
          <el-input-number v-model="form.weight_in_score" :min="0" :max="100" />
          <span class="unit-tip">% (占平时成绩权重)</span>
        </el-form-item>
        <el-form-item label="作业要求" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请输入详细的作业要求和说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Timer } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/format'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 权限逻辑
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStudent = computed(() => userStore.user?.role === 'student')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

// 状态变量
const loading = ref(false)
const submitting = ref(false)
const assignments = ref([])
const courses = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref('pending')
const dialogVisible = ref(false)
const formRef = ref(null)

const searchQuery = reactive({
  search: '',
  course: ''
})

const form = reactive({
  id: null,
  course: '',
  title: '',
  description: '',
  deadline: '',
  allow_late_submission: true,
  late_penalty: 10,
  weight_in_score: 0
})

const rules = {
  course: [{ required: true, message: '请选择课程', trigger: 'change' }],
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }],
  description: [{ required: true, message: '请输入作业要求', trigger: 'blur' }]
}

// 获取作业列表
const fetchAssignments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.search,
      course: searchQuery.course
    }
    
    // 如果是学生，增加时间过滤逻辑（前端过滤或后端支持）
    // 目前后端 get_queryset 已经处理了权限，我们只需要获取数据
    const response = await api.get('/academic/assignments/', { params })
    let data = response.data.results || response.data
    
    if (isStudent.value) {
      const now = new Date()
      if (activeTab.value === 'pending') {
        data = data.filter(a => {
          const isOverdue = new Date(a.deadline) < now
          const isSubmitted = ['submitted', 'graded', 'returned'].includes(a.student_status)
          return !isOverdue || (isOverdue && !isSubmitted)
        })
      } else {
        data = data.filter(a => {
          const isOverdue = new Date(a.deadline) < now
          const isSubmitted = ['submitted', 'graded', 'returned'].includes(a.student_status)
          return isOverdue || isSubmitted
        })
      }
    }
    
    assignments.value = data
    total.value = response.data.count || data.length
  } catch (error) {
    ElMessage.error('获取作业列表失败')
  } finally {
    loading.value = false
  }
}

// 获取教师课程列表（用于发布作业）
const fetchCourses = async () => {
  try {
    const response = await api.get('/academic/courses/')
    courses.value = response.data.results || response.data
  } catch (error) {
    console.error('获取课程列表失败', error)
  }
}

// 搜索处理
const isExpired = (assignment) => {
  if (!assignment.deadline) return false
  return new Date(assignment.deadline) < new Date()
}

const averageSubmissionRate = computed(() => {
  if (assignments.value.length === 0) return 0
  const totalRate = assignments.value.reduce((acc, curr) => {
    const rate = curr.total_students ? (curr.submission_count / curr.total_students) : 0
    return acc + rate
  }, 0)
  return (totalRate / assignments.value.length) * 100
})

const handleSearch = () => {
  currentPage.value = 1
  fetchAssignments()
}

const resetSearch = () => {
  searchQuery.search = ''
  searchQuery.course = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAssignments()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAssignments()
}

// 操作处理
const handleDetail = (row) => {
  router.push(`/academic/assignments/${row.id}`)
}

const handleAdd = () => {
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await api.delete(`/academic/assignments/${row.id}/`)
    ElMessage.success('删除成功')
    fetchAssignments()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  Object.assign(form, {
    id: null,
    course: '',
    title: '',
    description: '',
    deadline: '',
    allow_late_submission: true,
    late_penalty: 10,
    weight_in_score: 0
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (form.id) {
          await api.put(`/academic/assignments/${form.id}/`, form)
          ElMessage.success('修改成功')
        } else {
          await api.post('/academic/assignments/', form)
          ElMessage.success('发布成功')
        }
        dialogVisible.value = false
        fetchAssignments()
      } catch (error) {
        ElMessage.error(form.id ? '修改失败' : '发布失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 辅助函数
const isRisk = (row) => {
  if (row.student_status === 'pending') {
    const now = new Date()
    const deadline = new Date(row.deadline)
    return deadline - now < 24 * 60 * 60 * 1000 && deadline > now
  }
  return row.student_status === 'overdue'
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    submitted: 'success',
    graded: 'success',
    returned: 'warning',
    overdue: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待提交',
    submitted: '已提交',
    graded: '已评分',
    returned: '需重交',
    overdue: '已逾期'
  }
  return map[status] || status
}

const canSubmit = (row) => {
  return ['pending', 'returned', 'overdue'].includes(row.student_status)
}

onMounted(() => {
  fetchAssignments()
  if (isStaff.value) {
    fetchCourses()
  }
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.list-card {
  .search-bar {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .search-left {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .filter-item {
      width: 200px;
    }
  }
}

.mt-20 {
  margin-top: 20px;
}

.assignment-title {
  color: #409eff;
  cursor: pointer;
  font-weight: 500;
  &:hover {
    text-decoration: underline;
  }
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  text-align: center;
  margin-top: 4px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.switch-tip, .unit-tip {
  margin-left: 12px;
  font-size: 13px;
  color: #909399;
}

:deep(.el-progress-bar__outer) {
  background-color: #f5f7fa;
  height: 8px !important;
}
</style>
