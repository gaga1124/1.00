<template>
  <el-card class="teacher-card">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <span class="card-title-main">教师管理</span>
          <span class="card-title-sub">管理教师账号及基本信息</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon class="btn-icon"><Plus /></el-icon>
            <span>新增教师</span>
          </el-button>
          <el-button type="success" @click="handleBulkAdd">
            <el-icon class="btn-icon"><Upload /></el-icon>
            <span>批量新增</span>
          </el-button>
        </div>
      </div>
    </template>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters" label-width="60px" size="small">
        <el-form-item label="姓名">
          <el-input v-model="filters.real_name" placeholder="请输入姓名" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="工号">
          <el-input v-model="filters.profile__employee_id" placeholder="请输入工号" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table :data="teachers" v-loading="loading" style="width: 100%" size="small" border>
      <el-table-column prop="employee_id" label="工号" width="120">
         <template #default="{ row }">
           {{ row.profile?.employee_id || row.employee_id }}
         </template>
      </el-table-column>
      <el-table-column prop="real_name" label="姓名" width="100" />
      <el-table-column prop="job_title" label="职务" width="120">
         <template #default="{ row }">
           {{ row.profile?.job_title || row.job_title }}
         </template>
      </el-table-column>
      <el-table-column prop="department_name" label="部门" width="150" />
      <el-table-column prop="phone" label="手机号" width="120" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button type="primary" link size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" link size="small" @click="handleDelete(scope.row)">删除</el-button>
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

    <!-- 新增/编辑教师对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑教师' : '新增教师'" width="500px" destroy-on-close @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" status-icon>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="工号" prop="employee_id">
          <el-input v-model="form.employee_id" placeholder="工号将作为默认登录账号" />
        </el-form-item>
        <el-form-item label="职务" prop="job_title">
          <el-input v-model="form.job_title" placeholder="如：讲师、教授" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
           <el-tree-select
              v-model="form.department"
              :data="departments"
              :props="{ label: 'name', value: 'id', children: 'children' }"
              placeholder="请选择部门"
              check-strictly
              style="width: 100%"
           />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
           <el-input v-model="form.password" type="password" placeholder="默认同工号或123456" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="submitForm">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量新增教师对话框 -->
    <el-dialog v-model="bulkVisible" title="批量新增教师" width="700px" destroy-on-close>
      <div class="bulk-tip">
        <p>请选择部门，并上传xlsx表格文件或按格式输入教师数据：</p>
        <p class="format-tip">xlsx表格表头应为：工号,姓名,职务,手机号,邮箱,身份证号</p>
        <p class="example-tip">或文本格式：工号,姓名,职务,手机号,邮箱,身份证号（每行一条记录）</p>
      </div>
      <el-form :model="bulkForm" ref="bulkFormRef" label-width="80px">
        <el-form-item label="部门">
           <el-tree-select
              v-model="bulkForm.department"
              :data="departments"
              :props="{ label: 'name', value: 'id', children: 'children' }"
              placeholder="请选择部门（可选）"
              check-strictly
              style="width: 100%"
           />
        </el-form-item>
        <el-form-item label="上传xlsx">
          <div class="upload-container">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              :on-change="handleFileChange"
              :on-exceed="handleExceed"
              :file-list="fileList"
              accept=".xlsx,.xls"
              drag
              action="#"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处 或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持xlsx格式，表头：工号,姓名,职务,手机号,邮箱,身份证号,部门
                </div>
              </template>
            </el-upload>
            <el-button type="primary" link @click="downloadTemplate" class="download-template-btn">
              <el-icon><Download /></el-icon>
              下载模版
            </el-button>
          </div>
        </el-form-item>
        <el-divider>或手动输入</el-divider>
        <el-form-item label="教师数据">
          <el-input
            v-model="bulkForm.teachers_data"
            type="textarea"
            :rows="8"
            placeholder="请按格式输入教师数据，每行一条
格式：工号,姓名,职务,手机号,邮箱,身份证号
示例：
T001,张三,讲师,13800138000,zhangsan@school.edu,110101199001011234
T002,李四,教授,13900139000,lisi@school.edu,110101199002021234"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bulkVisible = false">取消</el-button>
        <el-button type="primary" :loading="bulkLoading" @click="submitBulkForm">
          批量创建
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, UploadFilled, Download } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import api from '@/utils/api'

const loading = ref(false)
const teachers = ref([])
const departments = ref([])

