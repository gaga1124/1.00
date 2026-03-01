<template>
  <div class="student-records-container page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>学生管理</el-breadcrumb-item>
        <el-breadcrumb-item>学籍变动与档案</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddRecord" v-if="!isStudent">
          <el-icon><Plus /></el-icon>新增记录
        </el-button>
        <el-button type="warning" @click="handleStatusChange" v-if="!isStudent">
          <el-icon><Refresh /></el-icon>学籍变动
        </el-button>
      </div>
    </div>

    <el-card class="list-card">
      <div class="search-bar">
        <div class="search-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索学生姓名或标题"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            class="filter-item"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="filterType" placeholder="记录类型" clearable @change="handleSearch" class="filter-item">
            <el-option label="获奖记录" value="award" />
            <el-option label="惩处记录" value="punishment" />
            <el-option label="科研成果" value="research" />
            <el-option label="活动参与" value="activity" />
            <el-option label="其他" value="other" />
          </el-select>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="档案记录" name="records">
          <el-table :data="records" v-loading="loading" border stripe>
            <el-table-column prop="student_name" label="学生姓名" v-if="!isStudent" width="120" />
            <el-table-column prop="record_type_display" label="类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getRecordTag(row.record_type)">{{ row.record_type_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="created_at" label="记录时间" width="180" />
            <el-table-column prop="operator_name" label="记录人" width="120" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewRecordDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="学籍变动" name="status-changes">
          <el-table :data="statusChanges" v-loading="loading" border stripe>
            <el-table-column prop="student_name" label="学生姓名" v-if="!isStudent" width="120" />
            <el-table-column prop="change_type_display" label="变动类型" width="120">
              <template #default="{ row }">
                <el-tag effect="dark">{{ row.change_type_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="from_status" label="原状态" width="120" />
            <el-table-column prop="to_status" label="新状态" width="120" />
            <el-table-column prop="change_date" label="变动日期" width="120" />
            <el-table-column prop="document_no" label="文件编号" min-width="150" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewChangeDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="政治面貌流转" name="political">
          <el-table :data="politicalRecords" v-loading="loading" border stripe>
            <el-table-column prop="student_name" label="学生姓名" v-if="!isStudent" width="120" />
            <el-table-column label="流转过程" min-width="200">
              <template #default="{ row }">
                {{ row.from_status_display }} <el-icon><Right /></el-icon> {{ row.to_status_display }}
              </template>
            </el-table-column>
            <el-table-column prop="status_display" label="审批状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getPoliticalStatusTag(row.status)">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="application_date" label="申请日期" width="120" />
            <el-table-column prop="approval_date" label="批准日期" width="120" />
            <el-table-column label="操作" width="150" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewPoliticalDetail(row)">详情</el-button>
                <el-button link type="success" v-if="row.status === 'pending' && !isStudent" @click="handleApprove(row)">审批</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

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

    <!-- 新增记录对话框 -->
    <el-dialog v-model="recordVisible" title="新增档案记录" width="600px">
      <el-form :model="recordForm" label-width="100px">
        <el-form-item label="学生" v-if="!isStudent">
          <el-select v-model="recordForm.student" filterable placeholder="选择学生">
            <el-option v-for="s in students" :key="s.id" :label="s.user_info.real_name + '(' + s.student_id + ')'" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="记录类型">
          <el-select v-model="recordForm.record_type">
            <el-option label="获奖记录" value="award" />
            <el-option label="惩处记录" value="punishment" />
            <el-option label="科研成果" value="research" />
            <el-option label="活动参与" value="activity" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="recordForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="recordForm.description" type="textarea" rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="recordVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRecord">提交</el-button>
      </template>
    </el-dialog>

    <!-- 学籍变动对话框 -->
    <el-dialog v-model="statusVisible" title="学籍变动处理" width="600px">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="学生">
          <el-select v-model="statusForm.student" filterable placeholder="选择学生">
            <el-option v-for="s in students" :key="s.id" :label="s.user_info.real_name + '(' + s.student_id + ')'" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="变动类型">
          <el-select v-model="statusForm.change_type">
            <el-option label="休学" value="suspend" />
            <el-option label="复学" value="resume" />
            <el-option label="转专业" value="other" />
            <el-option label="退学" value="withdraw" />
            <el-option label="毕业" value="graduate" />
          </el-select>
        </el-form-item>
        <el-form-item label="变动日期">
          <el-date-picker v-model="statusForm.change_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="变动后状态">
          <el-input v-model="statusForm.to_status" placeholder="如：休学中、在读、已毕业" />
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="statusForm.reason" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="文件编号">
          <el-input v-model="statusForm.document_no" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStatusChange">确认变动</el-button>
      </template>
    </el-dialog>
    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" :title="detailTitle" width="500px">
      <div v-if="currentDetail" class="detail-content">
        <template v-if="detailType === 'record'">
          <p><strong>类型:</strong> {{ currentDetail.record_type_display }}</p>
          <p><strong>标题:</strong> {{ currentDetail.title }}</p>
          <p><strong>描述:</strong> {{ currentDetail.description }}</p>
          <p><strong>记录人:</strong> {{ currentDetail.operator_name }}</p>
          <p><strong>时间:</strong> {{ currentDetail.created_at }}</p>
        </template>
        <template v-else-if="detailType === 'change'">
          <p><strong>变动类型:</strong> {{ currentDetail.change_type_display }}</p>
          <p><strong>原状态:</strong> {{ currentDetail.from_status }}</p>
          <p><strong>新状态:</strong> {{ currentDetail.to_status }}</p>
          <p><strong>变动日期:</strong> {{ currentDetail.change_date }}</p>
          <p><strong>变动原因:</strong> {{ currentDetail.reason }}</p>
          <p><strong>文件编号:</strong> {{ currentDetail.document_no }}</p>
        </template>
        <template v-else-if="detailType === 'political'">
          <p><strong>流转:</strong> {{ currentDetail.from_status_display }} -> {{ currentDetail.to_status_display }}</p>
          <p><strong>状态:</strong> {{ currentDetail.status_display }}</p>
          <p><strong>申请日期:</strong> {{ currentDetail.application_date }}</p>
          <p><strong>批准日期:</strong> {{ currentDetail.approval_date || '未批准' }}</p>
          <p><strong>审批意见:</strong> {{ currentDetail.approval_comment || '无' }}</p>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Right, Search, Plus, Refresh } from '@element-plus/icons-vue'

const userStore = useUserStore()
const isStudent = computed(() => userStore.user?.role === 'student')

const loading = ref(false)
const activeTab = ref('records')
const records = ref([])
const statusChanges = ref([])
const politicalRecords = ref([])
const students = ref([])

// 搜索与分页
const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const detailTitle = ref('')
const detailType = ref('')
const currentDetail = ref(null)

const recordVisible = ref(false)
const recordForm = ref({
  student: '',
  record_type: 'other',
  title: '',
  description: ''
})

const statusVisible = ref(false)
const statusForm = ref({
  student: '',
  change_type: 'other',
  change_date: '',
  to_status: '',
  reason: '',
  document_no: ''
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      search: searchQuery.value,
      page: currentPage.value,
      size: pageSize.value
    }

    if (activeTab.value === 'records') {
      if (filterType.value) params.record_type = filterType.value
      const res = await api.get('/students/records/', { params })
      records.value = res.data.results || res.data
      total.value = res.data.count || (res.data.results ? res.data.results.length : records.value.length)
    } else if (activeTab.value === 'status-changes') {
      const res = await api.get('/students/status-changes/', { params })
      statusChanges.value = res.data.results || res.data
      total.value = res.data.count || (res.data.results ? res.data.results.length : statusChanges.value.length)
    } else if (activeTab.value === 'political') {
      const res = await api.get('/students/political-records/', { params })
      politicalRecords.value = res.data.results || res.data
      total.value = res.data.count || (res.data.results ? res.data.results.length : politicalRecords.value.length)
    }
    
    if (!isStudent.value && students.value.length === 0) {
      const studentsRes = await api.get('/students/')
      students.value = studentsRes.data.results || studentsRes.data
    }
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const resetSearch = () => {
  searchQuery.value = ''
  filterType.value = ''
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

watch(activeTab, () => {
  handleSearch()
})

const getRecordTag = (type) => {
  const map = {
    award: 'success',
    punishment: 'danger',
    research: 'warning',
    activity: 'primary',
    other: 'info'
  }
  return map[type] || 'info'
}

const getPoliticalStatusTag = (status) => {
  const map = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const handleAddRecord = () => {
  recordForm.value = {
    student: isStudent.value?.id || '',
    record_type: 'other',
    title: '',
    description: ''
  }
  recordVisible.value = true
}

const submitRecord = async () => {
  try {
    await api.post('/students/records/', recordForm.value)
    ElMessage.success('添加记录成功')
    recordVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleStatusChange = () => {
  statusForm.value = {
    student: '',
    change_type: 'other',
    change_date: new Date().toISOString().split('T')[0],
    to_status: '',
    reason: '',
    document_no: ''
  }
  statusVisible.value = true
}

const submitStatusChange = async () => {
  try {
    await api.post('/students/status-changes/', statusForm.value)
    ElMessage.success('状态变更记录已提交')
    statusVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const viewRecordDetail = (row) => {
  detailTitle.value = '档案记录详情'
  detailType.value = 'record'
  currentDetail.value = row
  detailVisible.value = true
}

const viewChangeDetail = (row) => {
  detailTitle.value = '学籍变动详情'
  detailType.value = 'change'
  currentDetail.value = row
  detailVisible.value = true
}

const viewPoliticalDetail = (row) => {
  detailTitle.value = '政治面貌流转详情'
  detailType.value = 'political'
  currentDetail.value = row
  detailVisible.value = true
}

const handleApprove = async (row) => {
  try {
    const { value: comment } = await ElMessageBox.prompt('请输入审批意见', '政治面貌审批', {
      confirmButtonText: '通过',
      cancelButtonText: '拒绝',
      distinguishCancelAndClose: true,
      inputPlaceholder: '可选'
    }).catch(({ action }) => {
      if (action === 'cancel') return { value: '', action: 'reject' }
      throw 'close'
    })

    const action = typeof comment === 'object' && comment.action === 'reject' ? 'reject' : 'approve'
    const finalComment = typeof comment === 'object' ? comment.value : comment

    await api.post(`/students/political-records/${row.id}/approve/`, {
      action,
      comment: finalComment
    })
    ElMessage.success('审批完成')
    fetchData()
  } catch (e) {
    if (e !== 'close') ElMessage.error('审批失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.student-records-container {
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
        width: 240px;
      }
    }

    .custom-tabs {
      margin-top: 10px;
    }

    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .detail-content {
    p {
      margin-bottom: 15px;
      line-height: 1.6;
      font-size: 14px;
      
      strong {
        display: inline-block;
        width: 80px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .header-actions {
    display: flex;
    gap: 12px;
  }
}
</style>
