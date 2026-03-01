<template>
  <div class="research-team">
    <el-row :gutter="20" v-loading="loading">
      <!-- 团队列表 -->
      <el-col :span="6">
        <el-card class="team-sidebar" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">科研团队</span>
              <el-button link type="primary" @click="handleCreateTeam" v-if="isStaff">
                <el-icon><Plus /></el-icon>新建
              </el-button>
            </div>
          </template>
          <el-scrollbar>
            <el-menu :default-active="activeTeamId" @select="handleTeamSelect" class="team-menu">
              <el-menu-item v-for="team in teams" :key="team.id" :index="team.id.toString()">
                <el-icon><User /></el-icon>
                <span>{{ team.name }}</span>
              </el-menu-item>
            </el-menu>
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- 团队详情与协作 -->
      <el-col :span="18">
        <el-card v-if="activeTeam" class="team-content" shadow="never">
          <template #header>
            <div class="team-header">
              <div class="team-info">
                <div class="team-title-row">
                  <h2>{{ activeTeam.name }}</h2>
                  <el-tag size="small" type="success" effect="plain" style="margin-left: 10px">
                    {{ activeTeam.members_info?.length || 0 }} 成员
                  </el-tag>
                </div>
                <p class="description">{{ activeTeam.description }}</p>
              </div>
              <div class="team-actions" v-if="isLeader">
                <el-button type="primary" plain @click="handleAddMember">
                  <el-icon><Plus /></el-icon>添加成员
                </el-button>
                <el-button type="danger" plain v-if="isAdmin" @click="handleDeleteTeam">
                  <el-icon><Delete /></el-icon>删除团队
                </el-button>
              </div>
            </div>
          </template>

          <el-tabs v-model="activeTab" class="custom-tabs">
            <!-- 成员列表 -->
            <el-tab-pane name="members">
              <template #label>
                <span class="tab-label"><el-icon><Avatar /></el-icon> 团队成员</span>
              </template>
              <el-table :data="activeTeam.members_info" style="width: 100%">
                <el-table-column label="成员" width="200">
                  <template #default="{ row }">
                    <div class="member-cell">
                      <el-avatar :size="32" :src="row.avatar" style="margin-right: 10px">{{ row.real_name?.[0] }}</el-avatar>
                      <span>{{ row.real_name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="username" label="工号/学号" width="120" />
                <el-table-column label="身份" width="120">
                  <template #default="{ row }">
                    <el-tag :type="row.id === activeTeam.leader ? 'danger' : 'info'" size="small">
                      {{ row.id === activeTeam.leader ? '负责人' : '成员' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" align="right">
                  <template #default="{ row }">
                    <el-button 
                      link 
                      type="danger" 
                      v-if="row.id !== activeTeam.leader && isLeader"
                      @click="handleRemoveMember(row)"
                    >移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 任务分配 -->
            <el-tab-pane name="tasks">
              <template #label>
                <span class="tab-label"><el-icon><Checked /></el-icon> 任务协作</span>
              </template>
              <div class="tab-header">
                <el-button type="primary" size="default" @click="handleAddTask" v-if="isLeader">
                  <el-icon><Plus /></el-icon>发布任务
                </el-button>
              </div>
              <el-table :data="activeTeam.tasks" style="width: 100%; margin-top: 15px">
                <el-table-column prop="title" label="任务名称" show-overflow-tooltip />
                <el-table-column label="执行人" width="120">
                  <template #default="{ row }">
                    <div class="assignee-cell">
                      <el-avatar :size="24" :src="row.assignee_info?.avatar" style="margin-right: 5px">
                        {{ row.assignee_info?.real_name?.[0] }}
                      </el-avatar>
                      <span>{{ row.assignee_info?.real_name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="due_date" label="截止日期" width="120" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getTaskStatusTag(row.status)" effect="light">{{ taskStatusMap[row.status] }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" align="right">
                  <template #default="{ row }">
                    <el-button link type="primary" @click="handleTaskDetail(row)">详情</el-button>
                    <el-button 
                      link 
                      type="success" 
                      v-if="row.status !== 'completed' && (row.assignee === userStore.user?.id || isLeader)" 
                      @click="handleCompleteTask(row)"
                    >完成</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>

            <!-- 会议纪要 -->
            <el-tab-pane name="meetings">
              <template #label>
                <span class="tab-label"><el-icon><Calendar /></el-icon> 会议纪要</span>
              </template>
              <div class="tab-header">
                <el-button type="primary" size="default" @click="handleAddMeeting" v-if="isLeader">
                  <el-icon><Calendar /></el-icon>记录会议
                </el-button>
              </div>
              <div class="timeline-container">
                <el-timeline style="margin-top: 20px">
                  <el-timeline-item
                    v-for="meeting in activeTeam.meetings"
                    :key="meeting.id"
                    :timestamp="formatDateTime(meeting.meeting_time)"
                    placement="top"
                    type="primary"
                  >
                    <el-card class="meeting-card" shadow="hover">
                      <div class="meeting-header-row">
                        <h4>{{ meeting.title }}</h4>
                        <span class="location"><el-icon><Location /></el-icon> {{ meeting.location }}</span>
                      </div>
                      <div class="meeting-content">{{ meeting.minutes }}</div>
                      <div class="meeting-footer">
                        <div class="attendees">
                          <span class="label">出席人员：</span>
                          <div class="avatar-list">
                            <el-avatar 
                              v-for="user in meeting.attendees_info" 
                              :key="user.id" 
                              :size="24" 
                              :title="user.real_name"
                              :src="user.avatar"
                              class="stacked-avatar"
                            >
                              {{ user.real_name?.[0] }}
                            </el-avatar>
                          </div>
                        </div>
                      </div>
                    </el-card>
                  </el-timeline-item>
                </el-timeline>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
        <div v-else class="empty-state">
          <el-empty description="请从左侧选择一个科研团队" :image-size="200" />
        </div>
      </el-col>
    </el-row>

    <!-- 新建团队弹窗 -->
    <el-dialog v-model="teamDialogVisible" title="新建科研团队" width="500px" destroy-on-close>
      <el-form :model="teamForm" :rules="teamRules" ref="teamFormRef" label-width="80px" label-position="top">
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="teamForm.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="团队描述" prop="description">
          <el-input v-model="teamForm.description" type="textarea" :rows="4" placeholder="请输入团队简介..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="teamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTeam" :loading="teamLoading">确定创建</el-button>
      </template>
    </el-dialog>

    <!-- 添加成员弹窗 -->
    <el-dialog v-model="memberDialogVisible" title="添加团队成员" width="400px" destroy-on-close>
      <el-form :model="memberForm" label-width="80px" label-position="top">
        <el-form-item label="选择用户" required>
          <el-select 
            v-model="memberForm.user_id" 
            filterable 
            remote 
            placeholder="搜索姓名或工号"
            :remote-method="searchUsers"
            :loading="usersLoading"
            style="width: 100%"
          >
            <el-option
              v-for="user in availableUsers"
              :key="user.id"
              :label="`${user.real_name} (${user.username})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAddMember" :loading="memberSubmitting">添加</el-button>
      </template>
    </el-dialog>

    <!-- 会议记录弹窗 -->
    <el-dialog v-model="meetingDialogVisible" title="记录团队会议" width="600px" destroy-on-close>
      <el-form :model="meetingForm" :rules="meetingRules" ref="meetingFormRef" label-width="80px" label-position="top">
        <el-form-item label="会议主题" prop="title">
          <el-input v-model="meetingForm.title" placeholder="请输入会议主题" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="会议时间" prop="meeting_time">
              <el-date-picker 
                v-model="meetingForm.meeting_time" 
                type="datetime" 
                placeholder="选择日期时间"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DDTHH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="会议地点" prop="location">
              <el-input v-model="meetingForm.location" placeholder="会议室/地点" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="出席人员" prop="attendees">
          <el-select v-model="meetingForm.attendees" multiple placeholder="选择出席成员" style="width: 100%">
            <el-option
              v-for="user in activeTeam?.members_info"
              :key="user.id"
              :label="user.real_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="会议纪要" prop="minutes">
          <el-input v-model="meetingForm.minutes" type="textarea" :rows="6" placeholder="记录会议主要内容、决议事项等..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="meetingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitMeeting" :loading="meetingSubmitting">提交记录</el-button>
      </template>
    </el-dialog>

    <!-- 任务弹窗 -->
    <el-dialog v-model="taskDialogVisible" title="发布任务" width="500px" destroy-on-close>
      <el-form :model="taskForm" label-width="80px" label-position="top">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.title" placeholder="请输入任务名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="执行人" required>
              <el-select v-model="taskForm.assignee" style="width: 100%" placeholder="选择执行人">
                <el-option v-for="user in activeTeam?.members_info" :key="user.id" :label="user.real_name" :value="user.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="截止日期">
              <el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" placeholder="选择日期" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" :rows="4" placeholder="请输入任务详细描述..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTask" :loading="taskLoading">发布任务</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { 
  User, Avatar, Checked, Calendar, 
  Location, Search, Plus, Delete
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const teams = ref([])
const activeTeamId = ref('')
const activeTab = ref('members')
const loading = ref(false)

// 弹窗可见性
const teamDialogVisible = ref(false)
const memberDialogVisible = ref(false)
const meetingDialogVisible = ref(false)
const taskDialogVisible = ref(false)

// 加载状态
const teamLoading = ref(false)
const memberSubmitting = ref(false)
const meetingSubmitting = ref(false)
const taskLoading = ref(false)
const usersLoading = ref(false)

// 表单数据
const teamForm = reactive({
  name: '',
  description: ''
})

const memberForm = reactive({
  user_id: null
})

const meetingForm = reactive({
  title: '',
  meeting_time: '',
  location: '',
  attendees: [],
  minutes: ''
})

const taskForm = reactive({
  title: '',
  assignee: null,
  due_date: '',
  description: ''
})

const availableUsers = ref([])

// 表单引用
const teamFormRef = ref(null)
const meetingFormRef = ref(null)
const taskFormRef = ref(null)

// 校验规则
const teamRules = {
  name: [{ required: true, message: '请输入团队名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入团队简介', trigger: 'blur' }]
}

const meetingRules = {
  title: [{ required: true, message: '请输入会议主题', trigger: 'blur' }],
  meeting_time: [{ required: true, message: '请选择会议时间', trigger: 'change' }],
  attendees: [{ type: 'array', required: true, message: '请选择出席人员', trigger: 'change' }]
}

const taskRules = {
  title: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  assignee: [{ required: true, message: '请选择执行人', trigger: 'change' }]
}

const activeTeam = computed(() => {
  return teams.value.find(t => t.id.toString() === activeTeamId.value)
})

const isLeader = computed(() => {
  if (!activeTeam.value) return false
  return activeTeam.value.leader === userStore.user?.id || isAdmin.value
})

const taskStatusMap = {
  todo: '待处理',
  doing: '进行中',
  completed: '已完成'
}

const fetchTeams = async () => {
  loading.value = true
  try {
    const response = await api.get('/research/teams/')
    teams.value = response.data.results || response.data
    if (teams.value.length > 0 && !activeTeamId.value) {
      activeTeamId.value = teams.value[0].id.toString()
    }
  } catch (error) {
    console.error('Fetch teams error:', error)
    ElMessage.error(error.response?.data?.detail || '获取团队列表失败')
  } finally {
    loading.value = false
  }
}

const handleTeamSelect = (id) => {
  activeTeamId.value = id
}

// 团队管理
const handleCreateTeam = () => {
  teamForm.name = ''
  teamForm.description = ''
  teamDialogVisible.value = true
}

const submitTeam = async () => {
  if (!teamFormRef.value) return
  await teamFormRef.value.validate(async (valid) => {
    if (valid) {
      teamLoading.value = true
      try {
        await api.post('/research/teams/', {
          ...teamForm,
          leader: userStore.user.id
        })
        ElMessage.success('团队创建成功')
        teamDialogVisible.value = false
        fetchTeams()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '创建失败')
      } finally {
        teamLoading.value = false
      }
    }
  })
}

const handleDeleteTeam = () => {
  ElMessageBox.confirm('确定要解散该科研团队吗？该操作不可恢复！', '警告', {
    confirmButtonText: '确定解散',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/research/teams/${activeTeamId.value}/`)
      ElMessage.success('团队已解散')
      activeTeamId.value = ''
      fetchTeams()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  })
}

// 成员管理
const handleAddMember = () => {
  memberForm.user_id = null
  availableUsers.value = []
  memberDialogVisible.value = true
}

const searchUsers = async (query) => {
  if (query) {
    usersLoading.value = true
    try {
      const response = await api.get('/users/', { params: { search: query } })
      availableUsers.value = (response.data.results || response.data).filter(
        u => !activeTeam.value.members.includes(u.id)
      )
    } catch (error) {
      console.error(error)
    } finally {
      usersLoading.value = false
    }
  } else {
    availableUsers.value = []
  }
}

const submitAddMember = async () => {
  if (!memberForm.user_id) return ElMessage.warning('请选择要添加的用户')
  memberSubmitting.value = true
  try {
    await api.post(`/research/teams/${activeTeamId.value}/add_member/`, {
      user_id: memberForm.user_id
    })
    ElMessage.success('成员添加成功')
    memberDialogVisible.value = false
    fetchTeams()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '添加失败')
  } finally {
    memberSubmitting.value = false
  }
}

const handleRemoveMember = (member) => {
  ElMessageBox.confirm(`确定要将 ${member.real_name} 移出团队吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await api.post(`/research/teams/${activeTeamId.value}/remove_member/`, {
        user_id: member.id
      })
      ElMessage.success('成员已移除')
      fetchTeams()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  })
}

// 会议管理
const handleAddMeeting = () => {
  Object.assign(meetingForm, {
    title: '',
    meeting_time: '',
    location: '',
    attendees: [],
    minutes: ''
  })
  meetingDialogVisible.value = true
}

const submitMeeting = async () => {
  if (!meetingFormRef.value) return
  await meetingFormRef.value.validate(async (valid) => {
    if (valid) {
      meetingSubmitting.value = true
      try {
        await api.post('/research/meetings/', {
          ...meetingForm,
          team: activeTeamId.value,
          created_by: userStore.user.id
        })
        ElMessage.success('会议记录已保存')
        meetingDialogVisible.value = false
        fetchTeams()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '保存失败')
      } finally {
        meetingSubmitting.value = false
      }
    }
  })
}

// 任务管理
const handleAddTask = () => {
  Object.assign(taskForm, {
    title: '',
    assignee: null,
    due_date: '',
    description: ''
  })
  taskDialogVisible.value = true
}

const submitTask = async () => {
  if (!taskFormRef.value) return
  await taskFormRef.value.validate(async (valid) => {
    if (valid) {
      taskLoading.value = true
      try {
        await api.post('/research/tasks/', {
          ...taskForm,
          team: activeTeamId.value
        })
        ElMessage.success('任务发布成功')
        taskDialogVisible.value = false
        fetchTeams()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '发布失败')
      } finally {
        taskLoading.value = false
      }
    }
  })
}

const handleTaskDetail = (task) => {
  ElMessageBox.alert(task.description || '暂无描述', task.title)
}

const handleCompleteTask = async (task) => {
  try {
    await api.patch(`/research/tasks/${task.id}/`, { status: 'completed' })
    ElMessage.success('任务已完成')
    fetchTeams()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const getTaskStatusTag = (status) => {
  const map = {
    todo: 'info',
    pending: 'info',
    doing: 'primary',
    in_progress: 'primary',
    completed: 'success'
  }
  return map[status] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchTeams()
})
</script>

<style scoped>
.research-team {
  padding: 0;
}
.team-sidebar {
  height: calc(100vh - 110px);
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header .title {
  font-weight: bold;
  font-size: 16px;
}
.team-menu {
  border-right: none;
}
.team-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.team-title-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}
.team-title-row h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.description {
  color: #909399;
  margin: 0;
  font-size: 14px;
}
.tab-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}
.custom-tabs {
  margin-top: 10px;
}
.tab-label {
  display: flex;
  align-items: center;
  gap: 5px;
}
.member-cell, .assignee-cell {
  display: flex;
  align-items: center;
}
.timeline-container {
  padding: 10px 0;
}
.meeting-card {
  border-radius: 8px;
}
.meeting-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.meeting-header-row h4 {
  margin: 0;
  color: #303133;
}
.meeting-header-row .location {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 3px;
}
.meeting-content {
  margin: 10px 0;
  color: #606266;
  white-space: pre-wrap;
  line-height: 1.6;
}
.meeting-footer {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px dashed #ebeef5;
}
.attendees {
  display: flex;
  align-items: center;
  gap: 10px;
}
.attendees .label {
  font-size: 12px;
  color: #909399;
}
.avatar-list {
  display: flex;
  padding-left: 10px;
}
.stacked-avatar {
  border: 2px solid #fff;
  margin-left: -10px;
  transition: all 0.3s;
  cursor: pointer;
}
.stacked-avatar:hover {
  transform: translateY(-2px);
  z-index: 10;
}
.empty-state {
  height: calc(100vh - 110px);
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  border-radius: 4px;
}
</style>
