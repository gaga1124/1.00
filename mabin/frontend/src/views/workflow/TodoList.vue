<template>
  <el-card>
    <template #header>
      <span>待办任务</span>
    </template>
    
    <el-table :data="todos" v-loading="loading" style="width: 100%" class="responsive-table">
      <el-table-column prop="instance.title" label="任务标题" min-width="120" />
      <el-table-column prop="instance.workflow_name" label="流程类型" width="120" class-name="hidden-mobile" />
      <el-table-column prop="node_name" label="当前节点" width="100" />
      <el-table-column prop="instance.applicant_name" label="申请人" width="80" />
      <el-table-column prop="instance.created_at" label="创建时间" width="140" class-name="hidden-mobile" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleApprove(scope.row)">
            处理
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 审批对话框 -->
    <el-dialog v-model="approveVisible" title="审批任务" :width="dialogWidth">
      <div v-if="currentTodo">
        <WorkflowFlowchart 
          :workflow="{ nodes: currentTodo.instance_detail?.workflow_nodes }" 
          :current-instance="currentTodo.instance_detail" 
          style="margin-bottom: 20px"
        />
        
        <el-descriptions :column="isMobile ? 1 : 2" border>
          <el-descriptions-item label="流程">{{ currentTodo.instance.workflow_name }}</el-descriptions-item>
          <el-descriptions-item label="节点">{{ currentTodo.node_name }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ currentTodo.instance.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTodo.instance.created_at }}</el-descriptions-item>
        </el-descriptions>
        
        <el-form :model="approveForm" label-width="80px" style="margin-top: 20px">
          <el-form-item label="操作">
            <el-radio-group v-model="approveForm.action">
              <el-radio label="approve">通过</el-radio>
              <el-radio label="reject" v-if="currentTodo?.allow_reject">驳回</el-radio>
              <el-radio label="reject_to_previous" v-if="currentTodo?.allow_reject_to_previous">驳回至上一步</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="审批意见">
            <el-input v-model="approveForm.comment" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="approveVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitApprove">提交</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import WorkflowFlowchart from '@/components/WorkflowFlowchart.vue'

const loading = ref(false)
const todos = ref([])
const approveVisible = ref(false)
const currentTodo = ref(null)

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value <= 768)
const dialogWidth = computed(() => isMobile.value ? '95%' : '850px')

const updateWidth = () => {
  windowWidth.value = window.innerWidth
}

onMounted(() => {
  window.addEventListener('resize', updateWidth)
  fetchTodos()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWidth)
})

const approveForm = reactive({
  action: 'approve',
  comment: ''
})

const fetchTodos = async () => {
  loading.value = true
  try {
    const response = await api.get('/workflow/instances/my_todos/')
    todos.value = response.data
  } catch (error) {
    ElMessage.error('获取待办任务失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleApprove = (row) => {
  currentTodo.value = row
  approveForm.action = 'approve'
  approveForm.comment = ''
  approveVisible.value = true
}

const handleSubmitApprove = async () => {
  try {
    await api.post(`/workflow/instances/${currentTodo.value.instance.id}/approve/`, approveForm)
    ElMessage.success('审批成功')
    approveVisible.value = false
    fetchTodos()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '审批失败')
    console.error(error)
  }
}

onMounted(() => {
  fetchTodos()
})
</script>

<style scoped>
/* 移动端适配 */
@media (max-width: 768px) {
  :deep(.el-card__body) {
    padding: 10px;
  }
  
  :deep(.hidden-mobile) {
    display: none !important;
  }
  
  :deep(.el-table .cell) {
    padding: 0 5px;
  }
}
</style>
