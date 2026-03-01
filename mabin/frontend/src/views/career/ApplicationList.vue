<template>
  <div class="career-applications">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的投递记录</span>
        </div>
      </template>

      <el-table :data="applications" v-loading="loading">
        <el-table-column prop="company_name" label="公司名称" />
        <el-table-column prop="job_title" label="职位名称" />
        <el-table-column prop="applied_at" label="投递时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.applied_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetails(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="投递详情" width="500px">
      <div v-if="currentApp" class="app-detail">
        <p><strong>公司名称：</strong>{{ currentApp.company_name }}</p>
        <p><strong>职位名称：</strong>{{ currentApp.job_title }}</p>
        <p><strong>投递时间：</strong>{{ formatDate(currentApp.applied_at) }}</p>
        <p><strong>当前状态：</strong>
          <el-tag :type="getStatusType(currentApp.status)">{{ currentApp.status_display }}</el-tag>
        </p>
        <p><strong>求职信：</strong></p>
        <div class="cover-letter">{{ currentApp.cover_letter || '无' }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const applications = ref([])
const detailVisible = ref(false)
const currentApp = ref(null)

const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'viewed': 'primary',
    'interview': 'warning',
    'offer': 'success',
    'rejected': 'danger'
  }
  return map[status] || 'info'
}

const viewDetails = (app) => {
  currentApp.value = app
  detailVisible.value = true
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const fetchApplications = async () => {
  loading.value = true
  try {
    const res = await request.get('/career/applications/')
    applications.value = res.data.results || res.data
  } catch (error) {
    console.error('获取投递记录失败', error)
    ElMessage.error('获取投递记录失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchApplications)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.app-detail p {
  margin-bottom: 12px;
  line-height: 1.6;
}
.cover-letter {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-top: 8px;
  white-space: pre-wrap;
}
</style>
