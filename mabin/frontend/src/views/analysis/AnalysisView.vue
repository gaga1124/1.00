<template>
  <div class="analysis-view">
    <!-- 统计看板 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card academic">
          <template #header>教学质量</template>
          <div class="stat-body">
            <div class="stat-item">
              <span class="label">全校平均分</span>
              <span class="value">{{ stats.academic?.avg_score }}</span>
            </div>
            <div class="stat-item">
              <span class="label">挂科率</span>
              <span class="value warning">{{ stats.academic?.fail_rate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card career">
          <template #header>就业服务</template>
          <div class="stat-body">
            <div class="stat-item">
              <span class="label">毕业生总数</span>
              <span class="value">{{ stats.employment?.total_graduates }}</span>
            </div>
            <div class="stat-item">
              <span class="label">就业率</span>
              <span class="value success">{{ stats.employment?.employment_rate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card research">
          <template #header>科研成果</template>
          <div class="stat-body">
            <div class="stat-item">
              <span class="label">科研项目数</span>
              <span class="value">{{ stats.research?.total_projects }}</span>
            </div>
            <div class="stat-item">
              <span class="label">总经费</span>
              <span class="value">¥{{ formatMoney(stats.research?.total_funds) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 预警与决策建议 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card header="系统预警">
          <el-empty v-if="warnings.length === 0" description="暂无预警信息" />
          <el-alert
            v-for="(w, index) in warnings"
            :key="index"
            :title="w.message"
            :type="w.level === 'high' ? 'error' : 'warning'"
            show-icon
            style="margin-bottom: 10px"
          />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="决策建议">
          <div v-if="decision.trend_analysis" class="decision-content">
            <h4>热门专业预测：</h4>
            <el-tag 
              v-for="item in decision.trend_analysis.hot_majors" 
              :key="item.student__major"
              style="margin-right: 10px; margin-bottom: 10px"
            >
              {{ item.student__major }} ({{ item.selection_count }}人选课)
            </el-tag>
            <p class="suggestion">
              <el-icon><InfoFilled /></el-icon>
              {{ decision.trend_analysis.suggestion }}
            </p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { InfoFilled } from '@element-plus/icons-vue'

const stats = ref({})
const warnings = ref([])
const decision = ref({})

const fetchStats = async () => {
  const res = await request.get('/analysis/stats/')
  stats.value = res.data
}

const fetchWarnings = async () => {
  const res = await request.get('/analysis/warnings/')
  warnings.value = res.data
}

const fetchDecision = async () => {
  const res = await request.get('/analysis/decision/')
  decision.value = res.data
}

const formatMoney = (val) => {
  if (!val) return '0.00'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

onMounted(() => {
  fetchStats()
  fetchWarnings()
  fetchDecision()
})
</script>

<style scoped>
.stat-card :deep(.el-card__header) {
  font-weight: bold;
}
.stat-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stat-item .label {
  color: #909399;
  font-size: 14px;
}
.stat-item .value {
  font-size: 24px;
  font-weight: bold;
}
.value.warning { color: #f56c6c; }
.value.success { color: #67c23a; }

.decision-content h4 {
  margin-top: 0;
  margin-bottom: 15px;
}
.suggestion {
  margin-top: 20px;
  padding: 15px;
  background-color: #f4f4f5;
  border-radius: 4px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