const filters = reactive({
  real_name: '',
  profile__employee_id: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const fetchTeachers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '') delete params[key]
    })
    const response = await api.get('/users/teachers/', { params })
    const data = response?.data
    if (data && Array.isArray(data.results)) {
      teachers.value = data.results
      pagination.total = data.count || 0
    } else if (Array.isArray(data)) {
      teachers.value = data
      pagination.total = data.length
    } else {
      teachers.value = []
      pagination.total = 0
    }
  } catch (error) {
    ElMessage.error('获取教师列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await api.get('/rbac/departments/')
    const data = response?.data
    if (data && Array.isArray(data.results)) {
      departments.value = data.results
    } else if (Array.isArray(data)) {
      departments.value = data
    } else {
      departments.value = []
    }
  } catch (error) {
    console.error('获取部门失败', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchTeachers()
}

const handleReset = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = ''
  })
  handleSearch()
}

const formVisible = ref(false)
const isEdit = ref(false)
const formLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  real_name: '',
  employee_id: '',
  job_title: '',
  department: null,
  id_card: '',
  phone: '',
  email: '',
  password: ''
})

const rules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  employee_id: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }]
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  form.id = null
  form.real_name = ''
  form.employee_id = ''
  form.job_title = ''
  form.department = null
  form.id_card = ''
  form.phone = ''
  form.email = ''
  form.password = ''
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  formVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  formVisible.value = true
  form.id = row.id
  form.real_name = row.real_name
  form.employee_id = row.profile?.employee_id || ''
  form.job_title = row.profile?.job_title || ''
  form.department = row.department
  form.id_card = row.id_card
  form.phone = row.phone
  form.email = row.email
  form.password = ''
}

const submitForm = () => {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    formLoading.value = true
    try {
      const payload = { ...form }
      if (!payload.password || payload.password === '') {
        delete payload.password
      }
      if (!payload.department) {
        delete payload.department
      }
      
      if (isEdit.value && form.id) {
        await api.put(`/users/teachers/${form.id}/`, payload)
        ElMessage.success('更新成功')
      } else {
        await api.post('/users/teachers/', payload)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      fetchTeachers()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || (isEdit.value ? '更新失败' : '创建失败'))
      console.error(error)
    } finally {
      formLoading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该教师吗？这将同时删除其账号。', '提示', {
      type: 'warning'
    })
    await api.delete(`/users/teachers/${row.id}/`)
    ElMessage.success('删除成功')
    fetchTeachers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const bulkVisible = ref(false)
const bulkLoading = ref(false)
const bulkFormRef = ref(null)
const uploadRef = ref(null)
const fileList = ref([])
const parsedTeachersFromXlsx = ref([])

const bulkForm = reactive({
  department: null,
  teachers_data: ''
})

const handleBulkAdd = () => {
  bulkForm.department = null
  bulkForm.teachers_data = ''
  fileList.value = []
  parsedTeachersFromXlsx.value = []
  bulkVisible.value = true
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const firstSheet = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheet]
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
      
      if (jsonData.length < 2) {
        ElMessage.warning('xlsx文件内容为空或只有表头')
        return
      }
      
      const teachers = []
      const header = jsonData[0].map(h => h?.toString().trim() || '')
      
      const idxMap = {
        employee_id: header.findIndex(h => h.includes('工号')),
        real_name: header.findIndex(h => h.includes('姓名')),
        job_title: header.findIndex(h => h.includes('职务')),
        phone: header.findIndex(h => h.includes('手机') || h.includes('电话')),
        email: header.findIndex(h => h.includes('邮箱') || h.includes('邮件')),
        id_card: header.findIndex(h => h.includes('身份证')),
        department: header.findIndex(h => h.includes('部门'))
      }
      
      const hasDepartmentInXlsx = idxMap.department >= 0
      
      for (let i = 1; i < jsonData.length; i++) {
        const row = jsonData[i]
        if (!row || row.length === 0) continue
        
        const employee_id = row[idxMap.employee_id]?.toString().trim()
        const real_name = row[idxMap.real_name]?.toString().trim()
        
        if (!employee_id || !real_name) {
          continue
        }
        
        let deptValue = null
        if (hasDepartmentInXlsx && row[idxMap.department]) {
          deptValue = row[idxMap.department]?.toString().trim()
        }
        
        teachers.push({
          employee_id: employee_id,
          real_name: real_name,
          job_title: idxMap.job_title >= 0 ? (row[idxMap.job_title]?.toString().trim() || '') : '',
          phone: idxMap.phone >= 0 ? (row[idxMap.phone]?.toString().trim() || '') : '',
          email: idxMap.email >= 0 ? (row[idxMap.email]?.toString().trim() || '') : '',
          id_card: idxMap.id_card >= 0 ? (row[idxMap.id_card]?.toString().trim() || '') : '',
          department_name: deptValue
        })
      }
      
      parsedTeachersFromXlsx.value = teachers
      ElMessage.success(`成功解析 ${teachers.length} 条教师数据`)
    } catch (error) {
      console.error('解析xlsx文件失败:', error)
      ElMessage.error('解析xlsx文件失败，请检查文件格式')
    }
  }
  reader.readAsArrayBuffer(file.raw)
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个xlsx文件')
}

