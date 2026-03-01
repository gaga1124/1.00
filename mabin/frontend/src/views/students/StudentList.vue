<template>
  <el-card class="student-card">
    <template #header>
      <div class="card-header">
        <div class="card-title">
          <span class="card-title-main">学生管理</span>
          <span class="card-title-sub">支持筛选、批量导入和脱敏导出</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="handleAdd">
            <el-icon class="btn-icon"><Plus /></el-icon>
            <span>新增学生</span>
          </el-button>
          <el-button type="warning" @click="importDialogVisible = true">
            <el-icon class="btn-icon"><Upload /></el-icon>
            <span>Excel导入</span>
          </el-button>
          <div class="export-actions">
            <el-switch
              v-model="isExportMasked"
              active-text="开启脱敏"
              inactive-text="关闭脱敏"
            />
            <el-button
              type="info"
              plain
              @click="handleExportTemplate"
              :loading="exportTemplateLoading"
            >
              <el-icon class="btn-icon"><Download /></el-icon>
              <span>导出模板</span>
            </el-button>
            <el-tooltip content="导出当前筛选条件下的学生名单" placement="bottom">
              <el-button type="success" @click="handleExport" :loading="exportLoading">
                <el-icon class="btn-icon"><Download /></el-icon>
                <span>导出名单</span>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>
    </template>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filters" label-width="60px" size="small">
        <el-form-item label="姓名">
          <el-input v-model="filters.real_name" placeholder="请输入姓名" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="学院">
          <el-select v-model="filters.department" placeholder="请选择学院" clearable style="width: 180px">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专业">
          <el-input v-model="filters.major" placeholder="请输入专业" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="filters.gender" placeholder="请选择" clearable style="width: 100px">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="filters.grade" placeholder="请选择" clearable style="width: 120px">
            <el-option label="2021级" value="2021" />
            <el-option label="2022级" value="2022" />
            <el-option label="2023级" value="2023" />
            <el-option label="2024级" value="2024" />
            <el-option label="2025级" value="2025" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="filters.class_name" placeholder="请输入班级" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="政治面貌">
          <el-select v-model="filters.political_status" placeholder="请选择" clearable style="width: 130px">
            <el-option label="群众" value="masses" />
            <el-option label="团员" value="member" />
            <el-option label="入党积极分子" value="activist" />
            <el-option label="预备党员" value="probationary" />
            <el-option label="正式党员" value="party_member" />
          </el-select>
        </el-form-item>
        <el-form-item class="filter-actions">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table :data="students" v-loading="loading" style="width: 100%" size="small" border>
      <el-table-column prop="student_id" label="学号" width="120" />
      <el-table-column prop="user_info.real_name" label="姓名" width="100" />
      <el-table-column prop="department_name" label="学院" />
      <el-table-column prop="major" label="专业" />
      <el-table-column prop="class_name" label="班级" width="120" />
      <el-table-column prop="grade" label="年级" width="100" />
      <el-table-column label="政治面貌" width="130">
        <template #default="{ row }">
          <el-tag :type="getPoliticalTagType(row.political_status)" size="small">
            {{ row.political_status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button type="primary" link size="small" @click="handleView(scope.row)">查看</el-button>
          <el-button type="success" link size="small" @click="handleEdit(scope.row)">编辑</el-button>
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
    
    <!-- 学生详情对话框 -->
    <el-dialog v-model="detailVisible" title="学生详情" width="800px" destroy-on-close>
      <StudentDetail v-if="detailVisible" :student-id="currentStudentId" />
    </el-dialog>

    <!-- 新增/编辑学生对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑学生' : '新增学生'" width="640px" destroy-on-close @close="resetForm">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" status-icon>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="form.student_id" />
        </el-form-item>
        <el-form-item label="专业" prop="major">
          <el-input v-model="form.major" />
        </el-form-item>
        <el-form-item label="班级" prop="class_name">
          <el-input v-model="form.class_name" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-input v-model="form.grade" placeholder="如：2021级" />
        </el-form-item>
        <el-form-item label="学院" prop="department">
          <el-select v-model="form.department" placeholder="请选择学院" clearable style="width: 100%">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
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
        <el-form-item label="政治面貌" prop="political_status">
          <el-select v-model="form.political_status" placeholder="请选择">
            <el-option label="群众" value="masses" />
            <el-option label="团员" value="member" />
            <el-option label="入党积极分子" value="activist" />
            <el-option label="预备党员" value="probationary" />
            <el-option label="正式党员" value="party_member" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="formLoading" @click="submitForm">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Excel 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="Excel 导入学生" width="520px">
      <el-upload
        ref="uploadRef"
        drag
        :file-list="importFileList"
        :auto-upload="false"
        :multiple="false"
        :limit="1"
        accept=".xls,.xlsx"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :http-request="handleImportRequest"
      >
        <div class="el-upload__text">将 Excel 文件拖到此处，或点击选择</div>
        <div class="el-upload__tip">支持 .xls / .xlsx，首行为表头，需包含“学号、姓名”等字段</div>
      </el-upload>
      <div v-if="importResult" class="import-result">
        <el-alert
          :title="`本次导入：新增 ${importResult.created || 0} 条，更新 ${importResult.updated || 0} 条`"
          type="success"
          show-icon
          class="import-result-alert"
        />
        <el-alert
          v-if="importResult.errors && importResult.errors.length"
          title="以下数据行未被导入："
          type="warning"
          show-icon
          :closable="false"
          class="import-error-alert"
        >
          <template #default>
            <el-scrollbar max-height="160" class="import-error-list">
              <ul>
                <li v-for="(msg, index) in importResult.errors" :key="index">
                  {{ msg }}
                </li>
              </ul>
            </el-scrollbar>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="handleImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download } from '@element-plus/icons-vue'
import api from '@/utils/api'
import StudentDetail from './StudentDetail.vue'

const loading = ref(false)
const students = ref([])
const departments = ref([])
const detailVisible = ref(false)
const currentStudentId = ref(null)

const filters = reactive({
  real_name: '',
  department: null,
  major: '',
  gender: '',
  grade: '',
  class_name: '',
  political_status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const fetchStudents = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filters
    }
    if (filters.department) {
      params.department = filters.department
    }
    if (filters.gender) {
      params.user__gender = filters.gender
    }
    if (filters.real_name) {
      params.search = filters.real_name
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) delete params[key]
    })
    const response = await api.get('/students/', { params })
    students.value = response.data.results || response.data
    pagination.total = response.data.count || response.data.length || 0
  } catch (error) {
    ElMessage.error('获取学生列表失败')
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
  const hasFilter = Object.values(filters).some(v => v !== '' && v !== null)
  if (!hasFilter) {
    ElMessage.warning('请至少选择一个筛选条件')
    return
  }
  pagination.page = 1
  fetchStudents()
}

