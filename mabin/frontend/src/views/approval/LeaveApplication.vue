<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>请假申请</span>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </template>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      style="max-width: 800px"
    >
      <el-form-item label="申请人类型" prop="applicant_type">
        <el-radio-group v-model="form.applicant_type">
          <el-radio label="student">学生</el-radio>
          <el-radio label="teacher">教职工</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="请假类型" prop="leave_type">
        <el-select v-model="form.leave_type" placeholder="请选择请假类型" style="width: 100%">
          <el-option label="病假" value="sick" />
          <el-option label="事假" value="personal" />
          <el-option label="因公" value="business" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="开始时间" prop="start_time">
        <el-date-picker
          v-model="form.start_time"
          type="datetime"
          placeholder="选择开始时间"
          style="width: 100%"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
      
      <el-form-item label="结束时间" prop="end_time">
        <el-date-picker
          v-model="form.end_time"
          type="datetime"
          placeholder="选择结束时间"
          style="width: 100%"
          format="YYYY-MM-DD HH:mm"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>
      
      <el-form-item label="请假天数" prop="days">
        <el-input-number
          v-model="form.days"
          :precision="1"
          :min="0.5"
          :step="0.5"
          style="width: 100%"
        />
        <div class="form-tip">系统将根据开始和结束时间自动计算天数</div>
      </el-form-item>
      
      <el-form-item label="请假原因" prop="reason">
        <el-input
          v-model="form.reason"
          type="textarea"
          :rows="4"
          placeholder="请详细说明请假原因"
        />
      </el-form-item>
      
      <el-form-item label="医院证明" v-if="form.leave_type === 'sick'">
        <FileUpload
          v-model="form.medical_certificate"
          :limit="1"
          accept=".pdf,.jpg,.jpeg,.png"
          tip="病假需上传医院证明（PDF或图片）"
        />
      </el-form-item>
      
      <el-form-item label="其他附件">
        <FileUpload
          v-model="form.attachments"
          :limit="5"
          tip="可上传相关证明材料"
        />
      </el-form-item>

      <el-form-item label="抄送给">
        <el-select
          v-model="form.cc_user_ids"
          multiple
          filterable
          remote
          reserve-keyword
          placeholder="请输入用户名搜索"
          :remote-method="searchUsers"
          :loading="userLoading"
          style="width: 100%"
        >
          <el-option
            v-for="item in userOptions"
            :key="item.id"
            :label="item.real_name || item.username"
            :value="item.id"
          />
        </el-select>
        <div class="form-tip">抄送对象将收到通知并可查看申请详情</div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">提交申请</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import api from '@/utils/api'
import FileUpload from '@/components/FileUpload.vue'

dayjs.extend(customParseFormat)

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  applicant_type: 'student',
  leave_type: '',
  start_time: '',
  end_time: '',
  days: 0,
  reason: '',
  medical_certificate: [],
  attachments: [],
  cc_user_ids: []
})

const userOptions = ref([])
const userLoading = ref(false)

const searchUsers = async (query) => {
  if (query) {
    userLoading.value = true
    try {
      const response = await api.get('/users/', { params: { search: query } })
      userOptions.value = response.data.results || response.data
    } catch (error) {
      console.error(error)
    } finally {
      userLoading.value = false
    }
  } else {
    userOptions.value = []
  }
}

// Load initial users (optional, or just rely on search)
onMounted(() => {
  // Pre-load some users or wait for search
})

const rules = {
  applicant_type: [
    { required: true, message: '请选择申请人类型', trigger: 'change' }
  ],
  leave_type: [
    { required: true, message: '请选择请假类型', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  days: [
    { required: true, message: '请输入请假天数', trigger: 'blur' },
    { type: 'number', min: 0.5, message: '请假天数至少0.5天', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入请假原因', trigger: 'blur' },
    { min: 10, message: '请假原因至少10个字符', trigger: 'blur' }
  ]
}

// 自动计算天数
watch([() => form.start_time, () => form.end_time], ([start, end]) => {
  if (start && end) {
    const fmt = 'YYYY-MM-DD HH:mm:ss'
    const startDate = dayjs(start, fmt, true)
    const endDate = dayjs(end, fmt, true)
    if (startDate.isValid() && endDate.isValid() && endDate.isAfter(startDate)) {
      const diffHours = endDate.diff(startDate, 'hour', true)
      form.days = Math.ceil((diffHours / 24) * 2) / 2
    }
  }
})

// 病假必须上传证明
watch(() => form.leave_type, (type) => {
  if (type === 'sick') {
    rules.medical_certificate = [
      { required: true, message: '病假必须上传医院证明', trigger: 'change' }
    ]
  } else {
    delete rules.medical_certificate
  }
})

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    loading.value = true
    const data = {
      ...form,
      medical_certificate: form.medical_certificate[0]?.url || null,
      attachments: (form.attachments || []).map(f => ({
        name: f.name,
        url: f.url,
        size: f.size
      }))
    }
    await api.post('/approval/leave/', data)
    ElMessage.success('请假申请提交成功')
    // 通知首页刷新统计
    window.dispatchEvent(new CustomEvent('approval:changed', { detail: { type: 'leave', action: 'create' } }))
    router.push({ path: '/approval', query: { sub: 'my' } })
  } catch (error) {
    const msg = error?.response?.data?.message || error?.response?.data?.error || error?.message || '提交失败'
    ElMessage.error(msg)
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.medical_certificate = []
  form.attachments = []
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
