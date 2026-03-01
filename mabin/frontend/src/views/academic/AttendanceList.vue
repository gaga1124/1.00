<template>
  <div class="attendance-container page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>教务管理</el-breadcrumb-item>
        <el-breadcrumb-item>考勤管理</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="header-actions">
        <el-button type="warning" @click="router.push('/academic/live-checkin')">
          <el-icon><Timer /></el-icon>实时签到
        </el-button>
        <el-button v-if="isStaff" type="primary" @click="handleBatch">
          <el-icon><Plus /></el-icon>批量录入
        </el-button>
        <el-button v-if="isStaff" type="success" @click="handleExport">
          <el-icon><Download /></el-icon>导出报表
        </el-button>
      </div>
    </div>

    <el-card class="stats-card" v-if="stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总记录数" :value="stats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="出勤率" :value="stats.present_rate" :precision="2">
            <template #suffix>%</template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <div class="status-summary">
            <el-tag v-for="(count, status) in stats.status_counts" :key="status" :type="getStatusType(status)" class="status-tag">
              {{ getStatusLabel(status) }}: {{ count }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="list-card mt-20">
      <div class="search-bar">
        <div class="search-left">
          <el-select v-model="filterCourse" placeholder="选择课程" clearable @change="handleSearch" class="filter-item">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <el-date-picker
            v-model="filterDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
            class="filter-item"
          />
          <el-select v-model="filterStatus" placeholder="所有状态" clearable @change="handleSearch" class="filter-item">
            <el-option label="出勤" value="present" />
            <el-option label="缺勤" value="absent" />
            <el-option label="迟到" value="late" />
            <el-option label="早退" value="early_leave" />
            <el-option label="请假" value="excused" />
          </el-select>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
      </div>

      <el-table :data="attendances" v-loading="loading" border stripe>
        <el-table-column prop="date" label="日期" width="120" sortable />
        <el-table-column v-if="!isStudent" prop="student_id" label="学号" width="120" />
        <el-table-column v-if="!isStudent" prop="student_name" label="姓名" width="120" />
        <el-table-column prop="course_name" label="课程名称" min-width="180" />
        <el-table-column prop="time_slot" label="时间段" width="120" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column v-if="isStaff" label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">修改</el-button>
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

    <!-- 批量签到对话框 -->
    <el-dialog v-model="batchVisible" title="批量录入签到" width="800px">
      <el-form :model="batchForm" label-width="100px" class="batch-form">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择课程">
              <el-select v-model="batchForm.course_id" @change="fetchCourseStudents" placeholder="请选择课程" style="width: 100%">
                <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日期">
              <el-date-picker 
                v-model="batchForm.date" 
                type="date" 
                value-format="YYYY-MM-DD" 
                style="width: 100%"
                @change="fetchCourseStudents"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="时间段">
          <el-input v-model="batchForm.time_slot" placeholder="如：第一节课、上午、下午" />
        </el-form-item>
        
        <div class="student-table-header">
          <span>学生签到列表</span>
          <el-alert v-if="leaveCount > 0" :title="`检测到 ${leaveCount} 名学生处于请假期间，已自动标记为‘请假’`" type="info" :closable="false" show-icon />
        </div>

        <el-table :data="courseStudents" border max-height="400px">
          <el-table-column prop="student_name" label="姓名" width="120" />
          <el-table-column prop="student_id" label="学号" width="120" />
          <el-table-column label="签到状态">
            <template #default="{ row }">
              <el-radio-group v-model="row.status">
                <el-radio label="present">出勤</el-radio>
                <el-radio label="absent">缺勤</el-radio>
                <el-radio label="late">迟到</el-radio>
                <el-radio label="early_leave">早退</el-radio>
                <el-radio label="excused">请假</el-radio>
              </el-radio-group>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatch" :loading="submitting">提交录入</el-button>
      </template>
    </el-dialog>

    <!-- 单条记录修改对话框 -->
    <el-dialog v-model="editVisible" title="修改签到记录" width="400px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="学生">
          <el-input :value="editForm.student_name" disabled />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="出勤" value="present" />
            <el-option label="缺勤" value="absent" />
            <el-option label="迟到" value="late" />
            <el-option label="早退" value="early_leave" />
            <el-option label="请假" value="excused" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Search, Timer } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import * as XLSX from 'xlsx'

const router = useRouter()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStudent = computed(() => userStore.user?.role === 'student')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const attendances = ref([])
const stats = ref(null)
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const courses = ref([])
const filterCourse = ref('')
const filterDate = ref('')
const filterStatus = ref('')

const batchVisible = ref(false)
const submitting = ref(false)
const batchForm = reactive({
  course_id: '',
  date: new Date().toISOString().split('T')[0],
  time_slot: ''
})
const courseStudents = ref([])
const leaveCount = ref(0)

