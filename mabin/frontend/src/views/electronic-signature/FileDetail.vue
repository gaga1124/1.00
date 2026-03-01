<template>
  <el-dialog
    v-model="dialogVisible"
    title="文件详情"
    width="900px"
    :close-on-click-modal="false"
  >
    <div v-loading="loading" class="file-detail">
      <div v-if="file" class="detail-content">
        <div class="file-header">
          <div class="file-info">
            <el-icon class="file-type-icon" :class="getFileIconClass(file.file_name)">
              <Document v-if="isDocument(file.file_name)" />
              <Picture v-else-if="isImage(file.file_name)" />
              <Files v-else />
            </el-icon>
            <div class="file-text">
              <h3 class="file-title">{{ file.title }}</h3>
              <p class="file-name">{{ file.file_name }}</p>
            </div>
          </div>
          <div class="file-actions">
            <el-button type="primary" @click="handleDownload" :loading="downloadLoading">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
            <el-button v-if="file.status === 'signed' || file.status === 'sent'" @click="handleVerify">
              <el-icon><CircleCheck /></el-icon>
              验证签章
            </el-button>
          </div>
        </div>

        <el-divider />

        <div class="file-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件大小">
              {{ file.file_size_display }}
            </el-descriptions-item>
            <el-descriptions-item label="文件类型">
              {{ file.file_type_display }}
            </el-descriptions-item>
            <el-descriptions-item label="所属部门">
              {{ file.department?.name }}
            </el-descriptions-item>
            <el-descriptions-item label="文件状态">
              <el-tag :type="getStatusType(file.status)">{{ file.status_display }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="上传时间" :span="2">
              {{ file.created_at }}
            </el-descriptions-item>
            <el-descriptions-item v-if="file.description" label="文件描述" :span="2">
              {{ file.description }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="file.signature" class="signature-section">
          <el-divider />
          <h4 class="section-title">
            <el-icon><Stamp /></el-icon>
            签章信息
          </h4>
          <div class="signature-info">
            <div class="signature-preview">
              <div class="signature-image">
                <img v-if="file.signature.signature_image" :src="getSignatureImageUrl(file.signature.signature_image)" :alt="file.signature.name" />
                <div v-else class="signature-placeholder">
                  <el-icon><Stamp /></el-icon>
                </div>
              </div>
              <div class="signature-details">
                <div class="signature-name">{{ file.signature.name }}</div>
                <div class="signature-department">{{ file.signature.department?.name }}</div>
                <div class="signature-time">
                  <el-icon><Clock /></el-icon>
                  签章时间：{{ file.signed_at }}
                </div>
                <div class="signature-signer">
                  <el-icon><User /></el-icon>
                  签章人：{{ file.signer?.real_name }}
                </div>
              </div>
            </div>
            <div class="signature-hash">
              <el-alert
                title="文件完整性校验"
                type="success"
                :closable="false"
                show-icon
              >
                <div class="hash-info">
                  <div class="hash-label">文件哈希值：</div>
                  <div class="hash-value">{{ file.signature_hash }}</div>
                </div>
              </el-alert>
            </div>
          </div>
        </div>

        <div v-if="file.verification_result" class="verification-section">
          <el-divider />
          <h4 class="section-title">
            <el-icon><CircleCheck /></el-icon>
            验签结果
          </h4>
          <el-alert
            :title="file.verification_result.message"
            :type="file.verification_result.is_valid ? 'success' : 'error'"
            :closable="false"
            show-icon
          >
            <div class="verification-details">
              <div class="verification-item">
                <span class="verification-label">签章状态：</span>
                <el-tag :type="file.verification_result.is_valid ? 'success' : 'danger'">
                  {{ file.verification_result.is_valid ? '有效' : '无效' }}
                </el-tag>
              </div>
              <div class="verification-item">
                <span class="verification-label">文件完整性：</span>
                <el-tag :type="file.verification_result.is_valid ? 'success' : 'danger'">
                  {{ file.verification_result.is_valid ? '完整' : '已篡改' }}
                </el-tag>
              </div>
            </div>
          </el-alert>
        </div>

        <div v-if="file.recipients && file.recipients.length > 0" class="recipients-section">
          <el-divider />
          <h4 class="section-title">
            <el-icon><User /></el-icon>
            接收人信息
          </h4>
          <div class="recipients-list">
            <div class="recipients-summary">
              <el-tag type="info">共 {{ file.recipients.length }} 人</el-tag>
              <el-tag type="success">已读 {{ getReadCount() }} 人</el-tag>
              <el-tag type="warning">未读 {{ getUnreadCount() }} 人</el-tag>
            </div>
            <el-table :data="file.recipients" style="width: 100%" max-height="300">
              <el-table-column prop="recipient.real_name" label="姓名" width="120" />
              <el-table-column prop="recipient.department.name" label="部门" width="150" />
              <el-table-column label="阅读状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_read ? 'success' : 'warning'" size="small">
                    {{ row.is_read ? '已读' : '未读' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="read_at" label="阅读时间" width="170">
                <template #default="{ row }">
                  {{ row.read_at || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="received_at" label="接收时间" width="170" />
            </el-table>
          </div>
        </div>

        <div v-if="file.file && isImage(file.file_name)" class="file-preview-section">
          <el-divider />
          <h4 class="section-title">
            <el-icon><View /></el-icon>
            文件预览
          </h4>
          <div class="image-preview">
            <img :src="getFileUrl(file.file)" :alt="file.title" />
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, CircleCheck, Stamp, Clock, User, View, Document, Picture, Files } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  fileId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'refresh'])

const dialogVisible = ref(false)
const loading = ref(false)
const downloadLoading = ref(false)
const file = ref(null)

watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.fileId) {
    fetchFileDetail()
  }
})

