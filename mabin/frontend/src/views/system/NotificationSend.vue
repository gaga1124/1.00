<template>
  <div class="notification-send-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>发送通知</span>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="send-form">
        <el-form-item label="通知模板" prop="template_id">
          <el-select 
            v-model="form.template_id" 
            placeholder="请选择模板（可选）" 
            clearable 
            @change="handleTemplateChange"
            style="width: 100%"
          >
            <el-option 
              v-for="item in templates" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" 
            />
          </el-select>
        </el-form-item>

        <el-form-item label="发送对象" prop="broadcast">
          <el-radio-group v-model="form.broadcast">
            <el-radio :label="false">指定用户</el-radio>
            <el-radio :label="true">全员广播</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item 
          v-if="!form.broadcast" 
          label="选择用户" 
          prop="recipient_ids"
        >
          <!-- 实际项目中应使用用户选择器组件，这里简化为输入ID -->
           <el-input v-model="idsInput" placeholder="请输入用户ID，用逗号分隔 (例如: 1,2,3)" @blur="parseIds" />
        </el-form-item>

        <el-form-item label="通知标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>

        <el-form-item label="通知内容" prop="message">
          <el-input 
            v-model="form.message" 
            type="textarea" 
            :rows="6" 
            placeholder="请输入通知内容" 
          />
        </el-form-item>

        <el-form-item label="重要级别" prop="level">
          <el-select v-model="form.level">
            <el-option label="普通信息" value="info" />
            <el-option label="成功提示" value="success" />
            <el-option label="警告提醒" value="warning" />
            <el-option label="严重错误" value="error" />
          </el-select>
        </el-form-item>

        <el-form-item label="关联链接" prop="related_link">
          <el-input v-model="form.related_link" placeholder="例如: /approval/list" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSend" :loading="sending">发送通知</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import dayjs from 'dayjs'

const formRef = ref(null)
const sending = ref(false)
const templates = ref([])
const idsInput = ref('')

const form = ref({
  template_id: undefined,
  broadcast: false,
  recipient_ids: [],
  title: '',
  message: '',
  level: 'info',
  related_link: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  message: [{ required: true, message: '请输入内容', trigger: 'blur' }],
  recipient_ids: [
    { 
      validator: (rule, value, callback) => {
        if (!form.value.broadcast && (!value || value.length === 0)) {
          callback(new Error('请指定接收用户'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

const parseIds = () => {
  if (!idsInput.value) {
    form.value.recipient_ids = []
    return
  }
  const parts = idsInput.value.split(/[,，]/).map(s => s.trim()).filter(s => s)
  form.value.recipient_ids = parts.map(s => parseInt(s)).filter(n => !isNaN(n))
}

const fetchTemplates = async () => {
  try {
    const response = await api.get('/notifications/templates/')
    templates.value = response.data.results || response.data
  } catch (error) {
    console.error(error)
  }
}

const handleTemplateChange = (val) => {
  if (!val) return
  const template = templates.value.find(t => t.id === val)
  if (template) {
    const today = dayjs().format('YYYY年MM月DD日')
    form.value.title = template.title_template.replace(/{date}/g, today)
    form.value.message = template.content_template.replace(/{date}/g, today)
  }
}

const handleSend = async () => {
  if (!formRef.value) return
  
  parseIds() // Ensure IDs are parsed before validation
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      sending.value = true
      try {
        await api.post('/notifications/send_notification/', {
          recipient_ids: form.value.recipient_ids,
          broadcast: form.value.broadcast,
          title: form.value.title,
          message: form.value.message,
          level: form.value.level,
          related_link: form.value.related_link
        })
        ElMessage.success('发送成功')
        resetForm()
      } catch (error) {
        console.error(error)
        ElMessage.error('发送失败: ' + (error.response?.data?.error || '未知错误'))
      } finally {
        sending.value = false
      }
    }
  })
}

const resetForm = () => {
  formRef.value.resetFields()
  form.value = {
    template_id: undefined,
    broadcast: false,
    recipient_ids: [],
    title: '',
    message: '',
    level: 'info',
    related_link: ''
  }
  idsInput.value = ''
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.notification-send-page {
  padding: 20px;
}
.send-form {
  max-width: 800px;
}
</style>