const editVisible = ref(false)
const editForm = reactive({
  id: null,
  student_name: '',
  status: '',
  remark: ''
})

const getStatusType = (status) => {
  const map = {
    present: 'success',
    absent: 'danger',
    late: 'warning',
    early_leave: 'warning',
    excused: 'info'
  }
  return map[status] || ''
}

const getStatusLabel = (status) => {
  const map = {
    present: '出勤',
    absent: '缺勤',
    late: '迟到',
    early_leave: '早退',
    excused: '请假'
  }
  return map[status] || status
}

const fetchCourses = async () => {
  try {
    const res = await api.get('/academic/courses/')
    courses.value = res.data.results || res.data
  } catch (error) {
    console.error('获取课程失败', error)
  }
}

const fetchAttendances = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      course: filterCourse.value,
      date: filterDate.value,
      status: filterStatus.value
    }
    const res = await api.get('/academic/attendances/', { params })
    if (res.data.results) {
      attendances.value = res.data.results
      total.value = res.data.count
    } else {
      attendances.value = res.data
      total.value = res.data.length
    }
    fetchStats()
  } catch (error) {
    ElMessage.error('获取签到列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const params = {
      course_id: filterCourse.value,
      student_id: isStudent.value ? userStore.user?.id : undefined
    }
    const res = await api.get('/academic/attendances/statistics/', { params })
    stats.value = res.data
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchAttendances()
}

const resetSearch = () => {
  filterCourse.value = ''
  filterDate.value = ''
  filterStatus.value = ''
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchAttendances()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchAttendances()
}

const handleBatch = () => {
  batchVisible.value = true
  courseStudents.value = []
  leaveCount.value = 0
}

const fetchCourseStudents = async () => {
  if (!batchForm.course_id || !batchForm.date) return
  
  try {
    const res = await api.get(`/academic/courses/${batchForm.course_id}/students/`)
    const students = res.data.map(s => ({
      student_id: s.student,
      student_name: s.student_name,
      status: 'present'
    }))
    
    // 检查请假状态
    const studentIds = students.map(s => s.student_id)
    const leaveRes = await api.get('/academic/attendances/check_leaves/', {
      params: { 
        'student_ids[]': studentIds,
        date: batchForm.date
      }
    })
    
    const leaveStudentIds = leaveRes.data.leave_student_ids || []
    leaveCount.value = leaveStudentIds.length
    
    courseStudents.value = students.map(s => ({
      ...s,
      status: leaveStudentIds.includes(s.student_id) ? 'excused' : 'present'
    }))
  } catch (error) {
    ElMessage.error('获取学生名单失败')
  }
}

const submitBatch = async () => {
  if (!batchForm.course_id) {
    return ElMessage.warning('请选择课程')
  }
  submitting.value = true
  try {
    await api.post('/academic/attendances/batch_record/', {
      course_id: batchForm.course_id,
      date: batchForm.date,
      time_slot: batchForm.time_slot,
      records: courseStudents.value
    })
    ElMessage.success('批量签到录入成功')
    batchVisible.value = false
    fetchAttendances()
  } catch (error) {
    ElMessage.error('录入失败')
  } finally {
    submitting.value = false
  }
}

const handleEdit = (row) => {
  Object.assign(editForm, {
    id: row.id,
    student_name: row.student_name,
    status: row.status,
    remark: row.remark || ''
  })
  editVisible.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    await api.patch(`/academic/attendances/${editForm.id}/`, {
      status: editForm.status,
      remark: editForm.remark
    })
    ElMessage.success('修改成功')
    editVisible.value = false
    fetchAttendances()
  } catch (error) {
    ElMessage.error('修改失败')
  } finally {
    submitting.value = false
  }
}

const handleExport = () => {
  const data = attendances.value.map(a => ({
    '日期': a.date,
    '学号': a.student_id,
    '姓名': a.student_name,
    '课程': a.course_name,
    '时间段': a.time_slot,
    '状态': a.status_display,
    '备注': a.remark
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "签到表")
  XLSX.writeFile(wb, `考勤导出_${new Date().toLocaleDateString()}.xlsx`)
}

onMounted(() => {
  fetchCourses()
  fetchAttendances()
})
</script>

<style scoped lang="scss">
.attendance-container {
  .stats-card {
    margin-bottom: 20px;
    
    .status-summary {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: flex-end;
      height: 100%;
      align-items: center;
    }
    
    .status-tag {
      margin-left: 10px;
    }
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

  .batch-form {
    max-height: 500px;
    overflow-y: auto;
    
    .student-table-header {
      margin: 20px 0 10px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      
      .el-alert {
        width: auto;
        padding: 4px 16px;
      }
    }
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
