<template>
  <el-tag :type="tagType" :effect="effect" :size="size">
    {{ text }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'default' // default, approval, booking, leave, reimbursement
  },
  effect: {
    type: String,
    default: 'light'
  },
  size: {
    type: String,
    default: 'default'
  }
})

const statusMap = {
  default: {
    pending: { type: 'warning', text: '待处理' },
    processing: { type: 'primary', text: '处理中' },
    approved: { type: 'success', text: '已通过' },
    rejected: { type: 'danger', text: '已驳回' },
    cancelled: { type: 'info', text: '已取消' },
    completed: { type: 'success', text: '已完成' }
  },
  approval: {
    pending: { type: 'warning', text: '待审批' },
    approved: { type: 'success', text: '已批准' },
    rejected: { type: 'danger', text: '已驳回' },
    cancelled: { type: 'info', text: '已取消' }
  },
  booking: {
    pending: { type: 'warning', text: '待审批' },
    approved: { type: 'success', text: '已批准' },
    rejected: { type: 'danger', text: '已驳回' },
    cancelled: { type: 'info', text: '已取消' },
    completed: { type: 'success', text: '已完成' }
  },
  leave: {
    pending: { type: 'warning', text: '待审批' },
    approved: { type: 'success', text: '已批准' },
    rejected: { type: 'danger', text: '已驳回' },
    cancelled: { type: 'info', text: '已取消' }
  },
  reimbursement: {
    pending: { type: 'warning', text: '待审批' },
    approved: { type: 'success', text: '已批准' },
    rejected: { type: 'danger', text: '已驳回' },
    cancelled: { type: 'info', text: '已取消' },
    paid: { type: 'success', text: '已支付' }
  }
}

const tagConfig = computed(() => {
  const map = statusMap[props.type] || statusMap.default
  return map[props.status] || { type: 'info', text: props.status }
})

const tagType = computed(() => tagConfig.value.type)
const text = computed(() => tagConfig.value.text)
</script>

<style scoped>
</style>
