<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>流程管理</span>
        <el-button type="primary" @click="handleCreate">新建流程</el-button>
      </div>
    </template>
    
    <el-table :data="workflows" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="流程名称" />
      <el-table-column prop="code" label="流程编码" width="150" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="instances_count" label="实例数" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">
            {{ scope.row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleConfig(scope.row)">配置</el-button>
          <el-button type="success" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 流程配置对话框 -->
    <el-dialog v-model="configVisible" :title="currentWorkflow?.name + ' - 节点配置'" width="900px">
      <WorkflowConfig v-if="configVisible" :workflow-id="currentWorkflow?.id" />
    </el-dialog>

    <!-- 新建/编辑流程对话框 -->
    <el-dialog v-model="formVisible" :title="isEdit ? '编辑流程' : '新建流程'" width="500px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="流程名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入流程名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入流程描述" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="formLoading">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import WorkflowConfig from './WorkflowConfig.vue'

const loading = ref(false)
const workflows = ref([])
const configVisible = ref(false)
const currentWorkflow = ref(null)

const formVisible = ref(false)
const isEdit = ref(false)
const formLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入流程名称', trigger: 'blur' }]
}

const fetchWorkflows = async () => {
  loading.value = true
  try {
    const response = await api.get('/workflow/')
    workflows.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取流程列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  isEdit.value = false
  form.id = null
  form.name = ''
  form.code = ''
  form.description = ''
  form.is_active = true
  formVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.description = row.description
  form.is_active = row.is_active
  formVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      formLoading.value = true
      try {
        if (isEdit.value) {
          await api.put(`/workflow/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/workflow/', form)
          ElMessage.success('创建成功')
        }
        formVisible.value = false
        fetchWorkflows()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || (isEdit.value ? '更新失败' : '创建失败'))
        console.error(error)
      } finally {
        formLoading.value = false
      }
    }
  })
}

const handleConfig = (row) => {
  currentWorkflow.value = row
  configVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该流程吗？', '提示', {
      type: 'warning'
    })
    
    await api.delete(`/workflow/${row.id}/`)
    ElMessage.success('删除成功')
    fetchWorkflows()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchWorkflows()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
