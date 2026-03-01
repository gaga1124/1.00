<template>
  <div class="live-checkin page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>教务管理</el-breadcrumb-item>
        <el-breadcrumb-item>考勤管理</el-breadcrumb-item>
        <el-breadcrumb-item>实时签到</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-row :gutter="20">
      <!-- 教师端：发起签到 -->
      <el-col :span="24" v-if="isTeacher">
        <el-card class="action-card" v-if="!activeSession">
          <template #header>
            <div class="card-header">
              <span>发起新签到</span>
            </div>
          </template>
          <el-form :model="sessionForm" label-width="100px" style="max-width: 500px">
            <el-form-item label="选择课程" required>
              <el-select v-model="sessionForm.course" placeholder="请选择课程" style="width: 100%">
                <el-option v-for="c in teacherCourses" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间段">
              <el-input v-model="sessionForm.time_slot" placeholder="如：第一节课" />
            </el-form-item>
            <el-form-item label="有效时长">
              <el-select v-model="sessionForm.duration" style="width: 100%">
                <el-option label="5分钟" :value="5" />
                <el-option label="10分钟" :value="10" />
                <el-option label="15分钟" :value="15" />
                <el-option label="30分钟" :value="30" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="startSession" :loading="loading">开始签到</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="session-active-card" v-else>
          <template #header>
            <div class="card-header">
              <span>签到进行中: {{ activeSession.course_name }}</span>
              <el-button type="danger" size="small" @click="closeSession">结束签到</el-button>
            </div>
          </template>
          
          <div class="session-info-display">
            <div class="code-box">
              <div class="label">签到码</div>
              <div class="code">{{ activeSession.check_in_code }}</div>
            </div>
            <div class="stats-box">
              <el-progress type="circle" :percentage="presentPercentage" :color="progressColor" />
              <div class="stats-text">
                <div class="count">{{ activeSession.present_count }} / {{ activeSession.total_count }}</div>
                <div class="label">已签到人数</div>
              </div>
            </div>
          </div>

          <div class="realtime-list mt-20">
            <h3>最近签到</h3>
            <el-table :data="recentRecords" style="width: 100%">
              <el-table-column prop="student_name" label="学生姓名" />
              <el-table-column prop="student_id" label="学号" />
              <el-table-column prop="created_at" label="签到时间">
                <template #default="{ row }">
                  {{ formatTime(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 学生端：参与签到 -->
      <el-col :span="24" v-if="isStudent">
        <el-card class="student-checkin-card">
          <template #header>
            <div class="card-header">
              <span>课程签到</span>
            </div>
          </template>
          
          <div v-if="activeSessions.length > 0">
            <div v-for="session in activeSessions" :key="session.id" class="active-session-item">
              <div class="session-detail">
                <h4>{{ session.course_name }}</h4>
                <p>{{ session.time_slot }} | 教师: {{ session.teacher_name }}</p>
              </div>
              <div class="checkin-input-area" v-if="!hasCheckedIn(session.id)">
                <el-input 
                  v-model="checkInCodes[session.id]" 
                  placeholder="请输入4位签到码" 
                  maxlength="4"
                  style="width: 200px; margin-right: 10px"
                />
                <el-button type="primary" @click="submitCheckIn(session)">立即签到</el-button>
              </div>
              <el-tag v-else type="success" size="large">已成功签到</el-tag>
            </div>
          </div>
          <el-empty v-else description="当前暂无正在进行的签到会话" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStudent = computed(() => userStore.user?.role === 'student')

const loading = ref(false)
const teacherCourses = ref([])
const activeSession = ref(null)
const recentRecords = ref([])
const timer = ref(null)

const sessionForm = reactive({
  course: '',
  time_slot: '',
  duration: 10
})

// 学生端数据
const activeSessions = ref([])
const checkInCodes = reactive({})
const myRecords = ref([])

const presentPercentage = computed(() => {
  if (!activeSession.value || activeSession.value.total_count === 0) return 0
  return Math.round((activeSession.value.present_count / activeSession.value.total_count) * 100)
})

const progressColor = computed(() => {
  if (presentPercentage.value < 50) return '#f56c6c'
  if (presentPercentage.value < 80) return '#e6a23c'
  return '#67c23a'
})

const fetchTeacherCourses = async () => {
  try {
    const res = await api.get('/academic/courses/')
    teacherCourses.value = res.data.results || []
  } catch (e) {
    ElMessage.error('获取课程列表失败')
  }
}

const fetchActiveSession = async () => {
  try {
    const res = await api.get('/academic/attendance-sessions/', { params: { is_active: true } })
    const sessions = res.data.results || []
    if (isTeacher.value) {
      activeSession.value = sessions[0] || null
      if (activeSession.value) {
        fetchRecentRecords()
      }
    } else {
      activeSessions.value = sessions
    }
  } catch (e) {
    console.error('获取签到状态失败', e)
  }
}

const fetchRecentRecords = async () => {
  if (!activeSession.value) return
  try {
    const res = await api.get('/academic/attendances/', { 
      params: { session: activeSession.value.id, ordering: '-created_at' } 
    })
    recentRecords.value = res.data.results || []
    // 更新主Session的人数统计
    activeSession.value.present_count = recentRecords.value.length
  } catch (e) {
    console.error('获取签到记录失败', e)
  }
}

const startSession = async () => {
  if (!sessionForm.course) return ElMessage.warning('请选择课程')
  loading.value = true
  try {
    const expire_at = new Date(Date.now() + sessionForm.duration * 60000).toISOString()
    const res = await api.post('/academic/attendance-sessions/', {
      course: sessionForm.course,
      time_slot: sessionForm.time_slot,
      expire_at
    })
    activeSession.value = res.data
    ElMessage.success('签到已开启')
    startPolling()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '开启签到失败')
  } finally {
    loading.value = false
  }
}

const closeSession = async () => {
  try {
    await ElMessageBox.confirm('确定要手动结束本次签到吗？', '提示')
    await api.post(`/academic/attendance-sessions/${activeSession.value.id}/close/`)
    activeSession.value = null
    recentRecords.value = []
    stopPolling()
    ElMessage.success('签到已结束')
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('操作失败')
  }
}

// 学生端方法
const fetchMyRecords = async () => {
  try {
    const res = await api.get('/academic/attendances/')
    myRecords.value = res.data.results || []
  } catch (e) {
    console.error('获取我的签到记录失败', e)
  }
}

const hasCheckedIn = (sessionId) => {
  return myRecords.value.some(r => r.session === sessionId)
}

const submitCheckIn = async (session) => {
  const code = checkInCodes[session.id]
  if (!code || code.length !== 4) return ElMessage.warning('请输入4位签到码')
  
  try {
    await api.post('/academic/attendances/check_in/', {
      session_id: session.id,
      code: code
    })
    ElMessage.success('签到成功！')
    fetchMyRecords()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '签到失败')
  }
}

const startPolling = () => {
  stopPolling()
  timer.value = setInterval(() => {
    if (isTeacher.value) {
      fetchRecentRecords()
    } else {
      fetchActiveSession()
    }
  }, 5000)
}

const stopPolling = () => {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

const formatTime = (time) => {
  return new Date(time).toLocaleTimeString()
}

onMounted(() => {
  if (isTeacher.value) {
    fetchTeacherCourses()
  }
  fetchActiveSession()
  if (isStudent.value) {
    fetchMyRecords()
  }
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.live-checkin {
  padding: 20px;
}
.action-card {
  margin-bottom: 20px;
}
.session-active-card {
  text-align: center;
}
.session-info-display {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 40px 0;
  background: #fdfdfd;
  border-radius: 8px;
  flex-wrap: wrap;
}
.code-box {
  margin-bottom: 20px;
  .label { font-size: 16px; color: #909399; margin-bottom: 10px; }
  .code { font-size: 64px; font-weight: bold; letter-spacing: 8px; color: #409eff; }
}
.stats-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  .stats-text {
    margin-top: 15px;
    .count { font-size: 24px; font-weight: bold; }
    .label { font-size: 14px; color: #909399; }
  }
}
.active-session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 15px;
  transition: all 0.3s;
  flex-wrap: wrap;
}
.active-session-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}
.session-detail {
  flex: 1;
  min-width: 200px;
}
.session-detail h4 { margin: 0 0 8px 0; font-size: 18px; }
.session-detail p { margin: 0; color: #606266; font-size: 14px; }
.checkin-input-area {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .live-checkin {
    padding: 10px;
  }
  .session-info-display {
    flex-direction: column;
    padding: 20px 0;
  }
  .code-box .code {
    font-size: 48px;
    letter-spacing: 4px;
  }
  .active-session-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .checkin-input-area {
    width: 100%;
    margin-top: 15px;
  }
  .checkin-input-area .el-input {
    flex: 1;
    width: auto !important;
  }
}
</style>
