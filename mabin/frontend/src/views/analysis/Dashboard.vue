<template>
  <div class="analysis-dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">{{ stat.title }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-desc">{{ stat.desc }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card title="挂科预警">
          <template #header>
            <div class="card-header">
              <span>挂科预警 (及格率 < 70%)</span>
              <el-tag type="danger">高风险</el-tag>
            </div>
          </template>
          <el-table :data="warnings.failed_courses">
            <el-table-column prop="course_name" label="课程" />
            <el-table-column prop="fail_rate" label="不及格率">
              <template #default="{ row }">
                {{ (row.fail_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="student_count" label="人数" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card title="经费预警">
          <template #header>
            <div class="card-header">
              <span>科研经费预警 (使用率 > 90%)</span>
              <el-tag type="warning">关注</el-tag>
            </div>
          </template>
          <el-table :data="warnings.budget_overruns">
            <el-table-column prop="project_name" label="项目" />
            <el-table-column prop="usage_rate" label="使用率">
              <template #default="{ row }">
                {{ (row.usage_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="remaining" label="余额" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const stats = ref([
  { title: '在校学生总数', value: '1,240', desc: '较上学期 +2.4%' },
  { title: '平均学分绩点', value: '3.42', desc: '全院平均水平' },
  { title: '当前就业率', value: '82.5%', desc: '2025届毕业生' },
  { title: '科研经费总额', value: '¥4.2M', desc: '年度累计' }
])

const warnings = ref({
  failed_courses: [],
  budget_overruns: []
})

const fetchDashboardData = async () => {
  try {
    const res = await request.get('/analysis/dashboard/stats/')
    // stats.value = res.data.stats // Assuming the API returns stats
    
    const warnRes = await request.get('/analysis/warnings/')
    warnings.value = warnRes.data
  } catch (error) {
    console.error('获取分析数据失败', error)
  }
}

onMounted(fetchDashboardData)
</script>

<style scoped>
.analysis-dashboard {
  padding: 10px;
}
.stat-card {
  text-align: center;
}
.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}
.stat-desc {
  font-size: 12px;
  color: #67c23a;
}
.mt-20 {
  margin-top: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
