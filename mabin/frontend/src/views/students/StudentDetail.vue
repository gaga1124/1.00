<template>
  <div class="student-detail" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="basic">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="学号">{{ student.student_id }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ student.user_info?.real_name }}</el-descriptions-item>
          <el-descriptions-item label="学院">{{ student.department_name }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ student.major }}</el-descriptions-item>
          <el-descriptions-item label="班级">{{ student.class_name }}</el-descriptions-item>
          <el-descriptions-item label="年级">{{ student.grade }}</el-descriptions-item>
          <el-descriptions-item label="政治面貌">{{ student.political_status_display }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ student.user_info?.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ student.user_info?.email }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <el-tab-pane label="学籍变动" name="status">
        <el-table v-if="statusChanges.length > 0" :data="statusChanges" style="width: 100%">
          <el-table-column prop="change_date" label="日期" width="120" />
          <el-table-column prop="change_type_display" label="变动类型" width="120" />
          <el-table-column prop="from_status" label="变动前" />
          <el-table-column prop="to_status" label="变动后" />
          <el-table-column prop="reason" label="原因" show-overflow-tooltip />
          <el-table-column label="附件" width="100">
            <template #default="scope">
              <el-button v-if="scope.row.attachments?.length" link type="primary" @click="viewFiles(scope.row.attachments)">
                查看附件
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无学籍变动记录" />
      </el-tab-pane>
      
      <el-tab-pane label="政治面貌历史" name="political">
        <el-timeline v-if="politicalRecords.length > 0">
          <el-timeline-item
            v-for="record in politicalRecords"
            :key="record.id"
            :timestamp="record.created_at"
            placement="top"
          >
            <el-card>
              <h4>{{ record.from_status_display }} → {{ record.to_status_display }}</h4>
              <p>状态: <el-tag :type="getStatusType(record.status)">{{ record.status_display }}</el-tag></p>
              <p v-if="record.approval_comment">审批意见: {{ record.approval_comment }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无政治面貌历史记录" />
      </el-tab-pane>
      
      <el-tab-pane label="档案记录" name="records">
        <el-table v-if="records.length > 0" :data="records" style="width: 100%">
          <el-table-column prop="record_type_display" label="记录类型" width="120" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="operator_name" label="操作人" width="120" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button type="primary" size="small" @click="viewRecord(scope.row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无档案记录" />
      </el-tab-pane>

      <el-tab-pane v-if="isStaff" label="查阅记录" name="logs">
        <el-table v-if="viewLogs.length > 0" :data="viewLogs" style="width: 100%">
          <el-table-column prop="viewed_at" label="查阅时间" width="180">
            <template #default="scope">
              {{ formatDateTime(scope.row.viewed_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="viewer_name" label="查阅人" width="120" />
          <el-table-column prop="reason" label="查阅原因" />
          <el-table-column prop="ip_address" label="IP地址" width="140" />
        </el-table>
        <el-empty v-else description="暂无查阅记录" />
      </el-tab-pane>
    </el-tabs>

    <!-- 附件预览对话框 -->
    <el-dialog v-model="fileVisible" title="附件列表" width="400px">
      <el-list v-if="currentFiles.length">
        <el-list-item v-for="(file, idx) in currentFiles" :key="idx">
          <div class="file-item">
            <span>{{ file.name || '未命名文件' }}</span>
            <el-button link type="primary" @click="downloadFile(file.url)">下载</el-button>
          </div>
        </el-list-item>
      </el-list>
      <el-empty v-else description="暂无附件" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  studentId: {
    type: [Number, String],
    required: true
  }
})

const userStore = useUserStore()
const isStaff = computed(() => ['admin', 'teacher', 'staff'].includes(userStore.user?.role))

const loading = ref(false)
const activeTab = ref('basic')
const student = ref({})
const politicalRecords = ref([])
const records = ref([])
const statusChanges = ref([])
const viewLogs = ref([])

const fileVisible = ref(false)
const currentFiles = ref([])

const fetchStudentDetail = async () => {
  loading.value = true
  try {
    const response = await api.get(`/students/${props.studentId}/`)
    student.value = response.data
    // 如果返回了详情，可以直接赋值
    if (student.value.political_records) politicalRecords.value = student.value.political_records
    if (student.value.status_changes) statusChanges.value = student.value.status_changes
    if (student.value.archive_records) records.value = student.value.archive_records
  } catch (error) {
    console.error('获取学生详情失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchPoliticalHistory = async () => {
  try {
    const response = await api.get(`/students/${props.studentId}/political_history/`)
    politicalRecords.value = response.data
  } catch (error) {
    console.error('获取政治面貌历史失败:', error)
  }
}

const fetchRecords = async () => {
  try {
    const response = await api.get(`/students/${props.studentId}/records/`)
    records.value = response.data
  } catch (error) {
    console.error('获取档案记录失败:', error)
  }
}

const fetchStatusChanges = async () => {
  try {
    const response = await api.get('/students/status-changes/', { params: { student: props.studentId } })
    statusChanges.value = response.data.results || response.data
  } catch (error) {
    console.error('获取学籍变动失败:', error)
  }
}

const fetchViewLogs = async () => {
  try {
    const response = await api.get('/students/view-logs/', { params: { student: props.studentId } })
    viewLogs.value = response.data.results || response.data
  } catch (error) {
    console.error('获取查阅日志失败:', error)
  }
}

const formatDateTime = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleString()
}

const viewFiles = (files) => {
  currentFiles.value = files
  fileVisible.value = true
}

const downloadFile = (url) => {
  window.open(url, '_blank')
}

const getStatusType = (status) => {
  const map = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return map[status] || 'info'
}

const viewRecord = (row) => {
  // TODO: 显示记录详情
  console.log('查看记录:', row)
}

watch(() => props.studentId, () => {
  if (props.studentId) {
    fetchStudentDetail()
  }
})

watch(activeTab, (newTab) => {
  if (newTab === 'political' && politicalRecords.value.length === 0) {
    fetchPoliticalHistory()
  } else if (newTab === 'records' && records.value.length === 0) {
    fetchRecords()
  } else if (newTab === 'status' && statusChanges.value.length === 0) {
    fetchStatusChanges()
  } else if (newTab === 'logs' && viewLogs.value.length === 0) {
    fetchViewLogs()
  }
})

onMounted(() => {
  if (props.studentId) {
    fetchStudentDetail()
  }
})
</script>

<style scoped>
.student-detail {
  padding: 20px;
}
</style>
