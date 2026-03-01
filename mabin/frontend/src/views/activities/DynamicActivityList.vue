<template>
  <div class="dynamic-activity">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>自定义活动</span>
          <el-button type="primary" @click="handleCreate" v-if="selectedType">申报{{ selectedType.name }}</el-button>
        </div>
      </template>

      <!-- 活动类型选择 -->
      <div class="type-selector">
        <el-radio-group v-model="typeId" @change="handleTypeChange">
          <el-radio-button v-for="t in activityTypes" :key="t.id" :label="t.id">
            {{ t.name }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <!-- 数据列表 -->
      <el-table :data="instances" v-loading="loading" style="width: 100%; margin-top: 20px">
        <el-table-column v-for="field in tableFields" :key="field.name" :prop="'data.' + field.name" :label="field.label" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
            <el-button link type="danger" @click="handleDelete(row)" v-if="canDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 动态表单对话框 -->
    <el-dialog v-model="formVisible" :title="`申报 - ${selectedType?.name}`" width="550px">
      <el-form :model="formData" label-width="100px" ref="formRef">
        <el-form-item v-for="field in selectedType?.schema?.fields" :key="field.name" :label="field.label" :prop="field.name">
          <el-input v-if="field.type === 'text'" v-model="formData[field.name]" />
          <el-input v-if="field.type === 'textarea'" type="textarea" v-model="formData[field.name]" />
          <el-input-number v-if="field.type === 'number'" v-model="formData[field.name]" style="width: 100%" />
          <el-date-picker v-if="field.type === 'date'" v-model="formData[field.name]" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin' || userStore.user?.role === 'teacher')

const loading = ref(false)
const activityTypes = ref([])
const typeId = ref(null)
const instances = ref([])
const formVisible = ref(false)
const formData = reactive({})

const statusMap = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回'
}

const selectedType = computed(() => {
  return activityTypes.value.find(t => t.id === typeId.value)
})

const tableFields = computed(() => {
  if (!selectedType.value) return []
  // 只在表格展示前3个字段
  return selectedType.value.schema.fields.slice(0, 3)
})

const fetchTypes = async () => {
  try {
    const response = await axios.get('/api/activities/activity-types/')
    activityTypes.value = response.data
    if (activityTypes.value.length > 0) {
      typeId.value = activityTypes.value[0].id
      fetchInstances()
    }
  } catch (error) {
    ElMessage.error('获取活动类型失败')
  }
}

const fetchInstances = async () => {
  if (!typeId.value) return
  loading.value = true
  try {
    const response = await axios.get('/api/activities/activity-instances/', {
      params: { activity_type: typeId.value }
    })
    instances.value = response.data
  } catch (error) {
    ElMessage.error('获取活动数据失败')
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  fetchInstances()
}

const handleCreate = () => {
  // 重置表单
  selectedType.value.schema.fields.forEach(f => {
    formData[f.name] = f.type === 'number' ? 0 : ''
  })
  formVisible.value = true
}

const submitForm = async () => {
  try {
    await axios.post('/api/activities/activity-instances/', {
      activity_type: typeId.value,
      data: { ...formData }
    })
    ElMessage.success('提交成功')
    formVisible.value = false
    fetchInstances()
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该申请吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await axios.delete(`/api/activities/activity-instances/${row.id}/`)
      ElMessage.success('删除成功')
      fetchInstances()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const canDelete = (row) => {
  return isAdmin.value || (row.status === 'pending' && row.creator === userStore.user?.id)
}

const getStatusTag = (status) => {
  const map = {
    pending: 'info',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

const formatDateTime = (val) => {
  if (!val) return ''
  return new Date(val).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchTypes()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.type-selector {
  margin-bottom: 20px;
  text-align: center;
}
</style>
