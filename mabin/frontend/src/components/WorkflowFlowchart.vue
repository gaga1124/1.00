<template>
  <div class="flowchart-container">
    <svg :width="svgWidth" :height="svgHeight" class="flowchart-svg">
      <!-- 定义箭头 -->
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#909399" />
        </marker>
      </defs>

      <g v-for="(node, index) in nodes" :key="node.id">
        <!-- 节点连线 -->
        <line
          v-if="index < nodes.length - 1"
          :x1="getNodeX(index) + nodeWidth"
          :y1="getNodeY(index) + nodeHeight / 2"
          :x2="getNodeX(index + 1) - 10"
          :y2="getNodeY(index + 1) + nodeHeight / 2"
          stroke="#909399"
          stroke-width="2"
          marker-end="url(#arrowhead)"
        />

        <!-- 节点矩形 -->
        <rect
          :x="getNodeX(index)"
          :y="getNodeY(index)"
          :width="nodeWidth"
          :height="nodeHeight"
          rx="8"
          ry="8"
          :class="['node-rect', getNodeStatusClass(node)]"
        />

        <!-- 节点文字 -->
        <text
          :x="getNodeX(index) + nodeWidth / 2"
          :y="getNodeY(index) + 25"
          text-anchor="middle"
          class="node-name"
        >
          {{ node.name }}
        </text>
        <text
          :x="getNodeX(index) + nodeWidth / 2"
          :y="getNodeY(index) + 45"
          text-anchor="middle"
          class="node-type"
        >
          {{ node.approver_type_display }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  workflow: {
    type: Object,
    required: true
  },
  currentInstance: {
    type: Object,
    default: null
  }
})

const nodes = computed(() => props.workflow.nodes || [])
const nodeWidth = 140
const nodeHeight = 60
const horizontalGap = 60
const verticalGap = 40
const padding = 40

const svgWidth = computed(() => {
  return nodes.value.length * (nodeWidth + horizontalGap) + padding * 2
})

const svgHeight = computed(() => {
  return nodeHeight + padding * 2
})

const getNodeX = (index) => {
  return padding + index * (nodeWidth + horizontalGap)
}

const getNodeY = (index) => {
  return padding
}

const getNodeStatusClass = (node) => {
  if (!props.currentInstance) return 'status-default'
  
  const records = props.currentInstance.node_records || []
  const record = records.find(r => r.node === node.id)
  
  if (record) {
    if (record.status === 'approved') return 'status-approved'
    if (record.status === 'rejected') return 'status-rejected'
    if (record.status === 'pending') return 'status-pending'
  }
  
  if (props.currentInstance.current_node === node.id) {
    return 'status-current'
  }
  
  return 'status-default'
}
</script>

<style scoped>
.flowchart-container {
  width: 100%;
  overflow-x: auto;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
}
.flowchart-svg {
  display: block;
  margin: 0 auto;
}
.node-rect {
  fill: #fff;
  stroke: #dcdfe6;
  stroke-width: 2;
  transition: all 0.3s;
}
.node-name {
  font-size: 14px;
  font-weight: bold;
  fill: #303133;
}
.node-type {
  font-size: 12px;
  fill: #909399;
}

/* 状态样式 */
.status-approved {
  fill: #f0f9eb;
  stroke: #67c23a;
}
.status-rejected {
  fill: #fef0f0;
  stroke: #f56c6c;
}
.status-pending {
  fill: #fdf6ec;
  stroke: #e6a23c;
}
.status-current {
  stroke: #409eff;
  stroke-width: 3;
  stroke-dasharray: 5, 5;
  animation: dash 10s linear infinite;
}
.status-default {
  fill: #fff;
  stroke: #dcdfe6;
}

@keyframes dash {
  to {
    stroke-dashoffset: 100;
  }
}
</style>
