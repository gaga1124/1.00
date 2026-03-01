<template>
  <div class="workflow-config">
    <el-card class="flow-preview mb-20" v-if="nodes.length > 0">
      <template #header>
        <div class="card-header">
          <span>流程预览</span>
        </div>
      </template>
      <WorkflowFlowchart :workflow="{ nodes }" />
    </el-card>

    <div class="actions">
      <el-button type="primary" @click="handleAddNode" style="margin-bottom: 20px">添加节点</el-button>
    </div>
    
    <el-table :data="nodes" style="width: 100%">
      <el-table-column prop="name" label="节点名称" />
      <el-table-column prop="order" label="顺序" width="80" />
      <el-table-column prop="approver_type_display" label="审批人类型" width="120" />
      <el-table-column label="审批人/角色" width="150">
        <template #default="scope">
          <span v-if="scope.row.approver_type === 'user'">{{ scope.row.approver_user_name }}</span>
          <span v-else-if="scope.row.approver_type === 'role'">{{ scope.row.approver_role_name }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_parallel" label="会签" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_parallel ? 'success' : 'info'">
            {{ scope.row.is_parallel ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="condition_expression" label="条件" width="150">
        <template #default="scope">
          <el-tag v-if="scope.row.condition_expression" type="warning" size="small">
            {{ scope.row.condition_expression }}
          </el-tag>
          <span v-else class="text-gray">-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 节点编辑对话框 -->
    <el-dialog v-model="nodeDialogVisible" :title="editingNode ? '编辑节点' : '新增节点'" width="600px">
      <el-form :model="nodeForm" label-width="120px">
        <el-form-item label="节点名称">
          <el-input v-model="nodeForm.name" />
        </el-form-item>
        <el-form-item label="顺序">
          <el-input-number v-model="nodeForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="审批人类型">
          <el-select v-model="nodeForm.approver_type">
            <el-option label="指定用户" value="user" />
            <el-option label="指定角色" value="role" />
            <el-option label="部门负责人" value="department_leader" />
            <el-option label="创建人" value="creator" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择用户" v-if="nodeForm.approver_type === 'user'">
           <el-select v-model="nodeForm.approver_user" filterable placeholder="请选择用户" style="width: 100%">
              <el-option v-for="user in users" :key="user.id" :label="user.real_name || user.username" :value="user.id" />
           </el-select>
        </el-form-item>
        <el-form-item label="选择角色" v-if="nodeForm.approver_type === 'role'">
           <el-select v-model="nodeForm.approver_role" placeholder="请选择角色" style="width: 100%">
              <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
           </el-select>
        </el-form-item>
        <el-form-item label="是否并行">
          <el-switch v-model="nodeForm.is_parallel" />
        </el-form-item>
        <el-form-item label="需要审批人数" v-if="nodeForm.is_parallel">
          <el-input-number v-model="nodeForm.required_approvers" :min="1" />
        </el-form-item>
        <el-form-item label="允许驳回">
             <el-switch v-model="nodeForm.allow_reject" />
        </el-form-item>
        <el-form-item label="允许驳回上一步">
             <el-switch v-model="nodeForm.allow_reject_to_previous" />
        </el-form-item>
        <el-divider>条件设置（可选）</el-divider>
        <el-form-item label="预设条件">
          <el-select v-model="conditionTemplate" placeholder="选择预设条件模板" clearable @change="applyConditionTemplate" style="width: 100%">
            <el-option label="无（默认通过）" value="" />
            <el-option label="请假天数 > X 天" value="days_gt" />
            <el-option label="请假天数 >= X 天" value="days_gte" />
            <el-option label="请假天数 <= X 天" value="days_lte" />
            <el-option label="报销金额 > X 元" value="amount_gt" />
            <el-option label="报销金额 >= X 元" value="amount_gte" />
            <el-option label="报销金额 <= X 元" value="amount_lte" />
            <el-option label="按类别判断" value="category" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件表达式" v-if="conditionTemplate || nodeForm.condition_expression">
          <el-input v-model="nodeForm.condition_expression" placeholder="如: days > 3 或 amount >= 10000" />
          <div class="condition-hint">
            <p>可用变量：</p>
            <ul>
              <li><code>days</code> - 请假天数（请假流程）</li>
              <li><code>amount</code> - 报销金额（报销流程）</li>
              <li><code>category</code> - 类别</li>
              <li><code>applicant_role</code> - 申请人角色</li>
            </ul>
            <p>示例：<code>days > 3</code>、<code>amount >= 5000</code>、<code>category == 'travel'</code></p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveNode">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import WorkflowFlowchart from '@/components/WorkflowFlowchart.vue'

const props = defineProps({
  workflowId: {
    type: Number,
    required: true
  }
})

const nodes = ref([])
const users = ref([])
const roles = ref([])
const nodeDialogVisible = ref(false)
const editingNode = ref(null)

const conditionTemplate = ref('')

const nodeForm = reactive({
  name: '',
  order: 0,
  approver_type: 'user',
  approver_user: null,
  approver_role: null,
  is_parallel: false,
  required_approvers: 1,
  allow_reject: true,
  allow_reject_to_previous: true,
  condition_expression: ''
})

const applyConditionTemplate = () => {
  if (!conditionTemplate.value) {
    nodeForm.condition_expression = ''
    return
  }
  
  const templates = {
    'days_gt': 'days > ',
    'days_gte': 'days >= ',
    'days_lte': 'days <= ',
    'amount_gt': 'amount > ',
    'amount_gte': 'amount >= ',
    'amount_lte': 'amount <= ',
    'category': "category == ''"
  }
  
  nodeForm.condition_expression = templates[conditionTemplate.value] || ''
}

const fetchNodes = async () => {
  try {
    const response = await api.get(`/workflow/${props.workflowId}/`)
    nodes.value = response.data.nodes || []
  } catch (error) {
    ElMessage.error('获取节点列表失败')
    console.error(error)
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/')
    users.value = response.data.results || response.data
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

const fetchRoles = async () => {
  try {
    const response = await api.get('/rbac/roles/')
    roles.value = response.data.results || response.data
  } catch (error) {
    console.error('获取角色列表失败', error)
  }
}

const handleAddNode = () => {
  editingNode.value = null
  Object.assign(nodeForm, {
    name: '',
    order: nodes.value.length,
    approver_type: 'user',
    approver_user: null,
    approver_role: null,
    is_parallel: false,
    required_approvers: 1,
    allow_reject: true,
    allow_reject_to_previous: true,
    condition_expression: ''
  })
  conditionTemplate.value = ''
  nodeDialogVisible.value = true
}

const handleEdit = (row) => {
  editingNode.value = row
  Object.assign(nodeForm, {
    name: row.name,
    order: row.order,
    approver_type: row.approver_type,
    approver_user: row.approver_user,
    approver_role: row.approver_role,
    is_parallel: row.is_parallel,
    required_approvers: row.required_approvers,
    allow_reject: row.allow_reject,
    allow_reject_to_previous: row.allow_reject_to_previous,
    condition_expression: row.condition_expression || ''
  })
  
  if (row.condition_expression && row.condition_expression.startsWith('days > ')) {
    conditionTemplate.value = 'days_gt'
  } else if (row.condition_expression && row.condition_expression.startsWith('days >= ')) {
    conditionTemplate.value = 'days_gte'
  } else if (row.condition_expression && row.condition_expression.startsWith('days <= ')) {
    conditionTemplate.value = 'days_lte'
  } else if (row.condition_expression && row.condition_expression.startsWith('amount > ')) {
    conditionTemplate.value = 'amount_gt'
  } else if (row.condition_expression && row.condition_expression.startsWith('amount >= ')) {
    conditionTemplate.value = 'amount_gte'
  } else if (row.condition_expression && row.condition_expression.startsWith('amount <= ')) {
    conditionTemplate.value = 'amount_lte'
  } else if (row.condition_expression && row.condition_expression.startsWith('category')) {
    conditionTemplate.value = 'category'
  } else {
    conditionTemplate.value = ''
  }
  
  nodeDialogVisible.value = true
}

const handleSaveNode = async () => {
  if (nodeForm.approver_type === 'user' && !nodeForm.approver_user) {
    ElMessage.warning('请选择审批用户')
    return
  }
  if (nodeForm.approver_type === 'role' && !nodeForm.approver_role) {
    ElMessage.warning('请选择审批角色')
    return
  }

  try {
    const url = editingNode.value
      ? `/workflow/nodes/${editingNode.value.id}/`
      : `/workflow/nodes/`
    
    const method = editingNode.value ? 'put' : 'post'
    
    // 清理无关数据
    const data = {
      ...nodeForm,
      workflow: props.workflowId
    }
    
    if (data.approver_type !== 'user') data.approver_user = null
    if (data.approver_type !== 'role') data.approver_role = null
    
    await api[method](url, data)
    ElMessage.success('保存成功')
    nodeDialogVisible.value = false
    fetchNodes()
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

const handleDelete = async (row) => {
  try {
    await api.delete(`/workflow/nodes/${row.id}/`)
    ElMessage.success('删除成功')
    fetchNodes()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchNodes()
  fetchUsers()
  fetchRoles()
})
</script>

<style scoped>
.workflow-config {
  padding: 20px;
}

.condition-hint {
  margin-top: 8px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.condition-hint p {
  margin: 4px 0;
}

.condition-hint ul {
  margin: 4px 0;
  padding-left: 20px;
}

.condition-hint code {
  background-color: #e6e8eb;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}

.text-gray {
  color: #909399;
}
</style>
