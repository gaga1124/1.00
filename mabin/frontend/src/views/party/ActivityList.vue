<template>
  <div class="party-activity">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>组织生活与团课学习</span>
          <el-button type="primary" @click="handleAdd">记录活动</el-button>
        </div>
      </template>

      <el-table :data="activities" v-loading="loading">
        <el-table-column prop="title" label="活动主题" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="时间" width="180" />
        <el-table-column prop="location" label="地点" />
        <el-table-column prop="participants_count" label="参加人数" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary">查看详情</el-button>
            <el-button link type="success">签到管理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const loading = ref(false)
const activities = ref([])

const getLabel = (type) => {
  const map = {
    'meeting': '组织生活会',
    'class': '团课学习',
    'volunteer': '志愿活动'
  }
  return map[type] || type
}

const fetchActivities = async () => {
  loading.value = true
  try {
    const res = await request.get('/party/activities/')
    activities.value = res.data
  } catch (error) {
    console.error('获取党建活动失败', error)
  } finally {
    loading.value = false
  }
}

onMounted(fetchActivities)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