const downloadTemplate = () => {
  const headers = ['工号', '姓名', '职务', '手机号', '邮箱', '身份证号', '部门']
  const sampleData = [
    ['T001', '张三', '讲师', '13800138000', 'zhangsan@school.edu', '110101199001011234', '计算机学院'],
    ['T002', '李四', '教授', '13900139000', 'lisi@school.edu', '110101199002021234', '数学学院']
  ]
  
  const ws = XLSX.utils.aoa_to_sheet([headers, ...sampleData])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '教师信息')
  
  XLSX.writeFile(wb, '教师信息模版.xlsx')
  ElMessage.success('模版下载成功')
}

const submitBulkForm = async () => {
  if (!bulkForm.teachers_data.trim() && parsedTeachersFromXlsx.value.length === 0) {
    ElMessage.warning('请上传xlsx文件或输入教师数据')
    return
  }
  
  let teachersList = []
  
  if (parsedTeachersFromXlsx.value.length > 0) {
    teachersList = parsedTeachersFromXlsx.value.map(t => {
      const item = {
        employee_id: t.employee_id,
        real_name: t.real_name,
        job_title: t.job_title,
        phone: t.phone,
        email: t.email,
        id_card: t.id_card
      }
      if (bulkForm.department) {
        item.department = bulkForm.department
      }
      return item
    })
  } else if (bulkForm.teachers_data.trim()) {
    try {
      const lines = bulkForm.teachers_data.trim().split('\n')
      for (const line of lines) {
        const parts = line.split(',').map(s => s.trim())
        if (parts.length < 2) {
          throw new Error(`数据格式错误: ${line}，格式应为: 工号,姓名,职务,手机号,邮箱,身份证号`)
        }
        teachersList.push({
          employee_id: parts[0],
          real_name: parts[1],
          job_title: parts[2] || '',
          phone: parts[3] || '',
          email: parts[4] || '',
          id_card: parts[5] || '',
          department: bulkForm.department
        })
      }
    } catch (e) {
      ElMessage.error(e.message)
      return
    }
  }
  
  if (teachersList.length === 0) {
    ElMessage.warning('未解析到有效的教师数据')
    return
  }
  
  bulkLoading.value = true
  try {
    const response = await api.post('/users/teachers/bulk_create/', { teachers: teachersList })
    console.log('批量创建响应:', response.data)
    const result = response.data
    const successCount = result.success_count ?? result.created?.length ?? 0
    const errorCount = result.error_count ?? result.errors?.length ?? 0
    let msg = `成功创建 ${successCount} 位教师`
    if (errorCount > 0) {
      msg += `，失败 ${errorCount} 位`
      if (result.errors && result.errors.length > 0) {
        console.error('创建失败详情:', result.errors)
      }
    }
    ElMessage.success(msg)
    bulkVisible.value = false
    fetchTeachers()
  } catch (error) {
    console.error('批量创建错误:', error)
    const errMsg = error.response?.data?.error || error.response?.data?.detail || JSON.stringify(error.response?.data) || '批量创建失败'
    ElMessage.error(errMsg)
  } finally {
    bulkLoading.value = false
  }
}

const handleSizeChange = () => {
  fetchTeachers()
}

const handlePageChange = () => {
  fetchTeachers()
}

onMounted(() => {
  fetchTeachers()
  fetchDepartments()
})
</script>

<style scoped>
.teacher-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  flex-direction: column;
}

.card-title-main {
  font-size: 16px;
  font-weight: 600;
}

.card-title-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-icon {
  margin-right: 4px;
}

.filter-bar {
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.filter-actions {
  margin-left: 12px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.bulk-tip {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.bulk-tip p {
  margin: 4px 0;
  font-size: 14px;
}

.format-tip {
  color: #e6a23c;
}

.example-tip {
  margin-top: 8px !important;
  color: #909399;
}

.example {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  margin: 8px 0 0 0;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.download-template-btn {
  align-self: flex-start;
}
</style>
