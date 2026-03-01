<template>
  <div class="party-member-list">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>党团成员管理</span>
          <el-button type="primary" @click="handleSync" v-if="isAdmin">同步人员数据</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-form :inline="true" :model="searchQuery" size="default">
          <el-form-item label="政治面貌">
            <el-select v-model="searchQuery.member_type" placeholder="全部" clearable style="width: 150px">
              <el-option label="团员" value="member" />
              <el-option label="入党积极分子" value="activist" />
              <el-option label="预备党员" value="probationary" />
              <el-option label="正式党员" value="party_member" />
            </el-select>
          </el-form-item>
          <el-form-item label="所属支部">
            <el-select v-model="searchQuery.branch" placeholder="全部" clearable style="width: 200px">
              <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchMembers">查询</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 列表 -->
      <el-table :data="members" v-loading="loading" style="width: 100%">
        <el-table-column prop="user_info.real_name" label="姓名" width="120" />
        <el-table-column prop="user_info.username" label="学号/工号" width="150" />
        <el-table-column prop="member_type" label="政治面貌" width="140">
          <template #default="{ row }">
            <el-tag :type="getMemberTypeTag(row.member_type)">{{ memberTypeMap[row.member_type] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="branch_info.name" label="所属支部" width="200" />
        <el-table-column prop="volunteer_hours" label="志愿时长" width="120">
          <template #default="{ row }">
            <el-statistic :value="row.volunteer_hours" :precision="1" suffix="h" />
          </template>
        </el-table-column>
        <el-table-column prop="join_date" label="加入日期" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)" v-if="isAdmin">编辑状态</el-button>
            <el-button link type="success" @click="handleDetail(row)">档案</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑状态对话框 -->
    <el-dialog v-model="editVisible" title="更新政治面貌" width="450px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="当前成员">
          <el-tag>{{ currentMember.user_info?.real_name }}</el-tag>
        </el-form-item>
        <el-form-item label="政治面貌">
          <el-select v-model="editForm.member_type" style="width: 100%">
            <el-option label="团员" value="member" />
            <el-option label="入党积极分子" value="activist" />
            <el-option label="预备党员" value="probationary" />
            <el-option label="正式党员" value="party_member" />
          </el-select>
        </el-form-item>
        <el-form-item label="变动日期">
          <el-date-picker v-model="editForm.change_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="所属支部">
          <el-select v-model="editForm.branch" style="width: 100%">
            <el-option v-for="b in branches" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.role === 'teacher')

const loading = ref(false)
const members = ref([])
const branches = ref([])
const editVisible = ref(false)
const currentMember = ref({})

const memberTypeMap = {
  member: '团员',
  activist: '入党积极分子',
  probationary: '预备党员',
  party_member: '正式党员'
}

const searchQuery = reactive({
  member_type: '',
  branch: ''
})

const editForm = reactive({
  member_type: '',
  branch: '',
  change_date: ''
})

const fetchMembers = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/party/members/', { params: searchQuery })
    members.value = response.data
  } catch (error) {
    ElMessage.error('获取成员列表失败')
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

const handleEdit = (row) => {
  currentMember.value = row
  editForm.member_type = row.member_type
  editForm.branch = row.branch
  editForm.change_date = new Date().toISOString().split('T')[0]
  editVisible.value = true
}

const submitEdit = async () => {
  try {
    await axios.patch(`/api/party/members/${currentMember.value.id}/`, editForm)
    ElMessage.success('更新成功')
    editVisible.value = false
    fetchMembers()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const handleSync = async () => {
  try {
    await axios.post('/api/party/members/sync/')
    ElMessage.success('同步成功')
    fetchMembers()
  } catch (error) {
    ElMessage.error('同步失败')
  }
}

const getMemberTypeTag = (type) => {
  const map = {
    member: 'info',
    activist: 'warning',
    probationary: 'primary',
    party_member: 'danger'
  }
  return map[type] || 'info'
}

onMounted(() => {
  fetchMembers()
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
</style>
