<template>
  <div class="course-list page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>教务管理</el-breadcrumb-item>
        <el-breadcrumb-item>课程管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd" v-if="isStaff">
          <el-icon><Plus /></el-icon>新增课程
        </el-button>
        <el-button type="info" plain @click="handleExportTemplate" v-if="isStaff">
          <el-icon><Notebook /></el-icon>导出模板
        </el-button>
        <el-button type="warning" @click="importDialogVisible = true" v-if="isStaff">
          <el-icon><Notebook /></el-icon>Excel导入
        </el-button>
      </div>
    </div>
    
    <el-card class="list-card">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <div class="search-left">
          <el-input
            v-model="searchQuery.name"
            placeholder="搜索课程名称..."
            class="filter-item"
            clearable
            @clear="fetchCourses"
            @keyup.enter="fetchCourses"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-input
            v-model="searchQuery.course_code"
            placeholder="课程代码"
            class="filter-item"
            style="width: 150px"
            clearable
            @clear="fetchCourses"
            @keyup.enter="fetchCourses"
          />

          <el-select v-model="searchQuery.course_type" placeholder="全部类型" clearable class="filter-item" style="width: 120px" @change="fetchCourses">
            <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
          </el-select>

          <el-input
            v-model="searchQuery.semester"
            placeholder="学期 (如: 2024-1)"
            class="filter-item"
            style="width: 150px"
            clearable
            @clear="fetchCourses"
            @keyup.enter="fetchCourses"
          />

          <el-button type="primary" @click="fetchCourses">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
      </div>

      <el-table :data="courses" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="name" label="课程名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="credit" label="学分" width="80" align="center" />
        <el-table-column prop="hours" label="学时" width="80" align="center" />
        <el-table-column prop="course_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.course_type)" effect="light">
              {{ typeMap[row.course_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assessment_method" label="考核方式" width="120" show-overflow-tooltip />
        <el-table-column label="授课教师" width="150">
          <template #default="{ row }">
            <div class="teacher-cell">
              <el-avatar :size="24" :src="row.teacher_info?.avatar" style="margin-right: 8px">
                {{ row.teacher_info?.real_name?.[0] }}
              </el-avatar>
              <span>{{ row.teacher_info?.real_name || '未分配' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="学期" width="140" />
        <el-table-column label="选课情况" width="120">
          <template #default="{ row }">
            <el-tooltip :content="`容量: ${row.max_students}`" placement="top">
              <span :class="{'text-danger': row.current_students >= row.max_students}">
                {{ row.current_students }} / {{ row.max_students }}
              </span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-divider direction="vertical" v-if="isStaff" />
            <el-button link type="primary" @click="handleEdit(row)" v-if="isStaff">编辑</el-button>
            <el-divider direction="vertical" v-if="isAdmin" />
            <el-button link type="danger" @click="handleDelete(row)" v-if="isAdmin">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="650px" destroy-on-close>
      <el-form :model="courseForm" :rules="rules" ref="formRef" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程代码" prop="course_code">
              <el-input v-model="courseForm.course_code" placeholder="如：CS101" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程名称" prop="name">
              <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="课程类型" prop="course_type">
              <el-select v-model="courseForm.course_type" placeholder="请选择" style="width: 100%">
                <el-option v-for="(label, value) in typeMap" :key="value" :label="label" :value="value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学分" prop="credit">
              <el-input-number v-model="courseForm.credit" :precision="1" :step="0.5" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学时" prop="hours">
              <el-input-number v-model="courseForm.hours" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="授课教师" prop="teacher">
              <el-select
                v-model="courseForm.teacher"
                filterable
                remote
                placeholder="搜索教师姓名"
                :remote-method="searchTeachers"
                :loading="teachersLoading"
                style="width: 100%"
              >
                <el-option
                  v-for="teacher in teachers"
                  :key="teacher.id"
                  :label="`${teacher.real_name} (${teacher.username})`"
                  :value="teacher.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学期" prop="semester">
              <el-input v-model="courseForm.semester" placeholder="如：2024-2025-1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大选课人数" prop="max_students">
              <el-input-number v-model="courseForm.max_students" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开课学院" prop="department">
              <el-select v-model="courseForm.department" placeholder="选择学院" style="width: 100%">
                <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="考核方式" prop="assessment_method">
              <el-input v-model="courseForm.assessment_method" placeholder="如：考试、考查、论文等" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="课程描述" prop="description">
          <el-input v-model="courseForm.description" type="textarea" :rows="4" placeholder="请输入课程简介..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 课程详情 -->
    <el-dialog v-model="detailVisible" title="课程详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="课程代码">{{ currentCourse.course_code }}</el-descriptions-item>
        <el-descriptions-item label="课程类型">
          <el-tag :type="getTypeTag(currentCourse.course_type)">{{ typeMap[currentCourse.course_type] }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="课程名称" :span="2">{{ currentCourse.name }}</el-descriptions-item>
        <el-descriptions-item label="授课教师">{{ currentCourse.teacher_info?.real_name }}</el-descriptions-item>
        <el-descriptions-item label="学期">{{ currentCourse.semester }}</el-descriptions-item>
        <el-descriptions-item label="学分">{{ currentCourse.credit }}</el-descriptions-item>
        <el-descriptions-item label="学时">{{ currentCourse.hours }}</el-descriptions-item>
        <el-descriptions-item label="考核方式">{{ currentCourse.assessment_method || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="选课人数">{{ currentCourse.current_students }} / {{ currentCourse.max_students }}</el-descriptions-item>
        <el-descriptions-item label="开课学院">{{ currentCourse.department_name || '未分配' }}</el-descriptions-item>
        <el-descriptions-item label="课程描述" :span="2">{{ currentCourse.description || '暂无描述' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Excel 导入课程 -->
    <el-dialog v-model="importDialogVisible" title="Excel 导入课程" width="520px">
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
        <div class="el-upload__tip">
          支持 .xls / .xlsx，首行为表头，需包含
          “课程代码、课程名称、学分、学时、课程类型、学期、最大选课人数、考核方式、开课学院”等字段
        </div>
      </el-upload>
      <div v-if="importResult" class="import-result">
        <el-alert
          :title="`本次导入：新增 ${importResult.created || 0} 门，更新 ${importResult.updated || 0} 门`"
          type="success"
          show-icon
          class="import-result-alert"
        />
        <el-alert
          v-if="importResult.errors && importResult.errors.length"
          title="以下数据行未被导入或存在问题："
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
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Notebook, Plus, Search, User } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { exportToExcel } from '@/utils/export'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const courses = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const teachersLoading = ref(false)
const currentCourse = ref({})
const formRef = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchQuery = reactive({
  name: '',
  course_code: '',
  course_type: '',
  semester: ''
})

const typeMap = {
  required: '必修',
  elective: '选修',
  public: '公选'
}

const courseForm = reactive({
  course_code: '',
  name: '',
  course_type: 'required',
  credit: 2.0,
  hours: 32,
  teacher: null,
  semester: '',
  max_students: 50,
  department: null,
  assessment_method: '',
  description: ''
})

const rules = {
  course_code: [{ required: true, message: '请输入课程代码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  course_type: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
  credit: [{ required: true, message: '请输入学分', trigger: 'blur' }],
  semester: [{ required: true, message: '请输入学期', trigger: 'blur' }]
}

const teachers = ref([])
const departments = ref([])

const importDialogVisible = ref(false)
const importLoading = ref(false)
const importFileList = ref([])
const uploadRef = ref(null)
const importResult = ref(null)
const exportTemplateLoading = ref(false)

const fetchCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      ...searchQuery
    }
    const response = await api.get('/academic/courses/', { params })
    courses.value = response.data.results || response.data
    total.value = response.data.count || (response.data.results ? response.data.results.length : courses.value.length)
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  Object.assign(searchQuery, {
    name: '',
    course_code: '',
    course_type: '',
    semester: ''
  })
  currentPage.value = 1
  fetchCourses()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchCourses()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchCourses()
}

const searchTeachers = async (query) => {
  if (query) {
    teachersLoading.value = true
    try {
      const response = await api.get('/users/', { params: { search: query, role: 'teacher' } })
      teachers.value = response.data.results || response.data
    } catch (error) {
      console.error(error)
    } finally {
      teachersLoading.value = false
    }
  }
}

const fetchDepartments = async () => {
  try {
    const response = await api.get('/rbac/departments/')
    departments.value = response.data.results || response.data
  } catch (error) {
    console.error(error)
  }
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(courseForm, {
    course_code: '',
    name: '',
    course_type: 'required',
    credit: 2.0,
    hours: 32,
    teacher: null,
    semester: '',
    max_students: 50,
    department: null,
    assessment_method: '',
    description: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentCourse.value = row
  Object.assign(courseForm, {
    course_code: row.course_code,
    name: row.name,
    course_type: row.course_type,
    credit: row.credit,
    hours: row.hours,
    teacher: row.teacher,
    semester: row.semester,
    max_students: row.max_students,
    department: row.department,
    assessment_method: row.assessment_method,
    description: row.description
  })
  // 如果有教师，预填充教师列表
  if (row.teacher_info) {
    teachers.value = [row.teacher_info]
  }
  dialogVisible.value = true
}

const handleDetail = (row) => {
  currentCourse.value = row
  detailVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除课程 ${row.name} 吗？`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/academic/courses/${row.id}/`)
      ElMessage.success('删除成功')
      fetchCourses()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/academic/courses/${currentCourse.value.id}/`, courseForm)
          ElMessage.success('修改成功')
        } else {
          await api.post('/academic/courses/', courseForm)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchCourses()
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '保存失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const getTypeTag = (type) => {
  const map = {
    required: 'danger',
    elective: 'success',
    public: 'info'
  }
  return map[type] || 'info'
}

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

const handleExportTemplate = () => {
  exportTemplateLoading.value = true
  try {
    const columns = [
      { key: 'course_code', label: '课程代码' },
      { key: 'name', label: '课程名称' },
      { key: 'credit', label: '学分' },
      { key: 'hours', label: '学时' },
      { key: 'course_type', label: '课程类型' },
      { key: 'semester', label: '学期' },
      { key: 'max_students', label: '最大选课人数' },
      { key: 'assessment_method', label: '考核方式' },
      { key: 'department', label: '开课学院' },
      { key: 'teacher', label: '授课教师' }
    ]
    const emptyRow = {
      course_code: '',
      name: '',
      credit: '',
      hours: '',
      course_type: '',
      semester: '',
      max_students: '',
      assessment_method: '',
      department: '',
      teacher: ''
    }
    exportToExcel([emptyRow], '课程导入模板.xlsx', columns, { mask: false })
  } finally {
    exportTemplateLoading.value = false
  }
}

const handleImportRequest = async (option) => {
  importLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', option.file)
    const res = await api.post('/academic/courses/import_excel/', formData, {
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
    ElMessage.success(`导入成功，新增 ${importResult.value.created} 门，更新 ${importResult.value.updated} 门`)
    importFileList.value = []
    fetchCourses()
    if (option.onSuccess) {
      option.onSuccess(data)
    }
  } catch (error) {
    importResult.value = null
    ElMessage.error(error.response?.data?.error || '导入失败')
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

onMounted(() => {
  fetchCourses()
  fetchDepartments()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-card {
  .search-bar {
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .search-left {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .filter-item {
      width: 200px;
    }
  }
}

.teacher-cell {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
