<template>
  <div class="workflow-steps">
    <el-steps :active="activeStep" align-center finish-status="success">
      <el-step v-for="(node, index) in steps" :key="node.id" :title="node.name">
        <template #description>
          <div class="step-description">
            <div v-if="getApprover(node)" class="approver">
              审批人: {{ getApprover(node) }}
            </div>
            <div v-if="getRecord(node)" class="status">
              <span :class="'status-' + getRecord(node).status">
                {{ getRecord(node).status_display }}
              </span>
            </div>
            <div v-if="getRecord(node)?.approval_time" class="time">
              {{ formatTime(getRecord(node).approval_time) }}
            </div>
          </div>
        </template>
      </el-step>
    </el-steps>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  instance: {
    type: Object,
    required: true
  }
})

const steps = computed(() => {
  return props.instance.workflow_nodes || []
})

const activeStep = computed(() => {
  if (props.instance.status === 'approved') return steps.value.length
  if (props.instance.status === 'rejected') {
     // 找到第一个被拒绝的节点记录对应的索引
     const rejectedNodeId = props.instance.node_records?.find(r => r.status === 'rejected')?.node
     if (rejectedNodeId) {
       return steps.value.findIndex(n => n.id === rejectedNodeId)
     }
  }
  
  const currentNodeId = props.instance.current_node
  if (!currentNodeId) return 0
  return steps.value.findIndex(n => n.id === currentNodeId)
})

const getApprover = (node) => {
  const record = getRecord(node)
  if (record?.approver_name) return record.approver_name
  if (node.approver_type === 'user') return node.approver_user_name
  if (node.approver_type === 'role') return node.approver_role_name
  return node.approver_type_display
}

const getRecord = (node) => {
  return props.instance.node_records?.find(r => r.node === node.id)
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.workflow-steps {
  padding: 20px 0;
  margin-bottom: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}
.step-description {
  font-size: 12px;
  line-height: 1.4;
  margin-top: 4px;
}
.status-approved { color: #67c23a; }
.status-rejected { color: #f56c6c; }
.status-pending { color: #e6a23c; }
.time { color: #909399; margin-top: 2px; }
</style>
