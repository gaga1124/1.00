<template>
  <div class="grade-list-container page-container">
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>教务管理</el-breadcrumb-item>
        <el-breadcrumb-item>成绩查询</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <el-card class="stats-card" v-if="stats && (isStudent || isTeacher)">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic :title="isStudent ? '平均绩点 (GPA)' : '课程平均分'" :value="isStudent ? stats.average_gpa : stats.average_score" :precision="2">
            <template #suffix>
              <el-icon><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic :title="isStudent ? '已获学分' : '及格率'" :value="isStudent ? stats.total_credits : stats.pass_rate" :precision="isStudent ? 1 : 1">
            <template #suffix>{{ isStudent ? '' : '%' }}</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="修读课程数" :value="stats.total_courses" />
        </el-col>
        <el-col :span="6">
          <div class="chart-mini">
            <div class="chart-label">及格概况</div>
            <el-progress 
              type="dashboard" 
              :percentage="stats.pass_rate" 
              :width="80"
              :color="colors"
            />
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="list-card mt-20">
      <div class="search-bar">
        <div class="search-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索学生、课程或代码..."
            class="filter-item"
            style="width: 240px;"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select v-model="filterSemester" placeholder="所有学期" clearable @change="handleSearch" class="filter-item">
            <el-option v-for="s in semesters" :key="s" :label="s" :value="s" />
          </el-select>

          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
        <div class="search-right">
          <el-button v-if="isStaff" type="success" @click="handleExport">
            <el-icon><Download /></el-icon>导出成绩
          </el-button>
        </div>
      </div>

      <el-table :data="grades" v-loading="loading" border stripe>
        <el-table-column v-if="!isStudent" prop="student_id" label="学号" width="120" sortable />
        <el-table-column v-if="!isStudent" prop="student_name" label="姓名" width="120" />
        <el-table-column prop="course_code" label="课程代码" width="120" />
        <el-table-column prop="course_name" label="课程名称" min-width="180" />
        <el-table-column label="成绩详情" align="center">
          <el-table-column prop="usual_score" label="平时" width="80" />
          <el-table-column prop="midterm_score" label="期中" width="80" />
          <el-table-column prop="final_score" label="期末" width="80" />
          <el-table-column prop="total_score" label="总评" width="90" sortable>
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.total_score)" effect="dark">
                {{ row.total_score }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column prop="grade_point" label="绩点" width="80" sortable />
        <el-table-column prop="grade_level" label="等第" width="80" align="center">
          <template #default="{ row }">
            <span :class="['grade-level', row.grade_level]">{{ row.grade_level }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="semester" label="学期" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_confirmed ? 'success' : 'warning'" size="small">
              {{ row.is_confirmed ? '已确认' : '待确认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isStaff" label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">修改</el-button>
            <el-button v-if="!row.is_confirmed" link type="success" @click="handleConfirm(row)">确认</el-button>
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

    <!-- 成绩修改弹窗 -->
    <el-dialog v-model="dialogVisible" title="修改成绩" width="500px">
      <el-form :model="gradeForm" label-width="100px" ref="gradeFormRef">
        <el-form-item label="学生">
          <el-input :value="`${gradeForm.student_name} (${gradeForm.student_id})`" disabled />
        </el-form-item>
        <el-form-item label="平时成绩">
          <el-input-number v-model="gradeForm.usual_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="期中成绩">
          <el-input-number v-model="gradeForm.midterm_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="期末成绩">
          <el-input-number v-model="gradeForm.final_score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="gradeForm.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGrade" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, TrendCharts } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import * as XLSX from 'xlsx'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')
const isTeacher = computed(() => userStore.user?.role === 'teacher')
const isStudent = computed(() => userStore.user?.role === 'student')
const isStaff = computed(() => isAdmin.value || isTeacher.value)

const grades = ref([])
const stats = ref(null)
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const filterSemester = ref('')
const semesters = ref([])

const dialogVisible = ref(false)
const submitting = ref(false)
const gradeForm = reactive({
  id: null,
  student_name: '',
  student_id: '',
  usual_score: 0,
  midterm_score: 0,
  final_score: 0,
  remark: ''
})

const colors = [
  { color: '#f56c6c', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#5cb87a', percentage: 100 },
]

const getScoreType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 60) return ''
  return 'danger'
}

const fetchGrades = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      search: searchQuery.value,
      semester: filterSemester.value
    }
    const res = await api.get('/academic/grades/', { params })
    // 如果后端返回的是 DRF 分页格式
    if (res.data.results) {
      grades.value = res.data.results
      total.value = res.data.count
    } else {
      grades.value = res.data
      total.value = res.data.length
    }
    
    // 获取统计信息
    fetchStats()
  } catch (error) {
    console.error('获取成绩失败', error)
    ElMessage.error('获取成绩列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await api.get('/academic/grades/statistics/', {
      params: { semester: filterSemester.value }
    })
    stats.value = res.data
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

const fetchSemesters = async () => {
  try {
    const res = await api.get('/academic/grades/semesters/')
    semesters.value = res.data
  } catch (error) {
    console.error('获取学期列表失败', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchGrades()
}

const resetSearch = () => {
  searchQuery.value = ''
  filterSemester.value = ''
  handleSearch()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchGrades()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchGrades()
}

const handleEdit = (row) => {
  Object.assign(gradeForm, {
    id: row.id,
    student_name: row.student_name,
    student_id: row.student_id,
    usual_score: row.usual_score,
    midterm_score: row.midterm_score,
    final_score: row.final_score,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

const submitGrade = async () => {
  submitting.value = true
  try {
    await api.patch(`/academic/grades/${gradeForm.id}/`, {
      usual_score: gradeForm.usual_score,
      midterm_score: gradeForm.midterm_score,
      final_score: gradeForm.final_score,
      remark: gradeForm.remark
    })
    ElMessage.success('成绩修改成功')
    dialogVisible.value = false
    fetchGrades()
  } catch (error) {
    ElMessage.error('修改失败')
  } finally {
    submitting.value = false
  }
}

const handleConfirm = async (row) => {
  try {
    await ElMessageBox.confirm('确认后成绩将对学生可见，确定吗？', '提示', {
      type: 'warning'
    })
    await api.post(`/academic/grades/${row.id}/confirm/`)
    ElMessage.success('成绩已确认')
    fetchGrades()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const handleExport = () => {
  const data = grades.value.map(g => ({
    '学号': g.student_id,
    '姓名': g.student_name,
    '课程代码': g.course_code,
    '课程名称': g.course_name,
    '平时成绩': g.usual_score,
    '期中成绩': g.midterm_score,
    '期末成绩': g.final_score,
    '总评成绩': g.total_score,
    '绩点': g.grade_point,
    '等第': g.grade_level,
    '学期': g.semester
  }))
  
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "成绩表")
  XLSX.writeFile(wb, `成绩导出_${new Date().toLocaleDateString()}.xlsx`)
}

onMounted(() => {
  fetchGrades()
  fetchSemesters()
})
</script>

<style scoped lang="scss">
.grade-list-container {
  .stats-card {
    margin-bottom: 20px;
    
    .chart-mini {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .chart-label {
        font-size: 12px;
        color: #909399;
        margin-bottom: 5px;
      }
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

      .search-right {
        display: flex;
        gap: 12px;
      }

      .filter-item {
        width: 150px;
      }
    }
  }

  .grade-level {
    font-weight: bold;
    &.A { color: #67c23a; }
    &.B { color: #409eff; }
    &.C { color: #e6a23c; }
    &.D { color: #909399; }
    &.F { color: #f56c6c; }
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
