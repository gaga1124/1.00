<template>
  <div class="job-fair-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>校园招聘会</span>
          <el-input
            v-model="search"
            placeholder="搜索招聘会名称"
            style="width: 300px"
            @input="fetchJobFairs"
          />
        </div>
      </template>

      <el-table :data="jobFairs" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="fair-detail-expand">
              <p><strong>详细描述：</strong></p>
              <div class="text-content">{{ row.description || '暂无描述' }}</div>
              <p><strong>参会企业：</strong></p>
              <div class="companies-list">
                <el-tag 
                  v-for="company in row.companies_info" 
                  :key="company.id"
                  class="company-tag"
                >
                  {{ company.name }}
                </el-tag>
                <span v-if="!row.companies_info?.length">暂无企业信息</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" />
        <el-table-column prop="location" label="地点" width="180" />
        <el-table-column label="时间" width="300">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }} - {{ formatDateTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="人数" width="120">
          <template #default="{ row }">
            {{ row.current_participants }} / {{ row.max_participants }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              :type="row.is_registered ? 'info' : 'primary'" 
              size="small" 
              @click="handleRegister(row)"
              :disabled="row.is_registered || row.current_participants >= row.max_participants"
            >
              {{ row.is_registered ? '已报名' : '立即报名' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const jobFairs = ref([])
const loading = ref(false)
const search = ref('')

const fetchJobFairs = async () => {
  loading.value = true
  try {
    const res = await request.get('/career/job-fairs/', {
      params: { search: search.value }
    })
    jobFairs.value = res.data.results || res.data
  } catch (error) {
    console.error('获取招聘会失败', error)
    ElMessage.error('获取招聘会数据失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async (fair) => {
  try {
    await ElMessageBox.confirm(
      `确定报名参加“${fair.name}”吗？`,
      '确认报名',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    await request.post(`/career/job-fairs/${fair.id}/register/`)
    ElMessage.success('报名成功！')
    fetchJobFairs() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('报名失败', error)
      ElMessage.error(error.response?.data?.detail || '报名失败，请稍后再试')
    }
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

onMounted(fetchJobFairs)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.fair-detail-expand {
  padding: 20px;
}
.text-content {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin: 10px 0 20px 0;
  white-space: pre-wrap;
  color: #606266;
}
.companies-list {
  margin-top: 10px;
}
.company-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}
</style>