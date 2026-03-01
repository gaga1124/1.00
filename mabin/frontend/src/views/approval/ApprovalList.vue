<template>
  <el-card class="approval-card">
    <template #header>
      <div class="card-header">
        <span>审批管理</span>
        <div class="header-actions">
          <el-button type="primary" size="small" @click="handleCreateLeave">请假申请</el-button>
          <el-button type="success" size="small" @click="handleCreateReimbursement">财务报销</el-button>
          <el-button type="warning" size="small" v-if="userStore.user?.role === 'student'" @click="handleCreateParty">入党/入团申请</el-button>
        </div>
      </div>
    </template>
    
    <el-tabs v-model="activeTab" class="demo-tabs">
      <el-tab-pane label="请假申请" name="leave">
        <div class="sub-tabs">
          <el-radio-group v-model="activeSubTab" size="small">
            <el-radio-button label="pending">待审批</el-radio-button>
            <el-radio-button label="my">我发起的</el-radio-button>
            <el-radio-button label="cc">抄送我的</el-radio-button>
          </el-radio-group>
        </div>

        <el-table :data="currentList" v-loading="loading" style="width: 100%" class="responsive-table">
          <el-table-column prop="title" label="标题" min-width="120" />
          <el-table-column label="申请人" width="100">
            <template #default="scope">
              {{ scope.row.applicant_name }}
            </template>
          </el-table-column>
          <el-table-column prop="leave_type_display" label="类型" width="80" class-name="hidden-mobile" />
          <el-table-column prop="start_time" label="开始时间" width="140" class-name="hidden-mobile">
            <template #default="scope">{{ scope.row.start_time?.substring(0, 16) }}</template>
          </el-table-column>
          <el-table-column prop="days" label="天数" width="60" />
          <el-table-column prop="status_display" label="状态" width="80">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column v-if="activeSubTab === 'cc'" label="阅读状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.cc_info?.find(c => c.user_id === userStore.user?.id)?.is_read" type="success" size="small">已阅</el-tag>
              <el-tag v-else type="info" size="small">未阅</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button 
                v-if="activeSubTab === 'pending'" 
                type="primary" 
                size="small" 
                @click="handleApprove(scope.row, 'leave')"
              >
                审批
              </el-button>
              <el-button
                v-if="activeSubTab === 'my' && scope.row.status === 'pending'"
                type="danger"
                size="small"
                @click="handleCancel(scope.row, 'leave')"
              >
                撤回
              </el-button>
              <el-button 
                v-if="activeSubTab === 'cc' && !scope.row.cc_info?.find(c => c.user_id === userStore.user?.id)?.is_read" 
                type="success" 
                size="small" 
                @click="handleMarkRead(scope.row, 'leave')"
              >
                已阅
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="财务报销" name="reimbursement">
        <div class="sub-tabs">
          <el-radio-group v-model="activeSubTab" size="small">
            <el-radio-button label="pending">待审批</el-radio-button>
            <el-radio-button label="my">我发起的</el-radio-button>
            <el-radio-button label="cc">抄送我的</el-radio-button>
          </el-radio-group>
        </div>

        <el-table :data="currentList" v-loading="loading" style="width: 100%">
          <el-table-column prop="title" label="标题" min-width="150" />
          <el-table-column label="申请人" width="120">
             <template #default="scope">
              {{ scope.row.applicant_name }}
            </template>
          </el-table-column>
          <el-table-column prop="category_display" label="类别" width="100" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="scope">
              ¥{{ scope.row.amount }}
            </template>
          </el-table-column>
          <el-table-column prop="status_display" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status_display }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column v-if="activeSubTab === 'cc'" label="阅读状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.cc_info?.find(c => c.user_id === userStore.user?.id)?.is_read" type="success" size="small">已阅</el-tag>
              <el-tag v-else type="info" size="small">未阅</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button 
                v-if="activeSubTab === 'pending'" 
                type="primary" 
                size="small" 
                @click="handleApprove(scope.row, 'reimbursement')"
              >
                审批
              </el-button>
              <el-button
                v-if="activeSubTab === 'my' && scope.row.status === 'pending'"
                type="danger"
                size="small"
                @click="handleCancel(scope.row, 'reimbursement')"
              >
                撤回
              </el-button>
               <el-button 
                v-if="activeSubTab === 'cc' && !scope.row.cc_info?.find(c => c.user_id === userStore.user?.id)?.is_read" 
                type="success" 
                size="small" 
                @click="handleMarkRead(scope.row, 'reimbursement')"
              >
                已阅
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="入党/入团" name="party">
        <div class="sub-tabs">
          <el-radio-group v-model="activeSubTab" size="small">
            <el-radio-button label="pending">待审批</el-radio-button>
            <el-radio-button label="my">我发起的</el-radio-button>
          </el-radio-group>
        </div>

        <el-table :data="currentList" v-loading="loading" style="width: 100%">
          <el-table-column label="学生姓名" width="120">
             <template #default="scope">
              {{ scope.row.student_info?.real_name }}
            </template>
          </el-table-column>
          <el-table-column prop="application_type_display" label="申请类型" width="120" />
          <el-table-column prop="current_step" label="当前步骤" min-width="150" />
          <el-table-column prop="status_display" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ scope.row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="申请时间" width="160">
            <template #default="scope">{{ scope.row.created_at?.substring(0, 16) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button 
                v-if="activeSubTab === 'pending'" 
                type="primary" 
                size="small" 
                @click="handleApprove(scope.row, 'party-applications')"
              >
                审批
              </el-button>
              <el-button
                v-if="activeSubTab === 'my' && scope.row.status === 'pending'"
                type="danger"
                size="small"
                @click="handleCancel(scope.row, 'party-applications')"
              >
                撤回
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 审批对话框 -->
    <el-dialog v-model="approveVisible" :title="`审批申请 - ${currentApplication?.title || currentApplication?.application_type_display || ''}`" width="850px">
      <div v-if="currentApplication">
        <WorkflowFlowchart 
          v-if="currentApplication.workflow_instance" 
          :workflow="{ nodes: currentApplication.workflow_instance.workflow_nodes }" 
          :current-instance="currentApplication.workflow_instance"
          style="margin-bottom: 20px"
        />
        
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="申请人">{{ currentApplication.applicant_name || currentApplication.student_info?.real_name }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ currentApplication.created_at?.substring(0, 16) }}</el-descriptions-item>
          <el-descriptions-item label="类型" v-if="approveType === 'leave'">{{ currentApplication.leave_type_display }}</el-descriptions-item>
          <el-descriptions-item label="天数" v-if="approveType === 'leave'">{{ currentApplication.days }}</el-descriptions-item>
          <el-descriptions-item label="金额" v-if="approveType === 'reimbursement'">¥{{ currentApplication.amount }}</el-descriptions-item>
          <el-descriptions-item label="类别" v-if="approveType === 'reimbursement'">{{ currentApplication.category_display }}</el-descriptions-item>
          <el-descriptions-item label="原因" :span="2">{{ currentApplication.reason }}</el-descriptions-item>
        </el-descriptions>

        <el-form :model="approveForm" label-width="100px">
          <el-form-item label="操作">
            <el-radio-group v-model="approveForm.action">
              <el-radio label="approve">通过</el-radio>
              <el-radio label="reject">驳回</el-radio>
              <el-radio label="reject_to_previous" v-if="currentApplication.workflow_instance?.current_node_detail?.allow_reject_to_previous">驳回至上一步</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="审批意见">
            <el-input v-model="approveForm.comment" type="textarea" :rows="4" />
          </el-form-item>
          <el-form-item label="下一步骤" v-if="approveType === 'party-applications' && approveForm.action === 'approve'">
            <el-input v-model="approveForm.next_step" placeholder="例如：入党积极分子、预备党员" />
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { useRoute } from 'vue-router'
import WorkflowFlowchart from '@/components/WorkflowFlowchart.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const activeTab = ref('leave')
const activeSubTab = ref('pending') // pending, my, cc

