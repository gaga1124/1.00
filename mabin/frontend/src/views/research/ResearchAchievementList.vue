<template>
  <div class="research-achievements">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>科研成果管理</span>
          <el-button type="primary" @click="handleRegister">成果登记</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchQuery" size="default">
          <el-form-item label="成果名称">
            <el-input v-model="searchQuery.title" placeholder="输入成果名称" clearable @keyup.enter="fetchAchievements" />
          </el-form-item>
          <el-form-item label="成果类型">
            <el-select v-model="searchQuery.achievement_type" placeholder="全部" clearable style="width: 120px">
              <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchQuery.is_verified" placeholder="全部" clearable style="width: 120px">
              <el-option label="已审核" :value="true" />
              <el-option label="待审核" :value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchAchievements">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 成果列表 -->
      <el-table :data="achievements" v-loading="loading" style="width: 100%" border stripe>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="achievement_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.achievement_type)" effect="light">
              {{ typeMap[row.achievement_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="成果名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="achievement-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="first_author_info.real_name" label="第一作者" width="120">
          <template #default="{ row }">
            <div class="author-info">
              <el-avatar :size="24" :src="row.first_author_info?.avatar">{{ row.first_author_info?.real_name?.[0] }}</el-avatar>
              <span class="ml-2">{{ row.first_author_info?.real_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="journal" label="期刊/出版社" width="180" show-overflow-tooltip />
        <el-table-column prop="publish_date" label="发表日期" width="120" sortable />
        <el-table-column prop="is_verified" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_verified ? 'success' : 'warning'" size="small">
              {{ row.is_verified ? '已审核' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-button link type="success" v-if="!row.is_verified && isAdmin" @click="handleVerify(row)">审核</el-button>
            <el-button link type="primary" v-if="row.file" @click="handleDownload(row)">
              <el-icon><Download /></el-icon>下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 登记对话框 -->
    <el-dialog v-model="dialogVisible" title="科研成果登记" width="700px" destroy-on-close>
      <el-form :model="achievementForm" :rules="rules" ref="formRef" label-width="100px" status-icon>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="成果类型" prop="achievement_type">
              <el-select v-model="achievementForm.achievement_type" placeholder="请选择" style="width: 100%">
                <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联项目" prop="project">
              <el-select v-model="achievementForm.project" placeholder="选择关联项目" clearable style="width: 100%">
                <el-option v-for="p in projects" :key="p.id" :label="p.project_name" :value="p.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="成果名称" prop="title">
          <el-input v-model="achievementForm.title" placeholder="请输入成果完整标题" maxlength="200" show-word-limit />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="期刊/出版社" prop="journal">
              <el-input v-model="achievementForm.journal" placeholder="期刊名、出版社或奖项来源" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发表日期" prop="publish_date">
              <el-date-picker v-model="achievementForm.publish_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="卷号" prop="volume">
              <el-input v-model="achievementForm.volume" placeholder="Vol. No." />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="页码" prop="page_range">
              <el-input v-model="achievementForm.page_range" placeholder="pp. 1-10" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="DOI" prop="doi">
              <el-input v-model="achievementForm.doi" placeholder="10.xxx/xxx" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="成果文件" prop="file">
          <el-upload
            class="upload-demo"
            action="/api/research/achievements/upload/"
            :headers="uploadHeaders"
            :limit="1"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
          >
            <el-button type="primary"><el-icon><Upload /></el-icon>点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">请上传论文全文、专利证书扫描件等，不超过 20MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">提交登记</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="成果详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="成果类型">
          <el-tag :type="getTypeTag(currentAchievement.achievement_type)">
            {{ typeMap[currentAchievement.achievement_type] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="成果名称">{{ currentAchievement.title }}</el-descriptions-item>
        <el-descriptions-item label="第一作者">{{ currentAchievement.first_author_info?.real_name }}</el-descriptions-item>
        <el-descriptions-item label="关联项目">{{ currentAchievement.project_name || '无' }}</el-descriptions-item>
        <el-descriptions-item label="期刊/出版社">{{ currentAchievement.journal }}</el-descriptions-item>
        <el-descriptions-item label="发表日期">{{ currentAchievement.publish_date }}</el-descriptions-item>
        <el-descriptions-item label="卷/期/页码">{{ currentAchievement.volume }} {{ currentAchievement.page_range }}</el-descriptions-item>
        <el-descriptions-item label="DOI">{{ currentAchievement.doi }}</el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="currentAchievement.is_verified ? 'success' : 'info'">
            {{ currentAchievement.is_verified ? '已审核' : '待审核' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="奖励金额" v-if="currentAchievement.reward_amount">
          ¥{{ currentAchievement.reward_amount }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Upload } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${userStore.token}`
}))

const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const loading = ref(false)
const achievements = ref([])
const projects = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const submitting = ref(false)
const currentAchievement = ref({})
const formRef = ref(null)

const searchQuery = reactive({
  title: '',
  achievement_type: '',
  is_verified: ''
})

const resetSearch = () => {
  Object.assign(searchQuery, {
    title: '',
    achievement_type: '',
    is_verified: ''
  })
  fetchAchievements()
}

const beforeUpload = (file) => {
  const isLt20M = file.size / 1024 / 1024 < 20
  if (!isLt20M) {
    ElMessage.error('上传文件大小不能超过 20MB!')
  }
  return isLt20M
}

const typeMap = {
  paper: '论文',
  patent: '专利',
  book: '著作',
  award: '获奖',
  other: '其他'
}

const achievementForm = reactive({
  achievement_type: '',
  project: null,
  title: '',
  journal: '',
  publish_date: '',
  volume: '',
  page_range: '',
  doi: '',
  file: null
})

const rules = {
  achievement_type: [{ required: true, message: '请选择成果类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入成果名称', trigger: 'blur' }],
  journal: [{ required: true, message: '请输入期刊或出版社', trigger: 'blur' }],
  publish_date: [{ required: true, message: '请选择发表日期', trigger: 'change' }]
}

const fetchAchievements = async () => {
  loading.value = true
  try {
    const params = { ...searchQuery }
    const response = await api.get('/research/achievements/', { params })
    achievements.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取成果列表失败')
  } finally {
    loading.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/research/projects/')
    projects.value = response.data.results || response.data
  } catch (error) {
    console.error('获取项目列表失败')
  }
}

const handleRegister = () => {
  Object.assign(achievementForm, {
    achievement_type: '',
    project: null,
    title: '',
    journal: '',
    publish_date: '',
    volume: '',
    page_range: '',
    doi: '',
    file: null
  })
  dialogVisible.value = true
}

const handleDetail = (row) => {
  currentAchievement.value = row
  detailVisible.value = true
}

const handleVerify = (row) => {
  ElMessageBox.prompt('请输入奖励金额（可选）', '成果审核', {
    confirmButtonText: '审核通过',
    cancelButtonText: '取消',
    inputPattern: /^\d+(\.\d+)?$/,
    inputErrorMessage: '请输入有效的金额'
  }).then(async ({ value }) => {
    try {
      await api.patch(`/research/achievements/${row.id}/`, {
        is_verified: true,
        reward_amount: value || 0
      })
      ElMessage.success('审核已通过')
      fetchAchievements()
    } catch (error) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDownload = (row) => {
  window.open(row.file, '_blank')
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await api.post('/research/achievements/', achievementForm)
        ElMessage.success('登记成功，请等待审核')
        dialogVisible.value = false
        fetchAchievements()
      } catch (error) {
        console.error('Submit error:', error)
        if (error.response?.data) {
          const data = error.response.data
          const msg = typeof data === 'string' ? data : 
                     data.detail ? data.detail :
                     Object.values(data).flat().join('; ')
          ElMessage.error(msg || '提交失败')
        } else {
          ElMessage.error('提交失败，请检查网络连接')
        }
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleUploadSuccess = (response) => {
  achievementForm.file = response.url
  ElMessage.success('文件上传成功')
}

const getTypeTag = (type) => {
  const map = {
    paper: 'primary',
    patent: 'success',
    book: 'warning',
    award: 'danger',
    other: 'info'
  }
  return map[type] || 'info'
}

onMounted(() => {
  fetchAchievements()
  fetchProjects()
})
</script>

<style scoped>
.research-achievements {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-bar {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}
.achievement-title {
  font-weight: 500;
  color: #409eff;
}
.author-info {
  display: flex;
  align-items: center;
}
.ml-2 {
  margin-left: 8px;
}
</style>
