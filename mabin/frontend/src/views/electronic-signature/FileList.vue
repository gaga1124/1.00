<template>
  <div class="electronic-signature">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">电子文件管理</span>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </div>
        </div>
      </template>

      <div class="statistics-panel">
        <div class="stat-card">
          <div class="stat-icon total">
            <el-icon><Files /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.total }}</div>
            <div class="stat-label">文件总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon draft">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.draft }}</div>
            <div class="stat-label">草稿</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon signed">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.signed }}</div>
            <div class="stat-label">已签章</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon sent">
            <el-icon><Promotion /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.sent }}</div>
            <div class="stat-label">已发送</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon revoked">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.revoked }}</div>
            <div class="stat-label">已撤回</div>
          </div>
        </div>
      </div>

      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名或标题"
          clearable
          style="width: 300px"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="已签章" value="signed" />
          <el-option label="已发送" value="sent" />
          <el-option label="已撤回" value="revoked" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
          @change="handleDateChange"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <el-table :data="files" v-loading="loading" style="width: 100%">
        <el-table-column type="index" width="50" />
        <el-table-column prop="title" label="文件标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="file_name" label="文件名" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="file-name-cell">
              <el-icon class="file-type-icon" :class="getFileIconClass(row.file_name)">
                <Document v-if="isDocument(row.file_name)" />
                <Picture v-else-if="isImage(row.file_name)" />
                <Files v-else />
              </el-icon>
              <span>{{ row.file_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="100">
          <template #default="{ row }">
            {{ row.file_size_display }}
          </template>
        </el-table-column>
        <el-table-column prop="department.name" label="所属部门" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="签章" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.signature" type="success" size="small">已签章</el-tag>
            <el-tag v-else type="info" size="small">未签章</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="170" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button 
              v-if="row.status === 'draft'" 
              type="success" 
              link 
              size="small" 
              @click="handleSign(row)"
            >
              签章
            </el-button>
            <el-button 
              v-if="row.status === 'signed'" 
              type="warning" 
              link 
              size="small" 
              @click="handleSend(row)"
            >
              发送
            </el-button>
            <el-button 
              v-if="row.status === 'sent'" 
              type="danger" 
              link 
              size="small" 
              @click="handleRevoke(row)"
            >
              撤回
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 上传文件对话框 -->
    <FileFormDialog
      v-model:visible="formVisible"
      @success="handleFormSuccess"
    />

    <!-- 文件详情对话框 -->
    <FileDetail
      v-model:visible="detailVisible"
      :file-id="currentFileId"
      @refresh="fetchFiles"
    />

    <!-- 签章对话框 -->
    <el-dialog
      v-model="signVisible"
      title="文件签章"
      width="600px"
    >
      <el-form :model="signForm" label-width="100px">
        <el-form-item label="选择签章" required>
          <el-radio-group v-model="signForm.signature_id" class="signature-selector">
            <div 
              v-for="sig in signatures" 
              :key="sig.id" 
              class="signature-option"
              :class="{ 'selected': signForm.signature_id === sig.id }"
            >
              <el-radio :label="sig.id" class="signature-radio">
                <div class="signature-preview">
                  <div class="signature-image">
                    <img v-if="sig.signature_image" :src="getSignatureImageUrl(sig.signature_image)" :alt="sig.name" />
                    <div v-else class="signature-placeholder">
                      <el-icon><Stamp /></el-icon>
                    </div>
                  </div>
                  <div class="signature-info">
                    <div class="signature-name">{{ sig.name }}</div>
                    <div class="signature-department">{{ sig.department?.name }}</div>
                  </div>
                </div>
              </el-radio>
            </div>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="userStore.user.real_name" disabled />
        </el-form-item>
        <el-form-item label="操作时间">
          <el-input v-model="currentTime" disabled />
        </el-form-item>
        <el-alert
          title="签章后文件将被锁定，无法修改内容。请确保文件内容正确后再进行签章操作。"
          type="warning"
          :closable="false"
          show-icon
        />
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="signVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmSign" :loading="signLoading" :disabled="!signForm.signature_id">
            确认签章
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 发送文件对话框 -->
    <el-dialog
      v-model="sendVisible"
      title="发送文件"
      width="700px"
    >
      <el-form :model="sendForm" label-width="100px">
        <el-form-item label="发送方式">
          <el-radio-group v-model="sendForm.sendType">
            <el-radio label="specific">指定人员</el-radio>
            <el-radio label="department">指定部门</el-radio>
            <el-radio label="all">全员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="sendForm.sendType === 'specific'" label="选择人员">
          <el-select
            v-model="sendForm.recipient_ids"
            multiple
            filterable
            placeholder="请选择接收人"
            style="width: 100%"
          >
            <el-option 
              v-for="user in users" 
              :key="user.id" 
              :label="user.real_name" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="sendForm.sendType === 'department'" label="选择部门">
          <el-select
            v-model="sendForm.departments"
            multiple
            placeholder="请选择部门"
            style="width: 100%"
          >
            <el-option 
              v-for="dept in departments" 
              :key="dept.id" 
              :label="dept.name" 
              :value="dept.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="sendForm.sendType === 'all'" label="接收范围">
          <el-input value="系统内所有用户" disabled />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="sendVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmSend" :loading="sendLoading">
            确认发送
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, Document, Picture, Files, Stamp, CircleCheck, Promotion, CircleClose } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import FileFormDialog from './FileFormDialog.vue'
import FileDetail from './FileDetail.vue'

const userStore = useUserStore()
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const dateRange = ref([])
const formVisible = ref(false)
const detailVisible = ref(false)
const signVisible = ref(false)
const sendVisible = ref(false)
const signLoading = ref(false)
const sendLoading = ref(false)
const currentFileId = ref(null)
const currentSignFile = ref(null)
const currentSendFile = ref(null)
const currentTime = ref(new Date().toLocaleString())

const files = ref([])
const signatures = ref([])
const users = ref([])
const departments = ref([])
const statistics = reactive({
  total: 0,
  draft: 0,
  signed: 0,
  sent: 0,
  revoked: 0
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const signForm = reactive({
  signature_id: ''
})

const sendForm = reactive({
  sendType: 'specific',
  recipient_ids: [],
  departments: []
})

const statusMap = {
  draft: '草稿',
  signed: '已签章',
  sent: '已发送',
  revoked: '已撤回'
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

const getSignatureImageUrl = (imagePath) => {
  if (!imagePath) return ''
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${imagePath}`
}

const fetchFiles = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: searchQuery.value,
      ordering: '-created_at'
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.created_at__gte = dateRange.value[0]
      params.created_at__lte = dateRange.value[1]
    }
    const res = await api.get('/electronic-signature/files/', { params })
    files.value = res.data.results || []
    pagination.total = res.data.count || 0
  } catch (e) {
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStatistics = async () => {
  try {
    const res = await api.get('/electronic-signature/files/statistics/')
    statistics.total = res.data.total || 0
    statistics.draft = res.data.draft || 0
    statistics.signed = res.data.signed || 0
    statistics.sent = res.data.sent || 0
    statistics.revoked = res.data.revoked || 0
  } catch (e) {
    console.error('获取统计数据失败', e)
  }
}

const fetchSignatures = async () => {
  try {
    const res = await api.get('/electronic-signature/signatures/')
    signatures.value = res.data.results || []
  } catch (e) {
    console.error('获取签章失败', e)
  }
}

const fetchUsers = async () => {
  try {
    const res = await api.get('/users/list/')
    users.value = res.data || []
  } catch (e) {
    console.error('获取用户列表失败', e)
  }
}

const fetchDepartments = async () => {
  try {
    const res = await api.get('/rbac/departments/')
    departments.value = res.data.results || []
  } catch (e) {
    console.error('获取部门列表失败', e)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchFiles()
}

const handleReset = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  dateRange.value = []
  pagination.page = 1
  fetchFiles()
}

const handleDateChange = () => {
  pagination.page = 1
  fetchFiles()
}

const handleSizeChange = () => {
  fetchFiles()
}

const handlePageChange = () => {
  fetchFiles()
}

const handleCreate = () => {
  formVisible.value = true
}

const handleView = (row) => {
  currentFileId.value = row.id
  detailVisible.value = true
}

const handleSign = (row) => {
  currentSignFile.value = row
  signForm.signature_id = ''
  signVisible.value = true
}

const handleConfirmSign = async () => {
  if (!signForm.signature_id) {
    ElMessage.error('请选择签章')
    return
  }
  
  signLoading.value = true
  try {
    await api.post(`/electronic-signature/files/${currentSignFile.value.id}/sign/`, signForm)
    ElMessage.success('签章成功')
    signVisible.value = false
    fetchFiles()
    fetchStatistics()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '签章失败')
  } finally {
    signLoading.value = false
  }
}

const handleSend = (row) => {
  currentSendFile.value = row
  sendForm.sendType = 'specific'
  sendForm.recipient_ids = []
  sendForm.departments = []
  sendVisible.value = true
}

const handleConfirmSend = async () => {
  if (sendForm.sendType === 'specific' && sendForm.recipient_ids.length === 0) {
    ElMessage.error('请选择接收人')
    return
  }
  if (sendForm.sendType === 'department' && sendForm.departments.length === 0) {
    ElMessage.error('请选择部门')
    return
  }
  
  sendLoading.value = true
  try {
    const data = {
      recipient_ids: sendForm.recipient_ids,
      departments: sendForm.departments,
      send_all: sendForm.sendType === 'all'
    }
    await api.post(`/electronic-signature/files/${currentSendFile.value.id}/send/`, data)
    ElMessage.success('发送成功')
    sendVisible.value = false
    fetchFiles()
    fetchStatistics()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '发送失败')
  } finally {
    sendLoading.value = false
  }
}

const handleRevoke = async (row) => {
  try {
    await ElMessageBox.confirm('确定要撤回此文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.post(`/electronic-signature/files/${row.id}/revoke/`)
    ElMessage.success('撤回成功')
    fetchFiles()
    fetchStatistics()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '撤回失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除此文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'danger'
    })
    await api.delete(`/electronic-signature/files/${row.id}/`)
    ElMessage.success('删除成功')
    fetchFiles()
    fetchStatistics()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  fetchFiles()
  fetchStatistics()
}

onMounted(() => {
  fetchFiles()
  fetchStatistics()
  fetchSignatures()
  fetchUsers()
  fetchDepartments()
})
</script>

<style scoped>
.electronic-signature {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.statistics-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stat-card:nth-child(2) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card:nth-child(3) {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card:nth-child(4) {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-card:nth-child(5) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 28px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-type-icon {
  font-size: 16px;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.signature-selector {
  width: 100%;
}

.signature-option {
  display: inline-block;
  margin: 0 16px 16px 0;
  vertical-align: top;
}

.signature-radio {
  display: block;
  margin: 0;
}

.signature-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.signature-option.selected .signature-preview {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.signature-image {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.signature-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.signature-placeholder {
  color: #c0c4cc;
  font-size: 32px;
}

.signature-info {
  flex: 1;
}

.signature-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.signature-department {
  font-size: 12px;
  color: #909399;
}
</style>