const leaveApplications = ref([])
const reimbursements = ref([])
const partyApplications = ref([])
const approveVisible = ref(false)
const currentApplication = ref(null)
const approveType = ref('')

const approveForm = reactive({
  action: 'approve',
  comment: '',
  next_step: '' // For party applications
})

// Computed lists for Leave
const pendingLeaves = computed(() => {
  return leaveApplications.value.filter(item => 
    item.approver === userStore.user?.id && item.status === 'pending'
  )
})
const myLeaves = computed(() => {
  return leaveApplications.value.filter(item => item.applicant === userStore.user?.id)
})
const ccLeaves = computed(() => {
  return leaveApplications.value.filter(item => {
    // Check if I am in cc_info
    return item.cc_info && item.cc_info.some(cc => cc.user_id === userStore.user?.id)
  })
})

// Computed lists for Reimbursement
const pendingReimbursements = computed(() => {
  return reimbursements.value.filter(item => 
    item.approver === userStore.user?.id && item.status === 'pending'
  )
})
const myReimbursements = computed(() => {
  return reimbursements.value.filter(item => item.applicant === userStore.user?.id)
})
const ccReimbursements = computed(() => {
  return reimbursements.value.filter(item => {
    return item.cc_info && item.cc_info.some(cc => cc.user_id === userStore.user?.id)
  })
})

// Computed lists for Party
const pendingParty = computed(() => {
  return partyApplications.value.filter(item => 
    item.approver === userStore.user?.id && item.status === 'pending'
  )
})
const myParty = computed(() => {
  return partyApplications.value.filter(item => item.student_info?.user?.id === userStore.user?.id)
})

