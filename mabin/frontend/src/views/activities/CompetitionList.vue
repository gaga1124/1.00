<template>
  <div class="competition-list">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>学科竞赛管理</span>
          <el-button type="primary" @click="handleAdd" v-if="isAdmin">发布竞赛</el-button>
        </div>
      </template>

      <!-- 列表 -->
      <el-row :gutter="20">
        <el-col :span="8" v-for="comp in competitions" :key="comp.id" style="margin-bottom: 20px">
          <el-card shadow="hover" class="comp-card">
            <div class="comp-header">
              <el-tag size="small" :type="comp.is_active ? 'success' : 'info'">
                {{ comp.is_active ? '进行中' : '已结束' }}
              </el-tag>
              <span class="comp-level">{{ comp.level }}</span>
            </div>
            <h3 class="comp-title">{{ comp.title }}</h3>
            <div class="comp-info">
              <p><el-icon><OfficeBuilding /></el-icon> {{ comp.organizer }}</p>
              <p><el-icon><Calendar /></el-icon> 截止：{{ formatDateTime(comp.registration_deadline) }}</p>
            </div>
            <div class="comp-actions">
              <el-button type="primary" @click="handleRegister(comp)" :disabled="!comp.is_active">立即报名</el-button>
              <el-button @click="handleTeams(comp)">参赛队伍</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 报名对话框 -->
    <el-dialog v-model="registerVisible" title="竞赛报名" width="500px">
      <el-form :model="regForm" label-width="100px" ref="regFormRef" :rules="regRules">
        <el-form-item label="团队名称" prop="team_name">
          <el-input v-model="regForm.team_name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="指导教师" prop="advisor">
          <el-select v-model="regForm.advisor" placeholder="请选择指导教师" filterable style="width: 100%">
            <el-option v-for="t in teachers" :key="t.id" :label="t.real_name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="团队成员">
          <el-select v-model="regForm.members" multiple placeholder="请选择团队成员" filterable style="width: 100%">
            <el-option v-for="s in students" :key="s.id" :label="s.real_name" :value="s.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRegister">提交报名</el-button>
      </template>
    </el-dialog>

    <!-- 参赛队伍/作品管理对话框 -->
    <el-dialog v-model="teamsVisible" :title="`参赛队伍 - ${currentComp.title}`" width="900px">
      <el-table :data="compTeams" style="width: 100%">
        <el-table-column prop="team_name" label="团队名称" width="150" />
        <el-table-column prop="leader_info.real_name" label="负责人" width="100" />
        <el-table-column prop="advisor_info.real_name" label="指导教师" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="成绩" width="80" />
        <el-table-column prop="award_level" label="奖项" width="100" />
        <el-table-column label="操作" min-width="180">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleUploadWork(row)" v-if="canManageTeam(row)">提交作品</el-button>
            <el-button link type="warning" @click="handleScore(row)" v-if="isAdmin">打分</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 打分对话框 -->
    <el-dialog v-model="scoreVisible" title="作品打分/评奖" width="400px">
      <el-form :model="scoreForm" label-width="80px">
        <el-form-item label="成绩">
          <el-input-number v-model="scoreForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="奖项">
          <el-select v-model="scoreForm.award_level" placeholder="请选择奖项" style="width: 100%">
            <el-option label="特等奖" value="特等奖" />
            <el-option label="一等奖" value="一等奖" />
            <el-option label="二等奖" value="二等奖" />
            <el-option label="三等奖" value="三等奖" />
            <el-option label="优秀奖" value="优秀奖" />
            <el-option label="无" value="" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scoreVisible = false">取消</el-button>
        <el-button type="primary" @click="submitScore">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { OfficeBuilding, Calendar } from '@element-plus/icons-vue'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.role === 'teacher')

const competitions = ref([])
const compTeams = ref([])
const teachers = ref([])
const students = ref([])
const currentComp = ref({})
const currentTeam = ref({})

const registerVisible = ref(false)
const teamsVisible = ref(false)
const scoreVisible = ref(false)

const regForm = reactive({
  team_name: '',
  advisor: '',
  members: []
})

const scoreForm = reactive({
  score: 0,
  award_level: ''
})

const regRules = {
  team_name: [{ required: true, message: '请输入团队名称', trigger: 'blur' }],
  advisor: [{ required: true, message: '请选择指导教师', trigger: 'change' }]
}

const fetchCompetitions = async () => {
  try {
    const response = await axios.get('/api/activities/competitions/')
    competitions.value = response.data
  } catch (error) {
    ElMessage.error('获取竞赛列表失败')
  }
}

const fetchBaseData = async () => {
  try {
    const [tRes, sRes] = await Promise.all([
      axios.get('/api/rbac/users/?role=teacher'),
      axios.get('/api/rbac/users/?role=student')
    ])
    teachers.value = tRes.data
    students.value = sRes.data
  } catch (error) {
    console.error('获取基础数据失败')
  }
}

const handleRegister = (comp) => {
  currentComp.value = comp
  regForm.team_name = ''
  regForm.advisor = ''
  regForm.members = []
  registerVisible.value = true
}

const submitRegister = async () => {
  try {
    await axios.post(`/api/activities/competitions/${currentComp.value.id}/register/`, regForm)
    ElMessage.success('报名成功')
    registerVisible.value = false
  } catch (error) {
    ElMessage.error('报名失败')
  }
}

const handleTeams = async (comp) => {
  currentComp.value = comp
  try {
    const response = await axios.get(`/api/activities/competitions/${comp.id}/teams/`)
    compTeams.value = response.data
    teamsVisible.value = true
  } catch (error) {
    ElMessage.error('获取队伍列表失败')
  }
}

const handleScore = (team) => {
  currentTeam.value = team
  scoreForm.score = team.score || 0
  scoreForm.award_level = team.award_level || ''
  scoreVisible.value = true
}

const submitScore = async () => {
  try {
    await axios.post(`/api/activities/competition-teams/${currentTeam.value.id}/score/`, scoreForm)
    ElMessage.success('打分成功')
    scoreVisible.value = false
    handleTeams(currentComp.value)
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const canManageTeam = (team) => {
  return team.leader === userStore.user?.id || isAdmin.value
}

const formatDateTime = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCompetitions()
  fetchBaseData()
})
</script>

<style scoped>
.comp-card {
  height: 220px;
  display: flex;
  flex-direction: column;
}
.comp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.comp-level {
  font-size: 12px;
  color: #909399;
}
.comp-title {
  margin: 0 0 15px 0;
  font-size: 18px;
  height: 50px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.comp-info {
  flex: 1;
  font-size: 14px;
  color: #606266;
}
.comp-info p {
  margin: 5px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.comp-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}
</style>
