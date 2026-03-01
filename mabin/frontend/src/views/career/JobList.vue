<template>
  <div class="job-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>企业招聘信息</span>
          <el-input
            v-model="search"
            placeholder="搜索职位或公司"
            style="width: 300px"
            @input="fetchJobs"
          />
        </div>
      </template>

      <el-table :data="jobs" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="job-detail-expand">
              <p><strong>职位描述：</strong></p>
              <div class="text-content">{{ row.description }}</div>
              <p><strong>任职要求：</strong></p>
              <div class="text-content">{{ row.requirements }}</div>
              <p v-if="row.benefits"><strong>福利待遇：</strong></p>
              <div v-if="row.benefits" class="text-content">{{ row.benefits }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="职位名称" min-width="150" />
        <el-table-column prop="company_name" label="招聘单位" width="180" />
        <el-table-column prop="salary_range" label="薪资范围" width="120" />
        <el-table-column prop="location" label="工作地点" width="120" />
        <el-table-column prop="job_type_display" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.job_type === 'internship' ? 'warning' : 'success'">
              {{ row.job_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止日期" width="120" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleApplyClick(row)"
              :disabled="row.is_applied"
            >
              {{ row.is_applied ? '已投递' : '立即投递' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 投递对话框 -->
    <el-dialog v-model="applyVisible" title="职位投递" width="500px">
      <el-form :model="applyForm" label-width="100px">
        <el-form-item label="选择简历" required>
          <el-select v-model="applyForm.resume" placeholder="请选择简历" style="width: 100%">
            <el-option
              v-for="resume in resumes"
              :key="resume.id"
              :label="resume.name"
              :value="resume.id"
            />
          </el-select>
          <div class="form-tip">如果没有简历，请先去“个人中心-我的简历”创建</div>
        </el-form-item>
        <el-form-item label="求职信">
          <el-input
            v-model="applyForm.cover_letter"
            type="textarea"
            rows="4"
            placeholder="简要介绍你的优势..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApplication" :loading="submitting">确认投递</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const jobs = ref([])
const loading = ref(false)
const search = ref('')

// 投递相关
const applyVisible = ref(false)
const submitting = ref(false)
const resumes = ref([])
const currentJob = ref(null)
const applyForm = reactive({
  resume: null,
  cover_letter: ''
})

const fetchJobs = async () => {
  loading.value = true
  try {
    const res = await request.get('/career/jobs/', {
      params: { search: search.value }
    })
    jobs.value = res.data.results || res.data
  } catch (error) {
    console.error('获取招聘信息失败', error)
    ElMessage.error('获取招聘信息失败')
  } finally {
    loading.value = false
  }
}

const fetchResumes = async () => {
  try {
    const res = await request.get('/career/resumes/')
    resumes.value = res.data.results || res.data
    // 默认选择第一个简历
    if (resumes.value.length > 0) {
      applyForm.resume = resumes.value[0].id
    }
  } catch (error) {
    console.error('获取简历列表失败', error)
  }
}

const handleApplyClick = (job) => {
  currentJob.value = job
  applyVisible.value = true
  fetchResumes()
}

const submitApplication = async () => {
  if (!applyForm.resume) {
    ElMessage.warning('请选择简历')
    return
  }
  
  submitting.value = true
  try {
    await request.post('/career/applications/', {
      job: currentJob.value.id,
      resume: applyForm.resume,
      cover_letter: applyForm.cover_letter
    })
    ElMessage.success('投递成功！')
    applyVisible.value = false
    fetchJobs() // 刷新状态
  } catch (error) {
    console.error('投递失败', error)
    ElMessage.error(error.response?.data?.detail || '投递失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchJobs)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.job-detail-expand {
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
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
