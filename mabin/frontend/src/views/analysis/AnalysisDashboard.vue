<template>
  <div class="analysis-dashboard">
    <el-row :gutter="20">
      <!-- 核心统计指标 -->
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card academic">
          <div class="stat-info">
            <div class="stat-title">平均分</div>
            <div class="stat-value">{{ stats.academic?.avg_score || 0 }}</div>
            <div class="stat-footer">
              <span>全校挂科率: </span>
              <el-tag :type="stats.academic?.fail_rate > 10 ? 'danger' : 'success'">
                {{ stats.academic?.fail_rate || 0 }}%
              </el-tag>
            </div>
          </div>
          <el-icon class="stat-icon"><Reading /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card employment">
          <div class="stat-info">
            <div class="stat-title">平均就业率</div>
            <div class="stat-value">{{ stats.employment?.employment_rate || 0 }}%</div>
            <div class="stat-footer">
              <span>已就业人数: {{ stats.employment?.employed_count || 0 }} / {{ stats.employment?.total_graduates || 0 }}</span>
            </div>
          </div>
          <el-icon class="stat-icon"><Briefcase /></el-icon>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card research">
          <div class="stat-info">
            <div class="stat-title">科研总经费</div>
            <div class="stat-value">¥{{ formatNumber(stats.research?.total_funds || 0) }}</div>
            <div class="stat-footer">
              <span>项目总数: {{ stats.research?.total_projects || 0 }} | 成果数: {{ stats.research?.total_achievements || 0 }}</span>
            </div>
          </div>
          <el-icon class="stat-icon"><Opportunity /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 预警通知 -->
      <el-col :span="12">
        <el-card class="warning-card">
          <template #header>
            <div class="card-header">
              <span>系统预警</span>
              <el-tag type="danger">{{ warnings.length }} 条异常</el-tag>
            </div>
          </template>
          <el-scrollbar height="300px">
            <el-alert
              v-for="(warning, index) in warnings"
              :key="index"
              :title="warning.message"
              :type="warning.level === 'high' ? 'error' : 'warning'"
              show-icon
              :closable="false"
              style="margin-bottom: 10px"
            />
            <el-empty v-if="warnings.length === 0" description="暂无异常预警" />
          </el-scrollbar>
        </el-card>
      </el-col>

      <!-- 决策建议 -->
      <el-col :span="12">
        <el-card class="decision-card">
          <template #header>
            <div class="card-header">
              <span>决策建议</span>
            </div>
          </template>
          <div class="decision-content">
            <h4>热门专业趋势 (基于选课数据)</h4>
            <el-table :data="decisionData.trend_analysis?.hot_majors || []" size="small" border>
              <el-table-column prop="student__major" label="专业名称" />
              <el-table-column prop="selection_count" label="选课人次" width="100" />
              <el-table-column label="热度">
                <template #default="{ row }">
                  <el-progress :percentage="calculatePercentage(row.selection_count)" :show-text="false" />
                </template>
              </el-table-column>
            </el-table>
            <div class="suggestion-box">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ decisionData.trend_analysis?.suggestion || '正在通过历史数据生成建议...' }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表展示区域 (模拟) -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>多维度数据分布</span>
            </div>
          </template>
          <div class="chart-container">
            <!-- 这里通常会放置 ECharts 图表 -->
            <div class="mock-chart">
              <div class="bar-item" v-for="i in 12" :key="i" :style="{ height: Math.random() * 100 + '%' }">
                <span class="label">{{ i }}月</span>
              </div>
            </div>
            <p style="text-align: center; color: #999; margin-top: 20px">年度科研项目与就业率趋势对比图 (模拟可视化)</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const stats = ref({})
const warnings = ref([])
const decisionData = ref({})

const fetchDashboardData = async () => {
  try {
    const [statsRes, warningsRes, decisionRes] = await Promise.all([
      axios.get('/api/analysis/stats/'),
      axios.get('/api/analysis/warnings/'),
      axios.get('/api/analysis/decision/')
    ])
    stats.value = statsRes.data
    warnings.value = warningsRes.data
    decisionData.value = decisionRes.data
  } catch (error) {
    ElMessage.error('获取分析数据失败')
  }
}

const formatNumber = (num) => {
  return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2 })
}

const calculatePercentage = (count) => {
  const max = Math.max(...(decisionData.value.trend_analysis?.hot_majors?.map(m => m.selection_count) || [100]))
  return Math.round((count / max) * 100)
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  color: #fff;
}
.academic { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.employment { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.research { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: #333; }

.stat-info {
  flex: 1;
}
.stat-title {
  font-size: 14px;
  opacity: 0.8;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}
.stat-footer {
  font-size: 12px;
}
.stat-icon {
  font-size: 48px;
  opacity: 0.3;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-box {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f9eb;
  color: #67c23a;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-container {
  height: 350px;
}
.mock-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  border-bottom: 2px solid #eee;
  padding: 0 20px;
}
.bar-item {
  width: 30px;
  background-color: #409EFF;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: height 0.3s;
}
.bar-item:hover {
  background-color: #66b1ff;
}
.bar-item .label {
  position: absolute;
  bottom: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}
</style>
