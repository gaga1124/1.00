<template>
  <div class="notification-template-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通知模板管理</span>
          <el-button type="primary" @click="handleCreate">新建模板</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="templates" style="width: 100%">
        <el-table-column prop="name" label="模板名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title_template" label="标题模板" min-width="200" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 模板编辑/新建弹窗 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="模板类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="会议通知" value="meeting" />
            <el-option label="放假通知" value="holiday" />
            <el-option label="活动通知" value="activity" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题模板" prop="title_template">
          <el-input v-model="form.title_template" placeholder="例如：关于召开{date}会议的通知" />
          <div class="form-tip">支持变量: {date}</div>
        </el-form-item>
        <el-form-item label="内容模板" prop="content_template">
          <el-input 
            v-model="form.content_template" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入内容模板，支持变量 {date}" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const loading = ref(false)
const templates = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const form = ref({
  id: undefined,
  name: '',
  type: 'meeting',
  title_template: '',
  content_template: ''
})

const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模板类型', trigger: 'change' }],
  title_template: [{ required: true, message: '请输入标题模板', trigger: 'blur' }],
  content_template: [{ required: true, message: '请输入内容模板', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑模板' : '新建模板')

const getTypeTag = (type) => {
  const map = {
    meeting: 'primary',
    holiday: 'success',
    activity: 'warning'
  }
  return map[type] || 'info'
}

const getTypeLabel = (type) => {
  const map = {
    meeting: '会议通知',
    holiday: '放假通知',
    activity: '活动通知'
  }
  return map[type] || type
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

const fetchData = async () => {
  loading.value = true
  try {
    const response = await api.get('/notifications/templates/')
    templates.value = response.data.results || response.data
  } catch (error) {
    console.error(error)
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEdit.value = false
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该模板吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/notifications/templates/${row.id}/`)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error(error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  form.value = {
    id: undefined,
    name: '',
    type: 'meeting',
    title_template: '',
    content_template: ''
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await api.put(`/notifications/templates/${form.value.id}/`, form.value)
          ElMessage.success('更新成功')
        } else {
          await api.post('/notifications/templates/', form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error(error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.notification-template-list {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 4px;
}
</style>
