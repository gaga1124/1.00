<template>
  <div class="social-practice-list">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>社会实践管理</span>
          <el-button type="primary" @click="handleAdd">申报新项目</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchQuery" size="default">
          <el-form-item label="实践类型">
            <el-select v-model="searchQuery.practice_type" placeholder="全部" clearable style="width: 150px">
              <el-option label="三下乡" value="三下乡" />
              <el-option label="返家乡" value="返家乡" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目状态">
            <el-select v-model="searchQuery.status" placeholder="全部" clearable style="width: 150px">
              <el-option v-for="(label, key) in statusMap" :key="key" :label="label" :value="key" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchPractices">查询</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 列表 -->
      <el-table :data="practices" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="活动标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="practice_type" label="实践类型" width="120" />
        <el-table-column prop="team_name" label="团队名称" width="150" />
        <el-table-column prop="leader_info.real_name" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-button link type="success" @click="handleUpload(row)" v-if="canUpload(row)">成果提交</el-button>
            <el-button link type="warning" @click="handleApprove(row)" v-if="isAdmin && row.status === 'declared'">立项审核</el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="canDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 申报对话框 -->
    <el-dialog v-model="addVisible" title="社会实践项目申报" width="600px">
      <el-form :model="addForm" label-width="100px" ref="addFormRef" :rules="rules">
        <el-form-item label="项目标题" prop="title">
          <el-input v-model="addForm.title" placeholder="请输入活动标题" />
        </el-form-item>
        <el-form-item label="实践类型" prop="practice_type">
          <el-select v-model="addForm.practice_type" style="width: 100%">
            <el-option label="三下乡" value="三下乡" />
            <el-option label="返家乡" value="返家乡" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="团队名称" prop="team_name">
          <el-input v-model="addForm.team_name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="活动简介" prop="description">
          <el-input type="textarea" v-model="addForm.description" :rows="4" placeholder="请输入活动简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">提交申报</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="项目详情" width="700px">
      <div class="practice-detail">
        <h3>{{ currentPractice.title }}</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="实践类型">{{ currentPractice.practice_type }}</el-descriptions-item>
          <el-descriptions-item label="项目状态">
            <el-tag :type="getStatusTag(currentPractice.status)">{{ statusMap[currentPractice.status] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="团队名称">{{ currentPractice.team_name }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentPractice.leader_info?.real_name }}</el-descriptions-item>
          <el-descriptions-item label="创建日期">{{ formatDateTime(currentPractice.created_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="section">
          <h4>活动简介</h4>
          <p class="description">{{ currentPractice.description }}</p>
        </div>

        <div class="section" v-if="currentPractice.report_file">
          <h4>活动报告</h4>
          <el-link type="primary" :href="currentPractice.report_file" target="_blank">
            <el-icon><Document /></el-icon> 查看活动报告
          </el-link>
        </div>

        <div class="section" v-if="currentPractice.media_files?.length > 0">
          <h4>照片/视频展示</h4>
          <div class="media-list">
            <el-image 
              v-for="(url, index) in currentPractice.media_files" 
              :key="index"
              :src="url" 
              :preview-src-list="currentPractice.media_files"
              fit="cover"
              class="media-item"
            />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 成果提交对话框 -->
    <el-dialog v-model="uploadVisible" title="成果材料提交" width="500px">
      <el-form label-width="100px">
        <el-form-item label="活动报告">
          <el-upload
            class="upload-demo"
            action="/api/activities/practices/upload_report/"
            :data="{ practice_id: currentPractice.id }"
            :on-success="handleUploadSuccess"
            :limit="1"
          >
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">只能上传 PDF/Word 文件</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="照片/视频">
          <el-upload
            action="/api/activities/practices/upload_media/"
            :data="{ practice_id: currentPractice.id }"
            multiple
            list-type="picture-card"
            :on-success="handleMediaSuccess"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">完成</el-button>
        <el-button type="primary" @click="submitFinish">确认结项</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { Document, Plus } from '@element-plus/icons-vue'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.role === 'teacher')

const loading = ref(false)
const practices = ref([])
const addVisible = ref(false)
const detailVisible = ref(false)
const uploadVisible = ref(false)
const currentPractice = ref({})

const statusMap = {
  declared: '已申报',
  approved: '已立项',
  submitted: '成果提交',
  completed: '已结项',
  excellent: '评优'
}

const searchQuery = reactive({
  practice_type: '',
  status: ''
})

const addForm = reactive({
  title: '',
  practice_type: '三下乡',
  team_name: '',
  description: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  practice_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入简介', trigger: 'blur' }]
}

const fetchPractices = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/activities/practices/', { params: searchQuery })
    practices.value = response.data
  } catch (error) {
    ElMessage.error('获取实践列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  addVisible.value = true
}

const submitAdd = async () => {
  try {
    await axios.post('/api/activities/practices/', addForm)
    ElMessage.success('申报提交成功')
    addVisible.value = false
    fetchPractices()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const handleDetail = (row) => {
  currentPractice.value = row
  detailVisible.value = true
}

const handleUpload = (row) => {
  currentPractice.value = row
  uploadVisible.value = true
}

const handleApprove = (row) => {
  ElMessageBox.confirm('确认批准该项目立项吗？', '提示').then(async () => {
    try {
      await axios.post(`/api/activities/practices/${row.id}/approve/`)
      ElMessage.success('审核通过')
      fetchPractices()
    } catch (error) {
      ElMessage.error('审核失败')
    }
  })
}

const handleUploadSuccess = () => {
  ElMessage.success('报告上传成功')
  fetchPractices()
}

const handleMediaSuccess = () => {
  ElMessage.success('材料上传成功')
  fetchPractices()
}

const submitFinish = async () => {
  try {
    await axios.post(`/api/activities/practices/${currentPractice.value.id}/submit_results/`)
    ElMessage.success('成果提交成功')
    uploadVisible.value = false
    fetchPractices()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await axios.delete(`/api/activities/practices/${row.id}/`)
      ElMessage.success('删除成功')
      fetchPractices()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const canUpload = (row) => {
  return (row.status === 'approved' || row.status === 'submitted') && (row.leader === userStore.user?.id || isAdmin.value)
}

const canDelete = (row) => {
  return isAdmin.value || (row.status === 'declared' && row.leader === userStore.user?.id)
}

const getStatusTag = (status) => {
  const map = {
    declared: 'info',
    approved: 'primary',
    submitted: 'warning',
    completed: 'success',
    excellent: 'danger'
  }
  return map[status] || 'info'
}

const formatDateTime = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchPractices()
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
.practice-detail h3 {
  margin-bottom: 20px;
  text-align: center;
}
.section {
  margin-top: 25px;
}
.section h4 {
  border-left: 4px solid #409EFF;
  padding-left: 10px;
  margin-bottom: 15px;
}
.description {
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}
.media-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.media-item {
  width: 120px;
  height: 120px;
  border-radius: 4px;
}
</style>
