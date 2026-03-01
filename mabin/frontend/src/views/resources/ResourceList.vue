<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>资源管理</span>
        <el-button type="primary" @click="handleAdd">新增资源</el-button>
      </div>
    </template>
    
    <el-table :data="resources" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="资源名称" />
      <el-table-column prop="resource_type_display" label="类型" width="120" />
      <el-table-column prop="category_name" label="分类" width="100" />
      <el-table-column prop="department_name" label="归属部门" width="120" />
      <el-table-column prop="location" label="位置" />
      <el-table-column prop="capacity" label="容纳人数" width="100" />
      <el-table-column prop="require_approval" label="需要审批" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.require_approval ? 'warning' : 'success'">
            {{ scope.row.require_approval ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleBook(scope.row)">预约</el-button>
          <el-button type="success" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 预约对话框 -->
    <el-dialog v-model="bookingVisible" title="资源预约" width="600px">
      <el-form :model="bookingForm" label-width="100px">
        <el-form-item label="资源名称">
          <el-input v-model="currentResource.name" disabled />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="bookingForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker
            v-model="bookingForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预约标题" required>
          <el-input v-model="bookingForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="bookingForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitBooking">提交</el-button>
      </template>
    </el-dialog>
    
    <!-- 新增/编辑资源对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑资源' : '新增资源'" width="600px" destroy-on-close @close="resetForm">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="资源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入资源名称" />
        </el-form-item>
        <el-form-item label="资源类型" prop="resource_type">
          <el-select v-model="form.resource_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="会议室" value="meeting_room" />
            <el-option label="学术报告厅" value="lecture_hall" />
            <el-option label="实验室" value="laboratory" />
            <el-option label="教室" value="classroom" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" clearable style="width: 100%">
            <el-option
              v-for="cat in resourceCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="归属部门" prop="department">
          <el-select v-model="form.department" placeholder="请选择部门" clearable style="width: 100%">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入位置，如：教学楼A101" />
        </el-form-item>
        <el-form-item label="容纳人数" prop="capacity">
          <el-input-number v-model="form.capacity" :min="0" :max="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="需要审批">
          <el-switch v-model="form.require_approval" />
        </el-form-item>
        <el-form-item label="审批人" v-if="form.require_approval">
          <el-select v-model="form.approver" placeholder="请选择审批人" clearable style="width: 100%">
            <el-option
              v-for="user in approvers"
              :key="user.id"
              :label="user.real_name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入资源描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">{{ isEdit ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const resources = ref([])
const resourceCategories = ref([])
const departments = ref([])
const approvers = ref([])
const bookingVisible = ref(false)
const formVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentResource = ref({})

const form = reactive({
  id: null,
  name: '',
  resource_type: 'meeting_room',
  category: null,
  department: null,
  location: '',
  capacity: 0,
  description: '',
  require_approval: true,
  approver: null,
  is_active: true
})

const bookingForm = reactive({
  resource: null,
  title: '',
  description: '',
  start_time: null,
  end_time: null
})

const fetchResources = async () => {
  loading.value = true
  try {
    const response = await api.get('/resources/')
    resources.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取资源列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  formVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.resource_type = row.resource_type
  form.category = row.category
  form.department = row.department || null
  form.location = row.location
  form.capacity = row.capacity
  form.description = row.description || ''
  form.require_approval = row.require_approval
  form.approver = row.approver || null
  form.is_active = row.is_active
  formVisible.value = true
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.resource_type = 'meeting_room'
  form.category = null
  form.department = null
  form.location = ''
  form.capacity = 0
  form.description = ''
  form.require_approval = true
  form.approver = null
  form.is_active = true
}

const formRules = {
  name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  resource_type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入位置', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容纳人数', trigger: 'blur' }]
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (isEdit.value && form.id) {
        await api.put(`/resources/${form.id}/`, form)
        ElMessage.success('更新成功')
      } else {
        await api.post('/resources/', form)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      fetchResources()
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '保存失败')
      console.error(error)
    }
  })
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/resources/categories/')
    resourceCategories.value = response.data.results || response.data
  } catch (error) {
    console.error('获取分类失败', error)
  }
}

const fetchDepartments = async () => {
  try {
    const response = await api.get('/rbac/departments/')
    departments.value = response.data.results || response.data
  } catch (error) {
    console.error('获取部门失败', error)
  }
}

const fetchApprovers = async () => {
  try {
    const response = await api.get('/users/teachers/')
    approvers.value = response.data.results || response.data
  } catch (error) {
    console.error('获取审批人失败', error)
  }
}

const handleBook = (row) => {
  currentResource.value = row
  bookingForm.resource = row.id
  bookingForm.title = ''
  bookingForm.description = ''
  bookingForm.start_time = null
  bookingForm.end_time = null
  bookingVisible.value = true
}

const handleSubmitBooking = async () => {
  if (!bookingForm.start_time || !bookingForm.end_time) {
    ElMessage.warning('请选择预约时间')
    return
  }
  
  if (!bookingForm.title) {
    ElMessage.warning('请输入预约标题')
    return
  }
  
  try {
    const data = {
      ...bookingForm,
      start_time: dayjs(bookingForm.start_time).format('YYYY-MM-DD HH:mm:ss'),
      end_time: dayjs(bookingForm.end_time).format('YYYY-MM-DD HH:mm:ss')
    }
    
    await api.post('/resources/bookings/', data)
    ElMessage.success('预约提交成功，等待审批')
    bookingVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '预约失败')
    console.error(error)
  }
}

onMounted(() => {
  fetchResources()
  fetchCategories()
  fetchDepartments()
  fetchApprovers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
