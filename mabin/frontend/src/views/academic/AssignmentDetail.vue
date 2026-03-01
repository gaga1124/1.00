<template>
  <div class="assignment-detail-container">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="title">{{ assignment.title || '作业详情' }}</span>
      </template>
      <template #extra>
        <el-tag :type="getStatusType(studentStatus)" size="large" effect="dark">
          {{ getStatusText(studentStatus) }}
        </el-tag>
      </template>
    </el-page-header>

    <div class="main-content" v-loading="loading">
      <el-row :gutter="20">
        <!-- 左侧：详情与要求 -->
        <el-col :span="16">
          <el-card class="detail-card">
            <div class="section-title">作业要求</div>
            <div class="description-content">{{ assignment.description || '无描述' }}</div>
            
            <template v-if="assignment.file">
              <div class="section-title">附件材料</div>
              <div class="attachment-item">
                <el-icon><Document /></el-icon>
                <a :href="assignment.file" target="_blank" class="download-link">下载作业附件</a>
              </div>
            </template>
          </el-card>

          <!-- 提交区域 -->
          <el-card class="submission-card">
            <div class="section-title">我的提交</div>
            
            <!-- 已提交展示 -->
            <div v-if="submission" class="submission-view">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="提交时间">
                  {{ formatDateTime(submission.submitted_at) }}
                  <el-tag v-if="submission.is_late" type="warning" size="small" style="margin-left: 10px">逾期提交</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="作业内容">
                  <div class="content-text">{{ submission.content }}</div>
                </el-descriptions-item>
                <el-descriptions-item label="附件" v-if="submission.file">
                  <a :href="submission.file" target="_blank" class="download-link">
                    <el-icon><Download /></el-icon> 查看提交附件
                  </a>
                </el-descriptions-item>
              </el-descriptions>

              <!-- 评分展示 -->
              <div v-if="submission.status === 'graded'" class="grade-section">
                <el-divider content-position="left">教师评分</el-divider>
                <div class="grade-info">
                  <div class="score-display">
                    <span class="label">得分：</span>
                    <span class="score-num">{{ submission.score }}</span>
                  </div>
                  <div class="feedback-display">
                    <span class="label">评语：</span>
                    <span class="feedback-text">{{ submission.feedback || '无评语' }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="waiting-grade">
                <el-empty :image-size="60" description="作业已提交，等待老师评分..." />
              </div>
            </div>
            
            <!-- 提交表单 -->
            <div v-else-if="canSubmit" class="submission-form">
              <el-alert v-if="isOverdue" title="当前已逾期，若提交将被标记为逾期提交" type="warning" show-icon :closable="false" style="margin-bottom: 20px" />
              
              <el-form :model="form" label-position="top">
                <el-form-item label="回答内容">
                  <el-input 
                    v-model="form.content" 
                    type="textarea" 
                    :rows="8" 
                    placeholder="请在这里输入你的作业回答..." 
                  />
                </el-form-item>
                <el-form-item label="附件上传">
                  <el-upload
                    class="upload-demo"
                    drag
                    action="#"
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :limit="1"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      将文件拖到此处，或<em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        单个文件不超过 20MB
                      </div>
                    </template>
                  </el-upload>
                </el-form-item>
                <div class="form-ops">
                  <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
                    确认提交作业
                  </el-button>
                </div>
              </el-form>
            </div>
            
            <!-- 不可提交提示 -->
            <div v-else class="unavailable-tips">
              <el-empty description="当前不在提交时间内或已错过截止日期" />
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：概览与统计 -->
        <el-col :span="8">
          <el-card class="info-card">
            <div class="section-title">作业概览</div>
            <div class="meta-list">
              <div class="meta-item">
                <span class="label">所属课程</span>
                <span class="value">{{ assignment.course_name }}</span>
              </div>
              <div class="meta-item">
                <span class="label">截止日期</span>
                <span class="value" :class="{ 'text-danger': isOverdue }">
                  {{ formatDateTime(assignment.deadline) }}
                </span>
              </div>
              <div class="meta-item">
                <span class="label">逾期政策</span>
                <span class="value">
                  <el-tag :type="assignment.allow_late_submission ? 'warning' : 'danger'" size="small">
                    {{ assignment.allow_late_submission ? `允许补交 (-${assignment.late_penalty}%)` : '不允许补交' }}
                  </el-tag>
                </span>
              </div>
            </div>
          </el-card>

          <el-card class="submission-stats" v-if="isStaff">
            <div class="section-title">提交统计</div>
            <div class="stats-content">
              <el-progress 
                type="circle" 
                :percentage="Math.round((assignment.submission_count / assignment.total_students) * 100) || 0" 
              />
              <div class="stats-text">
                <div class="num">{{ assignment.submission_count }} / {{ assignment.total_students }}</div>
                <div class="label">已提交人数</div>
              </div>
            </div>
            <div class="stats-ops">
              <el-button type="primary" plain style="width: 100%" @click="goSubmissions">
                管理所有提交
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, Download, UploadFilled } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const assignmentId = route.params.id

