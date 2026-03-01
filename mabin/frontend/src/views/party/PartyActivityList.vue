<template>
  <div class="party-activity-list">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>党团活动管理</span>
          <el-button type="primary" @click="handleAdd" v-if="isAdmin">发布活动</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchQuery" size="default">
          <el-form-item label="活动类型">
            <el-select v-model="searchQuery.activity_type" placeholder="全部" clearable style="width: 150px">
              <el-option label="组织生活会" value="meeting" />
              <el-option label="党课/团课" value="lesson" />
              <el-option label="志愿活动" value="volunteer" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属支部">
            <el-select v-model="searchQuery.branch" placeholder="全部" clearable style="width: 200px">
              <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchActivities">查询</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 列表 -->
      <el-table :data="activities" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="活动标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="activity_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActivityTypeTag(row.activity_type)">{{ activityTypeMap[row.activity_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="branch_info.name" label="主办支部" width="180" />
        <el-table-column prop="start_time" label="开始时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="volunteer_hours_given" label="志愿时长" width="100">
          <template #default="{ row }">
            <span v-if="row.activity_type === 'volunteer'">{{ row.volunteer_hours_given }}h</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-button link type="success" @click="handleJoin(row)" v-if="!isParticipant(row)">报名</el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="isAdmin">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 活动详情对话框 -->
    <el-dialog v-model="detailVisible" :title="currentActivity.title" width="600px">
      <div class="activity-detail">
        <p><strong>类型：</strong>{{ activityTypeMap[currentActivity.activity_type] }}</p>
        <p><strong>地点：</strong>{{ currentActivity.location }}</p>
        <p><strong>时间：</strong>{{ formatDateTime(currentActivity.start_time) }} 至 {{ formatDateTime(currentActivity.end_time) }}</p>
        <p v-if="currentActivity.activity_type === 'volunteer'"><strong>志愿时长：</strong>{{ currentActivity.volunteer_hours_given }} 小时</p>
        <div class="content-box">
          <strong>活动内容：</strong>
          <div class="content">{{ currentActivity.content }}</div>
        </div>
      </div>
    </el-dialog>

    <!-- 发布活动对话框 -->
    <el-dialog v-model="addVisible" title="发布新活动" width="600px">
      <el-form :model="addForm" label-width="100px" ref="addFormRef" :rules="rules">
        <el-form-item label="标题" prop="title">
          <el-input v-model="addForm.title" />
        </el-form-item>
        <el-form-item label="类型" prop="activity_type">
          <el-select v-model="addForm.activity_type" style="width: 100%">
            <el-option label="组织生活会" value="meeting" />
            <el-option label="党课/团课" value="lesson" />
            <el-option label="志愿活动" value="volunteer" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属支部" prop="branch">
          <el-select v-model="addForm.branch" style="width: 100%">
            <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地点" prop="location">
          <el-input v-model="addForm.location" />
        </el-form-item>
        <el-form-item label="时间范围" prop="timeRange">
          <el-date-picker
            v-model="addForm.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="志愿时长" v-if="addForm.activity_type === 'volunteer'">
          <el-input-number v-model="addForm.volunteer_hours_given" :min="0" :step="0.5" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input type="textarea" v-model="addForm.content" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.role === 'teacher')

const loading = ref(false)
const activities = ref([])
const branches = ref([])
const detailVisible = ref(false)
const addVisible = ref(false)
const currentActivity = ref({})

const searchQuery = reactive({
  activity_type: '',
  branch: ''
})

const activityTypeMap = {
  meeting: '组织生活会',
  lesson: '党课/团课',
  volunteer: '志愿活动',
  other: '其他'
}

const addForm = reactive({
  title: '',
  activity_type: 'meeting',
  branch: '',
  location: '',
  timeRange: [],
  content: '',
  volunteer_hours_given: 0
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  activity_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  branch: [{ required: true, message: '请选择支部', trigger: 'change' }],
  location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
  timeRange: [{ required: true, message: '请选择时间', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/party/activities/', { params: searchQuery })
    activities.value = response.data
  } catch (error) {
    ElMessage.error('获取活动列表失败')
  } finally {
    loading.value = false
  }
}

const fetchBranches = async () => {
  try {
    const response = await axios.get('/api/party/branches/')
    branches.value = response.data
  } catch (error) {
    console.error('获取支部列表失败')
  }
}

const handleAdd = () => {
  addVisible.value = true
}

const submitAdd = async () => {
  try {
    const postData = {
      ...addForm,
      start_time: addForm.timeRange[0],
      end_time: addForm.timeRange[1]
    }
    delete postData.timeRange
    await axios.post('/api/party/activities/', postData)
    ElMessage.success('发布成功')
    addVisible.value = false
    fetchActivities()
  } catch (error) {
    ElMessage.error('发布失败')
  }
}

const handleDetail = (row) => {
  currentActivity.value = row
  detailVisible.value = true
}

const handleJoin = async (row) => {
  try {
    await axios.post(`/api/party/activities/${row.id}/join/`)
    ElMessage.success('报名成功')
    fetchActivities()
  } catch (error) {
    ElMessage.error('报名失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该活动吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await axios.delete(`/api/party/activities/${row.id}/`)
      ElMessage.success('删除成功')
      fetchActivities()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const isParticipant = (row) => {
  return row.participants?.includes(userStore.user?.id)
}

const getActivityTypeTag = (type) => {
  const map = {
    meeting: 'primary',
    lesson: 'warning',
    volunteer: 'success',
    other: 'info'
  }
  return map[type] || 'info'
}

const formatDateTime = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchActivities()
  fetchBranches()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  margin-bottom: 20px;
}
.activity-detail p {
  margin: 10px 0;
  line-height: 1.6;
}
.content-box {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
.content {
  margin-top: 10px;
  white-space: pre-wrap;
}
</style>
