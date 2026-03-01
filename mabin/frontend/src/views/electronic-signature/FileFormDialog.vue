<template>
  <el-dialog
    v-model="dialogVisible"
    title="上传电子文件"
    width="700px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
      <el-form-item label="文件标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入文件标题" />
      </el-form-item>
      <el-form-item label="文件描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          placeholder="请输入文件描述"
          :rows="3"
        />
      </el-form-item>
      <el-form-item label="所属部门" prop="department_id">
        <el-select v-model="form.department_id" placeholder="请选择部门" style="width: 100%">
          <el-option 
            v-for="dept in departments" 
            :key="dept.id" 
            :label="dept.name" 
            :value="dept.id" 
          />
        </el-select>
      </el-form-item>
      <el-form-item label="上传文件" prop="file" required>
        <div 
          class="upload-area"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="handleDragOver"
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileChange"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.gif"
            style="display: none"
          />
          
          <div v-if="!form.file" class="upload-placeholder">
            <el-icon class="upload-icon"><Upload /></el-icon>
            <div class="upload-text">
              <p>拖拽文件到此处，或点击上传</p>
              <p class="upload-hint">支持PDF、Word、Excel、PowerPoint、文本和图片文件</p>
            </div>
          </div>
          
          <div v-else class="file-preview">
            <div class="file-info">
              <el-icon class="file-icon" :class="getFileIconClass(form.file.name)">
                <Document v-if="isDocument(form.file.name)" />
                <Picture v-else-if="isImage(form.file.name)" />
                <Files v-else />
              </el-icon>
              <div class="file-details">
                <div class="file-name">{{ form.file.name }}</div>
                <div class="file-meta">
                  <span>{{ formatFileSize(form.file.size) }}</span>
                  <el-button type="danger" link @click.stop="removeFile" class="remove-btn">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-form-item>
      
      <el-form-item v-if="form.file && isImage(form.file.name)" label="文件预览">
        <div class="image-preview">
          <img :src="previewUrl" alt="文件预览" />
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          上传
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document, Picture, Files, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'success'])

const dialogVisible = ref(false)
const formRef = ref(null)
const fileInput = ref(null)
const loading = ref(false)
const isDragOver = ref(false)
const fileList = ref([])
const departments = ref([])

const form = reactive({
  title: '',
  description: '',
  department_id: '',
  file: null
})

const rules = {
  title: [
    { required: true, message: '请输入文件标题', trigger: 'blur' },
    { max: 255, message: '标题长度不能超过255个字符', trigger: 'blur' }
  ],
  department_id: [
    { required: true, message: '请选择所属部门', trigger: 'change' }
  ],
  file: [
    { required: true, message: '请选择文件', trigger: 'change' }
  ]
}

const previewUrl = computed(() => {
  if (form.file && isImage(form.file.name)) {
    return URL.createObjectURL(form.file)
  }
  return null
})

watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal) {
    resetForm()
    fetchDepartments()
  }
})

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.department_id = ''
  form.file = null
  fileList.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleFileSelect(files[0])
  }
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    handleFileSelect(files[0])
  }
}

const handleFileSelect = (file) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过50MB')
    return
  }
  
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'image/jpeg',
    'image/png',
    'image/gif'
  ]
  
  if (!allowedTypes.includes(file.type) && !isAllowedExtension(file.name)) {
    ElMessage.error('不支持的文件类型')
    return
  }
  
  form.file = file
  if (!form.title) {
    form.title = file.name.replace(/\.[^/.]+$/, '')
  }
}

const isAllowedExtension = (filename) => {
  const allowedExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.jpg', '.jpeg', '.png', '.gif']
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return allowedExtensions.includes(ext)
}

const removeFile = () => {
  form.file = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const isDocument = (filename) => {
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'].includes(ext)
}

const isImage = (filename) => {
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return ['.jpg', '.jpeg', '.png', '.gif'].includes(ext)
}

const getFileIconClass = (filename) => {
  if (isDocument(filename)) return 'document-icon'
  if (isImage(filename)) return 'image-icon'
  return 'file-icon'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const fetchDepartments = async () => {
  try {
    const res = await api.get('/rbac/departments/')
    departments.value = res.data.results || []
  } catch (e) {
    console.error('获取部门列表失败', e)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('title', form.title)
        formData.append('description', form.description)
        formData.append('department_id', form.department_id)
        formData.append('file', form.file)
        
        await api.post('/electronic-signature/files/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        ElMessage.success('上传成功')
        emit('update:visible', false)
        emit('success')
      } catch (e) {
        ElMessage.error(e.response?.data?.error || '上传失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #409EFF;
}

.upload-area.drag-over {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.upload-placeholder {
  text-align: center;
  color: #909399;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 4px 0;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.file-preview {
  width: 100%;
  padding: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.file-icon {
  font-size: 32px;
  color: #409EFF;
}

.file-icon.document-icon {
  color: #409EFF;
}

.file-icon.image-icon {
  color: #67C23A;
}

.file-icon.file-icon {
  color: #909399;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.remove-btn {
  padding: 4px;
}

.image-preview {
  width: 100%;
  max-height: 300px;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 8px;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  display: block;
  margin: 0 auto;
}
</style>
