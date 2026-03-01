<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-form-item label="报修分类" prop="category" required>
      <el-select v-model="form.category" placeholder="请选择报修分类" style="width: 100%">
        <el-option
          v-for="cat in categories"
          :key="cat.id"
          :label="cat.name"
          :value="cat.id"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="报修标题" prop="title" required>
      <el-input v-model="form.title" placeholder="请输入报修标题" />
    </el-form-item>
    
    <el-form-item label="报修地点" prop="location" required>
      <el-input v-model="form.location" placeholder="请输入具体地点，如：教学楼A101" />
    </el-form-item>
    
    <el-form-item label="详细描述" prop="description" required>
      <el-input
        v-model="form.description"
        type="textarea"
        :rows="5"
        placeholder="请详细描述报修问题，包括故障现象、影响范围等"
      />
    </el-form-item>
    
    <el-form-item label="优先级" prop="priority" required>
      <el-radio-group v-model="form.priority">
        <el-radio label="low">低</el-radio>
        <el-radio label="medium">中</el-radio>
        <el-radio label="high">高</el-radio>
        <el-radio label="urgent">紧急</el-radio>
      </el-radio-group>
      <div class="form-tip">紧急：影响正常教学/工作，需立即处理</div>
    </el-form-item>
    
    <el-form-item label="联系人" prop="contact_name" required>
      <el-input v-model="form.contact_name" placeholder="请输入联系人姓名" />
    </el-form-item>
    
    <el-form-item label="联系电话" prop="contact_phone" required>
      <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
    </el-form-item>
    
    <el-form-item label="现场图片">
      <FileUpload
        v-model="form.images"
        :limit="5"
        accept=".jpg,.jpeg,.png"
        tip="可上传现场照片，最多5张，支持jpg/png格式"
      />
      <div class="form-tip">上传现场照片有助于快速定位问题</div>
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">提交报修</el-button>
      <el-button @click="handleReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import FileUpload from '@/components/FileUpload.vue'
import { validatePhone } from '@/utils/validator'

const emit = defineEmits(['success'])

const formRef = ref(null)
const loading = ref(false)
const categories = ref([])
const fieldLabels = {
  applicant: '申请人',
  category: '报修分类',
  title: '报修标题',
  location: '报修地点',
  description: '详细描述',
  priority: '优先级',
  contact_name: '联系人',
  contact_phone: '联系电话',
  images: '现场图片'
}

const form = reactive({
  category: null,
  title: '',
  location: '',
  description: '',
  priority: 'medium',
  contact_name: '',
  contact_phone: '',
  images: []
})

const rules = {
  category: [
    { required: true, message: '请选择报修分类', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入报修标题', trigger: 'blur' },
    { min: 5, message: '标题至少5个字符', trigger: 'blur' }
  ],
  location: [
    { required: true, message: '请输入报修地点', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入详细描述', trigger: 'blur' },
    { min: 10, message: '描述至少10个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  contact_name: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { validator: validatePhone, trigger: 'blur' }
  ]
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/repair/categories/')
    categories.value = response.data.results || response.data
  } catch (error) {
    ElMessage.error('获取分类失败')
    console.error(error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    // Element Plus v2: validate() 成功时 resolve，无返回值；失败时 reject
    await formRef.value.validate()
  } catch {
    return
  }
  loading.value = true
  try {
    const data = {
      category: form.category,
      title: form.title,
      location: form.location,
      description: form.description,
      priority: form.priority,
      contact_name: form.contact_name,
      contact_phone: form.contact_phone,
      images: Array.isArray(form.images)
        ? form.images.map(img => ({
            name: img.name,
            url: img.url,
            size: img.size
          }))
        : []
    }
    await api.post('/repair/applications/', data)
    ElMessage.success('报修提交成功，我们会尽快处理')
    emit('success')
  } catch (error) {
    const data = error.response?.data
    let msg = data?.detail || data?.error
    let firstField = null
    if (!msg) {
      if (typeof data === 'string') {
        msg = data
      } else if (data && typeof data === 'object') {
        const parts = []
        for (const [k, v] of Object.entries(data)) {
          const text = Array.isArray(v) ? v.join(', ') : String(v)
          parts.push(`${fieldLabels[k] || k}: ${text}`)
          if (!firstField) firstField = k
        }
        msg = parts.filter(Boolean).join('; ')
      }
    }
    ElMessage.error(msg || '提交失败')
    if (firstField && formRef.value?.scrollToField) {
      formRef.value.scrollToField(firstField)
    }
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.images = []
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