const currentList = computed(() => {
  if (activeTab.value === 'leave') {
    if (activeSubTab.value === 'pending') return pendingLeaves.value
    if (activeSubTab.value === 'my') return myLeaves.value
    if (activeSubTab.value === 'cc') return ccLeaves.value
  } else if (activeTab.value === 'reimbursement') {
    if (activeSubTab.value === 'pending') return pendingReimbursements.value
    if (activeSubTab.value === 'my') return myReimbursements.value
    if (activeSubTab.value === 'cc') return ccReimbursements.value
  } else if (activeTab.value === 'party') {
    if (activeSubTab.value === 'pending') return pendingParty.value
    if (activeSubTab.value === 'my') return myParty.value
  }
  return []
})

const fetchLeaveApplications = async () => {
  loading.value = true
  try {
    const response = await api.get('/approval/leave/')
    leaveApplications.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取请假申请失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchReimbursements = async () => {
  loading.value = true
  try {
    const response = await api.get('/approval/reimbursement/')
    reimbursements.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取报销申请失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchPartyApplications = async () => {
  loading.value = true
  try {
    const response = await api.get('/approval/party-applications/')
    partyApplications.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取入党申请失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCreateLeave = () => {
  router.push('/approval/leave/create')
}

const handleCreateReimbursement = () => {
  router.push('/approval/reimbursement/create')
}

const handleCreateParty = () => {
  router.push('/approval/party/create')
}

const handleApprove = (row, type) => {
  currentApplication.value = row
  approveType.value = type
  approveForm.action = 'approve'
  approveForm.comment = ''
  approveForm.next_step = ''
  approveVisible.value = true
}

const handleMarkRead = async (row, type) => {
  try {
    await api.post(`/approval/${type}/${row.id}/mark_cc_read/`)
    ElMessage.success('已标记为已阅')
    // Refresh list locally
    const myCC = row.cc_info.find(cc => cc.user_id === userStore.user?.id)
    if (myCC) myCC.is_read = true
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  }
}

const handleSubmitApprove = async () => {
  try {
    const url = `/approval/${approveType.value}/${currentApplication.value.id}/approve/`
    await api.post(url, approveForm)
    ElMessage.success('审批成功')
    approveVisible.value = false
    
    if (approveType.value === 'leave') {
      fetchLeaveApplications()
    } else if (approveType.value === 'reimbursement') {
      fetchReimbursements()
    } else {
      fetchPartyApplications()
    }
    // 通知首页刷新统计
    window.dispatchEvent(new CustomEvent('approval:changed', { detail: { type: approveType.value, action: approveForm.action } }))
  } catch (error) {
    ElMessage.error('审批失败')
    console.error(error)
  }
}

const handleCancel = async (row, type) => {
  try {
    await api.post(`/approval/${type}/${row.id}/cancel/`)
    ElMessage.success('已撤回')
    if (type === 'leave') {
      fetchLeaveApplications()
    } else if (type === 'reimbursement') {
      fetchReimbursements()
    } else {
      fetchPartyApplications()
    }
    // 通知首页刷新统计
    window.dispatchEvent(new CustomEvent('approval:changed', { detail: { type, action: 'cancel' } }))
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '撤回失败')
    console.error(error)
  }
}

const getStatusType = (status) => {
  const map = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'cancelled': 'info'
  }
  return map[status] || 'info'
}

watch(activeTab, (newTab) => {
  if (newTab === 'leave' && leaveApplications.value.length === 0) {
    fetchLeaveApplications()
  } else if (newTab === 'reimbursement' && reimbursements.value.length === 0) {
    fetchReimbursements()
  } else if (newTab === 'party' && partyApplications.value.length === 0) {
    fetchPartyApplications()
  }
})

onMounted(() => {
  // 根据URL参数设置默认子标签
  const sub = route.query.sub
  if (sub && ['pending', 'my', 'cc'].includes(sub)) {
    activeSubTab.value = sub
  }
  fetchLeaveApplications()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.sub-tabs {
  margin-bottom: 20px;
}

/* 移动端适配样式 */
@media (max-width: 768px) {
  .approval-card :deep(.el-card__body) {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .header-actions .el-button {
    margin-left: 0 !important;
    margin-right: 10px;
    margin-bottom: 5px;
  }
  
  .sub-tabs {
    overflow-x: auto;
    white-space: nowrap;
    margin-bottom: 10px;
  }
  
  /* 隐藏非关键列 */
  :deep(.hidden-mobile) {
    display: none !important;
  }
  
  /* 调整表格内边距 */
  :deep(.el-table .cell) {
    padding: 0 5px;
  }
}
</style>
