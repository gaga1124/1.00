<template>
  <div class="file-upload">
    <el-upload
      :action="uploadUrl"
      :headers="uploadHeaders"
      :file-list="fileList"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-remove="handleRemove"
      :before-upload="beforeUpload"
      :limit="limit"
      :multiple="multiple"
      :accept="accept"
      :disabled="disabled"
    >
      <el-button type="primary" :disabled="disabled">
        <el-icon><Upload /></el-icon>
        选择文件
      </el-button>
      <template #tip>
        <div class="el-upload__tip">
          {{ tip || `支持 ${accept || '所有格式'}，单个文件不超过 ${maxSize}MB` }}
        </div>
      </template>
    </el-upload>
    
    <div v-if="fileList.length > 0" class="file-list">
      <div v-for="(file, index) in fileList" :key="index" class="file-item">
        <el-icon class="file-icon"><Document /></el-icon>
        <span class="file-name" @click="handlePreview(file)">{{ file.name }}</span>
        <span class="file-size">({{ formatFileSize(file.size) }})</span>
        <div class="file-ops">
          <el-button
            type="primary"
            link
            size="small"
            @click="handlePreview(file)"
          >
            预览
          </el-button>
          <el-button
            type="danger"
            link
            size="small"
            @click="handleRemove(file)"
            :disabled="disabled"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="文件预览" width="800px" destroy-on-close>
      <div v-if="previewFile" class="preview-container">
        <template v-if="isImage(previewFile.url)">
          <el-image :src="previewFile.url" fit="contain" style="width: 100%; max-height: 600px" />
        </template>
        <template v-else-if="isPDF(previewFile.url)">
          <iframe :src="previewFile.url" width="100%" height="600px" frameborder="0"></iframe>
        </template>
        <template v-else>
          <div class="unsupported-preview">
            <el-empty description="该文件类型暂不支持直接预览，请下载后查看">
              <el-button type="primary" @click="downloadFile(previewFile)">下载文件</el-button>
            </el-empty>
          </div>
        </template>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Document } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  limit: {
    type: Number,
    default: 10
  },
  maxSize: {
    type: Number,
    default: 10 // MB
  },
  accept: {
    type: String,
    default: '.pdf,.doc,.docx,.jpg,.jpeg,.png,.xls,.xlsx'
  },
  multiple: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  tip: {
    type: String,
    default: ''
  },
  uploadPath: {
    type: String,
    default: '/media/uploads/'
  }
})

const emit = defineEmits(['update:modelValue'])

const userStore = useUserStore()
const fileList = ref([])
const previewVisible = ref(false)
const previewFile = ref(null)

const uploadUrl = computed(() => {
  return `${api.defaults.baseURL}/utils/upload/`
})

const uploadHeaders = computed(() => {
  return {
    'Authorization': `Bearer ${userStore.token}`
  }
})

watch(() => props.modelValue, (newVal) => {
  if (newVal && newVal.length > 0) {
    fileList.value = newVal.map(item => ({
      name: item.name || item.url?.split('/').pop() || '文件',
      url: item.url,
      size: item.size || 0,
      uid: item.uid || Date.now() + Math.random()
    }))
  } else {
    fileList.value = []
  }
}, { immediate: true })

const beforeUpload = (file) => {
  // 检查文件大小
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  
  // 检查文件类型
  if (props.accept) {
    const acceptTypes = props.accept.split(',').map(t => t.trim())
    const fileExt = '.' + file.name.split('.').pop().toLowerCase()
    if (!acceptTypes.some(type => type.includes(fileExt))) {
      ElMessage.error(`不支持的文件类型，仅支持：${props.accept}`)
      return false
    }
  }
  
  return true
}

const handleSuccess = (response, file) => {
  if (response.success || response.url) {
    const fileInfo = {
      name: file.name,
      url: response.url || response.data?.url,
      size: file.size,
      uid: file.uid
    }
    fileList.value.push(fileInfo)
    updateModelValue()
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '文件上传失败')
  }
}

const handleError = (error) => {
  ElMessage.error('文件上传失败：' + (error.message || '未知错误'))
}

const handleRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
    updateModelValue()
  }
}

const updateModelValue = () => {
  const value = fileList.value.map(file => ({
    name: file.name,
    url: file.url,
    size: file.size
  }))
  emit('update:modelValue', value)
}

const handlePreview = (file) => {
  previewFile.value = file
  previewVisible.value = true
}

const isImage = (url) => {
  if (!url) return false
  const ext = url.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)
}

const isPDF = (url) => {
  if (!url) return false
  const ext = url.split('.').pop().toLowerCase()
  return ext === 'pdf'
}

const downloadFile = (file) => {
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const formatFileSize = (size) => {
  if (!size) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let unitIndex = 0
  let fileSize = size
  while (fileSize >= 1024 && unitIndex < units.length - 1) {
    fileSize /= 1024
    unitIndex++
  }
  return `${fileSize.toFixed(2)} ${units[unitIndex]}`
}
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.file-list {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  margin-right: 8px;
  color: #409eff;
}

.file-name {
  flex: 1;
  margin-right: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
}

.file-name:hover {
  color: #409eff;
}

.file-size {
  color: #909399;
  font-size: 12px;
  margin-right: 10px;
}

.file-ops {
  display: flex;
  gap: 10px;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.unsupported-preview {
  text-align: center;
}
</style>