const handleReset = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = key === 'department' ? null : ''
  })
  handleSearch()
}

const formVisible = ref(false)
const isEdit = ref(false)
const formLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  student_id: '',
  real_name: '',
  major: '',
  class_name: '',
  grade: '',
  department: null,
  id_card: '',
  phone: '',
  email: '',
  political_status: 'masses'
})

const rules = {
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }],
  class_name: [{ required: true, message: '请输入班级', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入年级', trigger: 'blur' }],
  political_status: [{ required: true, message: '请选择政治面貌', trigger: 'change' }]
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  form.id = null
  form.student_id = ''
  form.real_name = ''
  form.major = ''
  form.class_name = ''
  form.grade = ''
  form.id_card = ''
  form.phone = ''
  form.email = ''
  form.political_status = 'masses'
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  formVisible.value = true
}

const handleView = (row) => {
  currentStudentId.value = row.id
  detailVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  formVisible.value = true
  form.id = row.id
  form.student_id = row.student_id
  form.real_name = row.user_info?.real_name || ''
  form.major = row.major
  form.class_name = row.class_name
  form.grade = row.grade
  form.department = row.department || null
  form.id_card = row.user_info?.id_card || ''
  form.phone = row.user_info?.phone || ''
  form.email = row.user_info?.email || ''
  form.political_status = row.political_status
}

const submitForm = () => {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    formLoading.value = true
    try {
      const payload = {
        student_id: form.student_id,
        real_name: form.real_name,
        major: form.major,
        class_name: form.class_name,
        grade: form.grade,
        department: form.department,
        id_card: form.id_card,
        phone: form.phone,
        email: form.email,
        political_status: form.political_status
      }
      if (isEdit.value && form.id) {
        await api.put(`/students/${form.id}/`, payload)
        ElMessage.success('更新成功')
      } else {
        await api.post('/students/', payload)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      fetchStudents()
    } catch (error) {
      ElMessage.error('保存失败')
      console.error(error)
    } finally {
      formLoading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该学生吗？', '提示', {
      type: 'warning'
    })
    await api.delete(`/students/${row.id}/`)
    ElMessage.success('删除成功')
    fetchStudents()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

const handleSizeChange = () => {
  fetchStudents()
}

const handlePageChange = () => {
  fetchStudents()
}

onMounted(() => {
  fetchStudents()
  fetchDepartments()
})

const getPoliticalTagType = (status) => {
  if (status === 'member') return 'success'
  if (status === 'activist' || status === 'probationary') return 'warning'
  if (status === 'party_member') return 'danger'
  return ''
}

import { exportToExcel } from '@/utils/export'
const isExportMasked = ref(true)
const exportLoading = ref(false)
const exportTemplateLoading = ref(false)

const handleExportTemplate = () => {
  exportTemplateLoading.value = true
  try {
    const columns = [
      { key: 'student_id', label: '学号' },
      { key: 'real_name', label: '姓名' },
      { key: 'major', label: '专业' },
      { key: 'class_name', label: '班级' },
      { key: 'grade', label: '年级' },
      { key: 'political_status', label: '政治面貌' },
      { key: 'phone', label: '手机号' },
      { key: 'email', label: '邮箱' }
    ]
    const emptyRow = {
      student_id: '',
      real_name: '',
      major: '',
      class_name: '',
      grade: '',
      political_status: '',
      phone: '',
      email: ''
    }
    exportToExcel([emptyRow], '学生导入模板.xlsx', columns, { mask: false })
  } finally {
    exportTemplateLoading.value = false
  }
}

const handleExport = async () => {
  exportLoading.value = true
  try {
    const params = {
      page: 1,
      page_size: 10000,
      ...filters
    }
    Object.keys(params).forEach(key => {
      if (params[key] === '') delete params[key]
    })
    const response = await api.get('/students/', { params })
    const list = response.data.results || response.data
    const exportData = list.map((item) => ({
      ...item,
      phone: item.user_info?.phone || '',
      id_card: item.user_info?.id_card || '',
      email: item.user_info?.email || '',
      real_name: item.user_info?.real_name || '',
      political_status: item.political_status_display
    }))
    const columns = [
      { key: 'student_id', label: '学号' },
      { key: 'real_name', label: '姓名' },
      { key: 'major', label: '专业' },
      { key: 'class_name', label: '班级' },
      { key: 'phone', label: '手机号' },
      { key: 'id_card', label: '身份证号' },
      { key: 'email', label: '邮箱' },
      { key: 'political_status', label: '政治面貌' }
    ]
    exportToExcel(exportData, '学生名单.xlsx', columns, { mask: isExportMasked.value })
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  } finally {
    exportLoading.value = false
  }
}

const importDialogVisible = ref(false)
const importLoading = ref(false)
const importFileList = ref([])
const uploadRef = ref(null)
const importResult = ref(null)

const handleFileChange = (file, fileList) => {
  importFileList.value = fileList.slice(-1)
  importResult.value = null
}

const handleFileRemove = (file, fileList) => {
  importFileList.value = fileList
}

const handleImport = () => {
  if (!importFileList.value.length) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }
  if (uploadRef.value) {
    uploadRef.value.submit()
  }
}

const handleImportRequest = async (option) => {
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', option.file)
    const res = await api.post('/students/import_excel/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    const data = res.data || {}
    importResult.value = {
      created: data.created || 0,
      updated: data.updated || 0,
      errors: data.errors || []
    }
    ElMessage.success(`导入成功，新增 ${importResult.value.created} 条，更新 ${importResult.value.updated} 条`)
    importFileList.value = []
    fetchStudents()
    if (option.onSuccess) {
      option.onSuccess(data)
    }
  } catch (error) {
    importResult.value = null
    ElMessage.error(error.response?.data?.error || '导入失败')
    console.error(error)
    if (option.onError) {
      option.onError(error)
    }
  } finally {
    importLoading.value = false
  }
}

watch(importDialogVisible, (visible) => {
  if (!visible) {
    importFileList.value = []
    importResult.value = null
    importLoading.value = false
  }
})
</script>

<style scoped>
.student-card {
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

.export-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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

.import-result {
  margin-top: 16px;
}

.import-result-alert {
  margin-bottom: 8px;
}

.import-error-alert {
  margin-top: 8px;
}

.import-error-list {
  margin-top: 8px;
}

.import-error-list ul {
  padding-left: 16px;
  margin: 0;
}

.import-error-list li {
  line-height: 1.6;
  font-size: 13px;
}
</style>
