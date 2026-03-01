<template>
  <div class="repair-detail" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报修标题">{{ repair.title }}</el-descriptions-item>
          <el-descriptions-item label="报修分类">{{ repair.category_name }}</el-descriptions-item>
          <el-descriptions-item label="报修地点">{{ repair.location }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(repair.priority)">{{ repair.priority_display }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <StatusTag :status="repair.status" type="default" />
          </el-descriptions-item>
          <el-descriptions-item label="申请人">{{ repair.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="处理人">{{ repair.handler_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ repair.contact_phone }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(repair.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="受理时间">
            {{ repair.accepted_at ? formatDateTime(repair.accepted_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ repair.completed_at ? formatDateTime(repair.completed_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="评分" v-if="repair.rating">
            <el-rate :model-value="repair.rating" disabled />
          </el-descriptions-item>
        </el-descriptions>
        
        <el-card class="detail-card" style="margin-top: 20px">
          <template #header>详细描述</template>
          <p>{{ repair.description }}</p>
        </el-card>
        
        <el-card class="detail-card" v-if="repair.images && repair.images.length > 0">
          <template #header>现场图片</template>
          <div class="image-gallery">
            <el-image
              v-for="(img, index) in repair.images"
              :key="index"
              :src="img.url"
              :preview-src-list="repair.images.map(i => i.url)"
              fit="cover"
              class="gallery-image"
            />
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="处理记录" name="records">
        <el-timeline>
          <el-timeline-item
            v-for="record in records"
            :key="record.id"
            :timestamp="formatDateTime(record.created_at)"
            placement="top"
          >
            <el-card>
              <h4>{{ record.action }}</h4>
              <p>操作人：{{ record.operator_name }}</p>
              <p v-if="record.comment">备注：{{ record.comment }}</p>
              <div v-if="record.images && record.images.length > 0" class="record-images">
                <el-image
                  v-for="(img, index) in record.images"
                  :key="index"
                  :src="img.url"
                  fit="cover"
                  class="record-image"
                />
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-tab-pane>
      
      <el-tab-pane label="处理意见" name="comments" v-if="repair.handler_comment || repair.applicant_comment">
        <el-card v-if="repair.handler_comment">
          <template #header>处理人意见</template>
          <p>{{ repair.handler_comment }}</p>
        </el-card>
        <el-card v-if="repair.applicant_comment" style="margin-top: 20px">
          <template #header>申请人评价</template>
          <div v-if="repair.rating">
            <el-rate :model-value="repair.rating" disabled />
          </div>
          <p style="margin-top: 10px">{{ repair.applicant_comment }}</p>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 操作按钮 -->
    <div class="action-buttons" v-if="canOperate">
      <el-button
        v-if="repair.status === 'pending' && isHandler"
        type="primary"
        @click="handleAccept"
      >
        受理
      </el-button>
      <el-button
        v-if="repair.status === 'accepted' && isHandler"
        type="primary"
        @click="handleStartProcessing"
      >
        开始处理
      </el-button>
      <el-button
        v-if="repair.status === 'processing' && isHandler"
        type="success"
        @click="handleComplete"
      >
        完成
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { formatDateTime } from '@/utils/format'
import StatusTag from '@/components/StatusTag.vue'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  repairId: {
    type: Number,
    required: true
  }
})

const userStore = useUserStore()
const loading = ref(false)
const activeTab = ref('info')
const repair = ref({})
const records = ref([])

const isHandler = computed(() => {
  // 以后端计算好的 can_handle 为准，避免前端判断角色细节
  return !!repair.value?.can_handle
})

const canOperate = computed(() => {
  return isHandler.value && ['pending', 'accepted', 'processing'].includes(repair.value.status)
})

const fetchRepairDetail = async () => {
  loading.value = true
  try {
    const response = await api.get(`/repair/applications/${props.repairId}/`)
    repair.value = response.data
    records.value = response.data.records || []
  } catch (error) {
    ElMessage.error('获取报修详情失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleAccept = async () => {
  try {
    await api.post(`/repair/applications/${props.repairId}/accept/`)
    ElMessage.success('受理成功')
    fetchRepairDetail()
  } catch (error) {
    ElMessage.error('受理失败')
    console.error(error)
  }
}

const handleStartProcessing = async () => {
  try {
    await api.post(`/repair/applications/${props.repairId}/start_processing/`)
    ElMessage.success('已开始处理')
    fetchRepairDetail()
  } catch (error) {
    ElMessage.error('操作失败')
    console.error(error)
  }
}

const handleComplete = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入处理意见', '完成报修', {
      inputType: 'textarea',
      inputPlaceholder: '请描述处理过程和结果'
    })
    
    await api.post(`/repair/applications/${props.repairId}/complete/`, {
      comment: value
    })
    ElMessage.success('报修已完成')
    fetchRepairDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

const getPriorityType = (priority) => {
  const map = {
    'low': 'info',
    'medium': '',
    'high': 'warning',
    'urgent': 'danger'
  }
  return map[priority] || ''
}

watch(() => props.repairId, () => {
  if (props.repairId) {
    fetchRepairDetail()
  }
})

onMounted(() => {
  if (props.repairId) {
    fetchRepairDetail()
  }
})
</script>

<style scoped>
.repair-detail {
  padding: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.gallery-image {
  width: 150px;
  height: 150px;
  border-radius: 4px;
  cursor: pointer;
}

.record-images {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.record-image {
  width: 100px;
  height: 100px;
  border-radius: 4px;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}
</style>
