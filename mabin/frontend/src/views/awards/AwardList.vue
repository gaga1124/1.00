<template>
  <div class="award-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评奖评优管理</span>
          <el-button type="primary" @click="handleApply" v-if="isStudent">申请奖项</el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="可申请奖项" name="available">
          <el-table :data="awardTypes" v-loading="loading">
            <el-table-column prop="name" label="奖项名称" />
            <el-table-column prop="category" label="类别">
              <template #default="{ row }">
                <el-tag>{{ getCategoryLabel(row.category) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="级别" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">
                <span v-if="row.amount">¥{{ row.amount }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="申请时间" width="300">
              <template #default="{ row }">
                {{ formatDate(row.application_start) }} 至 {{ formatDate(row.application_end) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleApplyAward(row)">申请</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="我的申请" name="my-applications" v-if="isStudent">
          <el-table :data="myApplications" v-loading="loading">
            <el-table-column prop="award_type_name" label="申请奖项" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="match_score" label="匹配度" width="100">
              <template #default="{ row }">
                <el-progress :percentage="row.match_score || 0" :status="row.match_score >= 80 ? 'success' : ''" />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewDetails(row)">详情</el-button>
                <el-button link type="danger" v-if="row.status === 'draft'" @click="handleCancel(row)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="审核列表" name="review" v-if="isTeacher || isAdmin">
          <el-table :data="reviewApplications" v-loading="loading">
            <el-table-column prop="student_name" label="学生姓名" />
            <el-table-column prop="award_type_name" label="申请奖项" />
            <el-table-column prop="match_score" label="匹配度" width="100">
              <template #default="{ row }">
                <el-progress :percentage="row.match_score || 0" />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleReview(row)">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 申请对话框 -->
    <el-dialog v-model="applyVisible" :title="'申请奖项: ' + currentAward?.name" width="600px">
      <el-form :model="applyForm" label-width="100px" ref="applyFormRef">
        <el-form-item label="自动匹配">
          <el-alert
            v-if="matchResult"
            :title="'系统自动匹配度: ' + matchResult.score + '%'"
            :type="matchResult.score >= 80 ? 'success' : 'warning'"
            show-icon
            :closable="false"
          >
            <div v-for="(item, index) in matchResult.details" :key="index" class="match-detail-item">
              <el-icon :color="item.matched ? '#67C23A' : '#F56C6C'">
                <CircleCheck v-if="item.matched" />
                <CircleClose v-else />
              </el-icon>
              <span class="detail-name">{{ item.name }}:</span>
              <span :class="item.matched ? 'status-success' : 'status-fail'">
                {{ item.matched ? '符合' : '不符合' }}
              </span>
              <span v-if="item.value !== undefined" class="detail-value">
                (实际: {{ item.value }}, 要求: {{ item.required }})
              </span>
            </div>
          </el-alert>
          <el-button v-else type="info" size="small" @click="handleMatch">重新检查资格</el-button>
        </el-form-item>
        <el-form-item label="申请理由" required>
          <el-input v-model="applyForm.application_reason" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="主要成果">
          <el-button type="dashed" block @click="addAchievement">添加成果</el-button>
          <div v-for="(item, index) in applyForm.achievements" :key="index" class="achievement-item">
            <el-input v-model="item.title" placeholder="成果名称" />
            <el-button type="danger" icon="Delete" circle @click="applyForm.achievements.splice(index, 1)" />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApplication">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, CircleCheck, CircleClose } from '@element-plus/icons-vue'

const userStore = useUserStore()
const isStudent = computed(() => userStore.user?.student_profile)
const isTeacher = computed(() => userStore.user?.is_teacher || !userStore.user?.student_profile)
const isAdmin = computed(() => userStore.user?.is_superuser)

const loading = ref(false)
const activeTab = ref('available')
const awardTypes = ref([])
const myApplications = ref([])
const reviewApplications = ref([])

const applyVisible = ref(false)
const currentAward = ref(null)
const matchResult = ref(null)
const applyForm = ref({
  application_reason: '',
  achievements: []
})

const fetchAwardTypes = async () => {
  const res = await request.get('/awards/types/')
  awardTypes.value = res.data
}

const fetchMyApplications = async () => {
  if (!isStudent.value) return
  const res = await request.get('/awards/applications/')
  myApplications.value = res.data
}

const fetchReviewList = async () => {
  if (isStudent.value) return
  const res = await request.get('/awards/applications/')
  reviewApplications.value = res.data
}

const getCategoryLabel = (cat) => {
  const map = { scholarship: '奖学金', grant: '助学金', honor: '荣誉称号' }
  return map[cat] || cat
}

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    submitted: 'primary',
    reviewing: 'warning',
    approved: 'success',
    rejected: 'danger',
    publicized: 'success'
  }
  return map[status] || ''
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

const handleApplyAward = (award) => {
  currentAward.value = award
  applyForm.value = {
    application_reason: '',
    achievements: []
  }
  matchResult.value = null
  applyVisible.value = true
  handleMatch()
}

const handleMatch = async () => {
  try {
    const res = await request.post(`/awards/types/${currentAward.value.id}/match/`)
    matchResult.value = res.data
  } catch (error) {
    console.error('匹配失败', error)
  }
}

const addAchievement = () => {
  applyForm.value.achievements.push({ title: '', date: '' })
}

const submitApplication = async () => {
  try {
    await request.post('/awards/applications/', {
      award_type: currentAward.value.id,
      ...applyForm.value,
      match_score: matchResult.value?.score,
      match_details: matchResult.value?.details,
      status: 'submitted'
    })
    ElMessage.success('申请提交成功')
    applyVisible.value = false
    fetchMyApplications()
  } catch (error) {
    ElMessage.error('申请提交失败')
  }
}

const handleReview = (row) => {
  ElMessageBox.prompt('请输入审核意见', '奖项审核', {
    confirmButtonText: '通过',
    cancelButtonText: '驳回',
    distinguishCancelAndClose: true
  }).then(({ value }) => {
    updateStatus(row.id, 'approved', value)
  }).catch((action) => {
    if (action === 'cancel') {
      updateStatus(row.id, 'rejected', '审核驳回')
    }
  })
}

const updateStatus = async (id, status, comment) => {
  try {
    const action = status === 'approved' ? 'approve' : 'reject'
    await request.post(`/awards/applications/${id}/review/`, {
      action,
      comment
    })
    ElMessage.success('审核操作成功')
    fetchReviewList()
  } catch (error) {
    ElMessage.error('审核操作失败')
  }
}

onMounted(() => {
  fetchAwardTypes()
  fetchMyApplications()
  fetchReviewList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.achievement-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.match-detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.detail-name {
  font-weight: bold;
}
.status-success {
  color: #67C23A;
}
.status-fail {
  color: #F56C6C;
}
.detail-value {
  font-size: 12px;
  color: #909399;
}
</style>