watch(() => props.fileId, (newVal) => {
  if (newVal && dialogVisible.value) {
    fetchFileDetail()
  }
})

const fetchFileDetail = async () => {
  loading.value = true
  try {
    const res = await api.get(`/electronic-signature/files/${props.fileId}/`)
    file.value = res.data
  } catch (e) {
    ElMessage.error('获取文件详情失败')
  } finally {
    loading.value = false
  }
}

const handleDownload = async () => {
  downloadLoading.value = true
  try {
    const res = await api.get(`/electronic-signature/files/${file.value.id}/download/`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.value.file_name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (e) {
    ElMessage.error('下载失败')
  } finally {
    downloadLoading.value = false
  }
}

const handleVerify = async () => {
  try {
    const res = await api.post(`/electronic-signature/files/${file.value.id}/verify/`)
    file.value.verification_result = res.data
    ElMessage.success('验签完成')
  } catch (e) {
    ElMessage.error('验签失败')
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

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    signed: 'success',
    sent: 'warning',
    revoked: 'danger'
  }
  return map[status] || 'info'
}

const getSignatureImageUrl = (imagePath) => {
  if (!imagePath) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${imagePath}`
}

const getFileUrl = (filePath) => {
  if (!filePath) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${filePath}`
}

const getReadCount = () => {
  if (!file.value || !file.value.recipients) return 0
  return file.value.recipients.filter(r => r.is_read).length
}

const getUnreadCount = () => {
  if (!file.value || !file.value.recipients) return 0
  return file.value.recipients.filter(r => !r.is_read).length
}
</script>

<style scoped>
.file-detail {
  min-height: 200px;
}

.detail-content {
  padding: 0 20px;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.file-info {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  flex: 1;
}

.file-type-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.file-type-icon.document-icon {
  color: #409EFF;
}

.file-type-icon.image-icon {
  color: #67C23A;
}

.file-type-icon.file-icon {
  color: #909399;
}

.file-text {
  flex: 1;
  min-width: 0;
}

.file-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.file-name {
  margin: 0;
  font-size: 14px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.file-meta {
  margin: 20px 0;
}

.signature-section,
.verification-section,
.recipients-section,
.file-preview-section {
  margin: 20px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.signature-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.signature-preview {
  flex: 1;
  min-width: 300px;
  display: flex;
  gap: 16px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.signature-image {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid #ebeef5;
}

.signature-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.signature-placeholder {
  color: #c0c4cc;
  font-size: 40px;
}

.signature-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.signature-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.signature-department {
  font-size: 14px;
  color: #606266;
}

.signature-time,
.signature-signer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
}

.signature-hash {
  flex: 1;
  min-width: 300px;
}

.hash-info {
  margin-top: 12px;
}

.hash-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.hash-value {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #606266;
  word-break: break-all;
  line-height: 1.5;
}

.verification-details {
  margin-top: 12px;
  display: flex;
  gap: 24px;
}

.verification-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.verification-label {
  font-size: 13px;
  color: #606266;
}

.recipients-summary {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.image-preview {
  width: 100%;
  max-height: 500px;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 16px;
  background-color: #f5f7fa;
}

.image-preview img {
  max-width: 100%;
  max-height: 500px;
  display: block;
  margin: 0 auto;
  object-fit: contain;
}
</style>
