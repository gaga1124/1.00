<template>
  <div class="employment-stats">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">就业率</div>
          <div class="stat-value">{{ stats.employment_rate }}%</div>
          <el-progress 
            :percentage="stats.employment_rate" 
            :color="customColors" 
            :stroke-width="10"
          />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">平均薪资</div>
          <div class="stat-value">¥{{ stats.avg_salary }}</div>
          <div class="stat-desc">月薪平均水平</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">总人数</div>
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-desc">在籍毕业生总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已签约人数</div>
          <div class="stat-value">{{ employedCount }}</div>
          <div class="stat-desc">完成就业协议签署</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card header="就业去向分析（按行业）">
          <el-table :data="stats.by_industry" style="width: 100%">
            <el-table-column prop="company__industry" label="行业" />
            <el-table-column prop="count" label="人数" width="100" />
            <el-table-column label="占比" width="180">
              <template #default="{ row }">
                <el-progress :percentage="getPercentage(row.count)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="就业来源分析">
          <el-table :data="stats.by_source" style="width: 100%">
            <el-table-column prop="source" label="来源渠道">
              <template #default="{ row }">
                {{ getSourceLabel(row.source) }}
              </template>
            </el-table-column>
            <el-table-column prop="count" label="人数" width="100" />
            <el-table-column label="占比" width="180">
              <template #default="{ row }">
                <el-progress :percentage="getPercentage(row.count)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'

const stats = ref({
  employment_rate: 0,
  avg_salary: 0,
  by_industry: [],
  by_source: []
})

const totalCount = ref(0)
const employedCount = ref(0)

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

const getPercentage = (count) => {
  if (totalCount.value === 0) return 0
  return Math.round((count / totalCount.value) * 100)
}

const getSourceLabel = (source) => {
  const map = {
    'job_fair': '招聘会',
    'online': '网络招聘',
    'recommendation': '推荐',
    'other': '其他'
  }
  return map[source] || source
}

const fetchAnalysis = async () => {
  try {
    const res = await request.get('/career/statistics/analysis/')
    stats.value = res.data
    
    // 获取总数
    const listRes = await request.get('/career/statistics/')
    totalCount.value = listRes.data.count || listRes.data.length
    employedCount.value = Math.round((totalCount.value * stats.value.employment_rate) / 100)
  } catch (error) {
    console.error('获取统计数据失败', error)
    ElMessage.error('获取就业分析数据失败')
  }
}

onMounted(fetchAnalysis)
</script>

<style scoped>
.employment-stats {
  padding: 10px;
}
.stat-card {
  text-align: center;
  height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}
.stat-desc {
  font-size: 12px;
  color: #c0c4cc;
}
.mt-20 {
  margin-top: 20px;
}
</style>