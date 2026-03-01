<template>
  <div class="rbac-user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户与权限管理</span>
          <div class="tools">
            <el-button type="primary" @click="handleCreate">新增用户</el-button>
            <el-button type="warning" :disabled="selectedIds.length === 0" @click="openBulkDialog">批量修改角色</el-button>
          </div>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-form :inline="true" :model="filters" label-width="0" size="default">
          <el-form-item>
            <el-input v-model="search" placeholder="搜索用户名/姓名/手机号" clearable style="width: 260px" @keyup.enter="handleSearch" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table :data="users" v-loading="loading" @selection-change="handleSelectionChange" style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="real_name" label="姓名" min-width="120" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="department_name" label="部门" min-width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.role }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="role_type" label="角色类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.role_type === 'admin'" type="danger">管理员</el-tag>
            <el-tag v-else-if="row.role_type === 'student'" type="success">学生</el-tag>
            <el-tag v-else-if="row.role_type === 'teacher'" type="warning">教师</el-tag>
            <el-tag v-else-if="row.role_type === 'staff'" type="info">职工</el-tag>
            <el-tag v-else type="info">{{ row.role_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="positions" label="职务" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="pos in (row.positions || []).slice(0, 2)" :key="pos.id" size="small" class="mr-1">
              {{ pos.department_name }}-{{ pos.position_name }}
            </el-tag>
            <span v-if="(row.positions || []).length > 2" class="more-text">+{{ row.positions.length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleSetPosition(row)">设置职务</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="bulkVisible" title="批量修改角色" width="500px">
      <el-form :model="bulkForm" label-width="100px">
        <el-form-item label="角色">
          <el-select v-model="bulkForm.roleCode" placeholder="请选择角色" filterable style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r.code" :label="r.name" :value="r.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作方式">
          <el-radio-group v-model="bulkForm.mode">
            <el-radio label="add">添加到角色</el-radio>
            <el-radio label="remove">从角色移除</el-radio>
            <el-radio label="set">设为唯一角色</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="已选用户">
          <div class="selected-count">共 {{ selectedIds.length }} 人</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bulkVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleBulkSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增用户对话框 -->
    <el-dialog v-model="createVisible" title="新增用户" width="550px" destroy-on-close>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="createForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="工号/学号" prop="employee_id">
          <el-input v-model="createForm.employee_id" placeholder="将作为默认登录账号和初始密码" />
        </el-form-item>
        <el-form-item label="用户角色" prop="role_code">
          <el-select v-model="createForm.role_code" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
            <el-option label="职工" value="staff" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-tree-select
            v-model="createForm.department"
            :data="departmentOptions"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择部门"
            check-strictly
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="可选，默认同工号/学号" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="createForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createForm.email" placeholder="请输入邮箱" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="positionVisible" title="设置职务" width="600px" destroy-on-close>
      <div class="position-user-info">
        <el-text>当前用户：<strong>{{ currentUser?.real_name }}</strong></el-text>
      </div>
      <el-divider />
      <div class="position-list">
        <div class="position-header">
          <span>职务列表</span>
          <el-button type="primary" size="small" @click="addPosition">添加职务</el-button>
        </div>
        <el-table :data="positionList" border style="width: 100%; margin-top: 12px">
          <el-table-column label="所属部门" min-width="150">
            <template #default="{ row, $index }">
              <el-select v-model="row.department" placeholder="请选择部门" size="small" style="width: 100%">
                <el-option v-for="dept in departmentOptions" :key="dept.id" :label="dept.name" :value="dept.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="职务" width="140">
            <template #default="{ row, $index }">
              <el-select v-model="row.position_code" placeholder="请选择职务" size="small" style="width: 100%">
                <el-option v-for="pos in positionOptions" :key="pos.value" :label="pos.label" :value="pos.value" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="主职务" width="80">
            <template #default="{ row, $index }">
              <el-radio v-model="mainPositionIndex" :label="$index">是</el-radio>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60">
            <template #default="{ $index }">
              <el-button type="danger" link size="small" @click="removePosition($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="positionVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingPosition" @click="savePosition">确定</el-button>
      </template>
    </el-dialog>
  </div>
  </template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const users = ref([])
const loading = ref(false)
const search = ref('')
const selectedIds = ref([])
const filters = reactive({})
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const bulkVisible = ref(false)
const submitting = ref(false)
const bulkForm = reactive({
  roleCode: '',
  mode: 'add'
})
const roleOptions = ref([])

// 新增用户相关
const createVisible = ref(false)
const creating = ref(false)
const createFormRef = ref(null)
const departmentOptions = ref([])
const createForm = reactive({
  real_name: '',
  employee_id: '',
  role_code: 'student',
  department: null,
  username: '',
  phone: '',
  email: ''
})

const createRules = {
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  employee_id: [{ required: true, message: '请输入工号/学号', trigger: 'blur' }],
  role_code: [{ required: true, message: '请选择用户角色', trigger: 'change' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }]
}

const positionOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'student', label: '学生' },
  { value: 'teacher', label: '教师' },
  { value: 'secretary', label: '教学秘书' },
  { value: 'dean', label: '院长/系主任' },
  { value: 'secretary_party', label: '书记' },
  { value: 'clerk', label: '干事/科员' },
  { value: 'section_chief', label: '科长' },
  { value: 'deputy_director', label: '副处长' },
  { value: 'director', label: '处长' },
  { value: 'deputy_bureau', label: '副厅长' },
  { value: 'bureau_chief', label: '厅长' }
]

const positionVisible = ref(false)
const savingPosition = ref(false)
const currentUser = ref(null)
const positionList = ref([])
const mainPositionIndex = ref(0)

const handleSetPosition = async (row) => {
  currentUser.value = row
  positionVisible.value = true
  mainPositionIndex.value = 0
  
  try {
    const res = await api.get('/rbac/user-positions/', { params: { user: row.id } })
    const positions = res.data?.results || res.data || []
    positionList.value = positions.map(p => ({
      id: p.id,
      department: p.department,
      position_code: p.position_code
    }))
    const mainIdx = positions.findIndex(p => p.is_main)
    if (mainIdx >= 0) mainPositionIndex.value = mainIdx
    if (positionList.value.length === 0) {
      positionList.value = [{ department: null, position_code: '' }]
    }
  } catch (e) {
    positionList.value = [{ department: null, position_code: '' }]
  }
}

const addPosition = () => {
  positionList.value.push({ department: null, position_code: '' })
}

const removePosition = (index) => {
  if (positionList.value.length > 1) {
    positionList.value.splice(index, 1)
    if (mainPositionIndex.value >= positionList.value.length) {
      mainPositionIndex.value = positionList.value.length - 1
    }
  }
}

const savePosition = async () => {
  if (!positionList.value.length) return
  
  const valid = positionList.value.every(p => p.department && p.position_code)
  if (!valid) {
    ElMessage.warning('请完善所有职务信息')
    return
  }
  
  savingPosition.value = true
  try {
    await api.delete(`/rbac/user-positions/clear_by_user/`, { 
      data: { user: currentUser.value.id }
    })
    
    for (let i = 0; i < positionList.value.length; i++) {
      const p = positionList.value[i]
      await api.post('/rbac/user-positions/', {
        user: currentUser.value.id,
        department: p.department,
        position_code: p.position_code,
        is_main: i === mainPositionIndex.value
      })
    }
    
    ElMessage.success('职务设置成功')
    positionVisible.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    savingPosition.value = false
  }
}

const formatDate = (str) => {
  if (!str) return ''
  const d = new Date(str)
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (search.value) params.search = search.value
    const res = await api.get('/users/', { params })
    users.value = res.data?.results || res.data || []
    pagination.total = res.data?.count || res.data?.length || 0
  } catch (e) {
    ElMessage.error('获取用户失败')
  } finally {
    loading.value = false
  }
}

const fetchRoles = async () => {
  try {
    const res = await api.get('/rbac/roles/', { params: { is_active: true } })
    roleOptions.value = res.data?.results || res.data || []
  } catch {
    roleOptions.value = []
  }
}

const handleSelectionChange = (rows) => {
  selectedIds.value = rows.map(r => r.id)
}

const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

const handleSizeChange = () => {
  fetchUsers()
}

const handlePageChange = () => {
  fetchUsers()
}

const handleCreate = async () => {
  createVisible.value = true
  try {
    const res = await api.get('/rbac/departments/')
    departmentOptions.value = res.data?.results || res.data || []
  } catch (e) {
    ElMessage.error('获取部门列表失败')
  }
}

const handleCreateSubmit = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        await api.post('/users/', createForm)
        ElMessage.success('用户创建成功')
        createVisible.value = false
        fetchUsers()
        // 重置表单
        Object.assign(createForm, {
          real_name: '',
          employee_id: '',
          role_code: 'student',
          department: null,
          username: '',
          phone: '',
          email: ''
        })
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || e.response?.data?.employee_id?.[0] || '创建失败')
      } finally {
        creating.value = false
      }
    }
  })
}

const openBulkDialog = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择用户')
    return
  }
  await fetchRoles()
  bulkForm.roleCode = ''
  bulkForm.mode = 'add'
  bulkVisible.value = true
}

const handleBulkSubmit = async () => {
  if (!bulkForm.roleCode) {
    ElMessage.warning('请选择角色')
    return
  }
  submitting.value = true
  try {
    const payload = {
      user_ids: selectedIds.value,
      role_code: bulkForm.roleCode,
      mode: bulkForm.mode
    }
    const res = await api.post('/rbac/user-roles/bulk_modify/', payload)
    ElMessage.success('操作成功')
    bulkVisible.value = false
    fetchUsers()
    const currentId = userStore.user?.id
    if (currentId && selectedIds.value.includes(currentId)) {
      await userStore.fetchUserInfo()
    }
  } catch (e) {
    const msg = e.response?.data?.error || '操作失败'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.rbac-user-list {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tools {
  display: flex;
  gap: 12px;
}
.filter-bar {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.selected-count {
  color: #606266;
}
.mr-1 {
  margin-right: 4px;
}
.more-text {
  color: #909399;
  font-size: 12px;
}
.position-user-info {
  padding: 8px 0;
}
.position-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