const isStaff = computed(() => ['admin', 'teacher'].includes(userStore.user?.role))

const loading = ref(false)
const submitting = ref(false)
const assignment = ref({})
const submission = ref(null)

const form = reactive({
  content: '',
  file: null
})

const formatDateTime = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await request.get(`/academic/assignments/${assignmentId}/`)
    assignment.value = res.data
    
    // 获取当前学生的提交情况
    if (!isStaff.value) {
      const subRes = await request.get('/academic/submissions/', { 
        params: { assignment: assignmentId } 
      })
      if (subRes.data.results && subRes.data.results.length > 0) {
        submission.value = subRes.data.results[0]
      }
    }
  } catch (error) {
    console.error('获取详情失败', error)
    ElMessage.error('加载作业详情失败')
  } finally {
    loading.value = false
  }
}

const isOverdue = computed(() => {
  if (!assignment.value.deadline) return false
  return dayjs().isAfter(dayjs(assignment.value.deadline))
})

const studentStatus = computed(() => {
  if (submission.value) return submission.value.status
  if (isOverdue.value) return 'overdue'
  return 'pending'
})

const canSubmit = computed(() => {
  if (isStaff.value) return false
  if (submission.value) return false
  if (studentStatus.value === 'pending') return true
  if (studentStatus.value === 'overdue' && assignment.value.allow_late_submission) return true
  return false
})

const handleFileChange = (file) => {
  form.file = file.raw
}

const handleSubmit = async () => {
  if (!form.content && !form.file) {
    ElMessage.warning('请填写内容或上传附件')
    return
  }
  
  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('assignment', assignmentId)
    if (form.content) formData.append('content', form.content)
    if (form.file) formData.append('file', form.file)
    
    await request.post('/academic/submissions/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success('作业提交成功')
    fetchDetail()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '提交失败')
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.back()
const goSubmissions = () => router.push(`/academic/assignments/${assignmentId}/submissions`)

const getStatusType = (status) => {
  const map = { pending: 'info', submitted: 'primary', graded: 'success', returned: 'warning', overdue: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '待提交', submitted: '已提交', graded: '已评分', returned: '需重交', overdue: '已截止' }
  return map[status] || status
}

onMounted(fetchDetail)
</script>

<style scoped lang="scss">
.assignment-detail-container {
  padding: 20px;

  .page-header {
    margin-bottom: 24px;
    background: #fff;
    padding: 16px 24px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  }

  .main-content {
    .section-title {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 16px;
      padding-left: 10px;
      border-left: 4px solid #409eff;
    }

    .detail-card, .submission-card, .info-card, .submission-stats {
      margin-bottom: 20px;
      border-radius: 8px;
    }

    .description-content {
      line-height: 1.8;
      white-space: pre-wrap;
      color: #303133;
      font-size: 15px;
    }

    .attachment-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 4px;
      
      .download-link {
        color: #409eff;
        text-decoration: none;
        &:hover { text-decoration: underline; }
      }
    }

    .submission-view {
      .content-text {
        white-space: pre-wrap;
        line-height: 1.6;
      }
      
      .grade-section {
        margin-top: 30px;
        
        .grade-info {
          background: #f0f9eb;
          padding: 20px;
          border-radius: 8px;
          border-left: 5px solid #67c23a;
          
          .score-display {
            margin-bottom: 12px;
            .score-num {
              font-size: 24px;
              font-weight: bold;
              color: #67c23a;
            }
          }
          
          .feedback-text {
            color: #606266;
            line-height: 1.5;
          }
        }
      }
    }

    .form-ops {
      margin-top: 24px;
      display: flex;
      justify-content: center;
    }

    .meta-list {
      .meta-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 16px;
        
        .label { color: #909399; }
        .value { font-weight: 500; }
        .text-danger { color: #f56c6c; }
      }
    }

    .submission-stats {
      .stats-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        padding: 20px 0;
        
        .stats-text {
          text-align: center;
          .num { font-size: 20px; font-weight: bold; }
          .label { font-size: 12px; color: #909399; }
        }
      }
      .stats-ops { margin-top: 10px; }
    }
  }
}
</style>
