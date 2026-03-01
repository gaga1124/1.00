<template>
  <el-dialog
    :title="editData ? '编辑通知' : '新建通知'"
    v-model="dialogVisible"
    width="800px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入通知标题" maxlength="200" show-word-limit />
      </el-form-item>

      <el-form-item label="业务类型" prop="business_type">
        <el-select v-model="form.business_type" placeholder="请选择业务类型" style="width: 100%">
          <el-option label="系统通知" value="system" />
          <el-option label="流程审批" value="workflow" />
          <el-option label="文件签章" value="file" />
          <el-option label="教务通知" value="academic" />
          <el-option label="预警提醒" value="warning" />
          <el-option label="活动通知" value="activity" />
          <el-option label="报修服务" value="repair" />
          <el-option label="资源预约" value="resource" />
          <el-option label="评奖评优" value="award" />
          <el-option label="就业服务" value="career" />
          <el-option label="党建团建" value="party" />
          <el-option label="科研管理" value="research" />
        </el-select>
      </el-form-item>

      <el-form-item label="重要等级" prop="priority">
        <el-radio-group v-model="form.priority">
          <el-radio-button label="normal">普通</el-radio-button>
          <el-radio-button label="important">重要</el-radio-button>
          <el-radio-button label="urgent">紧急</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="接收人" prop="notification_type">
        <el-radio-group v-model="form.notification_type" @change="handleTypeChange">
          <el-radio-button label="all">全员通知</el-radio-button>
          <el-radio-button label="role">按角色</el-radio-button>
          <el-radio-button label="department">按部门</el-radio-button>
          <el-radio-button label="specific">指定人员</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 按角色选择 -->
      <el-form-item v-if="form.notification_type === 'role'" label="选择角色" prop="recipient_roles">
        <el-select
          v-model="form.recipient_roles"
          multiple
          placeholder="请选择角色"
          style="width: 100%"
        >
          <el-option label="管理员" value="admin" />
          <el-option label="教师" value="teacher" />
          <el-option label="学生" value="student" />
          <el-option label="职工" value="staff" />
        </el-select>
      </el-form-item>

      <!-- 按部门选择 -->
      <el-form-item v-if="form.notification_type === 'department'" label="选择部门" prop="recipient_departments">
        <el-tree-select
          v-model="form.recipient_departments"
          :data="departmentOptions"
          :props="{ label: 'name', value: 'id', children: 'children' }"
          multiple
          placeholder="请选择部门"
          style="width: 100%"
        />
      </el-form-item>

      <!-- 指定人员选择 -->
      <el-form-item v-if="form.notification_type === 'specific'" label="选择人员" prop="recipient_ids">
        <el-select
          v-model="form.recipient_ids"
          multiple
          filterable
          remote
          :remote-method="searchUsers"
          :loading="userLoading"
          placeholder="请输入姓名搜索"
          style="width: 100%"
        >
          <el-option
            v-for="user in userOptions"
            :key="user.id"
            :label="`${user.real_name || user.username} (${user.username})`"
            :value="user.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="内容" prop="content">
        <el-input
          v-model="form.content"
          type="textarea"
          :rows="6"
          placeholder="请输入通知内容"
          maxlength="5000"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="附件">
        <el-upload
          ref="uploadRef"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :on-remove="handleRemove"
          :before-upload="beforeUpload"
          :file-list="fileList"
          multiple
          :auto-upload="true"
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            上传附件
          </el-button>
          <template #tip>
            <div class="el-upload__tip">
              支持任意格式文件，单个文件不超过 50MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="info" @click="handleSaveDraft" :loading="saving">保存草稿</el-button>
      <el-button type="primary" @click="handleSend" :loading="sending">立即发送</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const props = defineProps({
  visible: Boolean,
  editData: Object
})

const emit = defineEmits(['update:visible', 'success'])

const userStore = useUserStore()
const formRef = ref(null)
const uploadRef = ref(null)
const saving = ref(false)
const sending = ref(false)
const userLoading = ref(false)

const departmentOptions = ref([])
const userOptions = ref([])
const fileList = ref([])
const uploadedFiles = ref([])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const form = reactive({
  title: '',
  content: '',
  priority: 'normal',
  business_type: 'system',
  notification_type: 'specific',
  recipient_ids: [],
  recipient_roles: [],
  recipient_departments: []
})

const rules = {
  title: [
    { required: true, message: '请输入通知标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入通知内容', trigger: 'blur' },
    { min: 1, max: 5000, message: '内容长度在 1 到 5000 个字符', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择重要等级', trigger: 'change' }
  ],
  notification_type: [
    { required: true, message: '请选择接收人类型', trigger: 'change' }
  ],
  recipient_roles: [
    { 
      required: true, 
      message: '请选择至少一个角色', 
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (form.notification_type === 'role' && (!value || value.length === 0)) {
          callback(new Error('请选择至少一个角色'))
        } else {
          callback()
        }
      }
    }
  ],
  recipient_departments: [
    {
      required: true,
      message: '请选择至少一个部门',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (form.notification_type === 'department' && (!value || value.length === 0)) {
          callback(new Error('请选择至少一个部门'))
        } else {
          callback()
        }
      }
    }
  ],
  recipient_ids: [
    {
      required: true,
      message: '请选择至少一个接收人',
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (form.notification_type === 'specific' && (!value || value.length === 0)) {
          callback(new Error('请选择至少一个接收人'))
        } else {
          callback()
        }
      }
    }
  ]
}

const uploadUrl = computed(() => {
  return `${api.defaults.baseURL}/utils/upload/`
})

const uploadHeaders = computed(() => {
  return {
    'Authorization': `Bearer ${userStore.token}`
  }
})

const resetForm = () => {
  form.title = ''
  form.content = ''
  form.priority = 'normal'
  form.business_type = 'system'
  form.notification_type = 'specific'
  form.recipient_ids = []
  form.recipient_roles = []
  form.recipient_departments = []
  fileList.value = []
  uploadedFiles.value = []
}

// 监听编辑数据变化
watch(() => props.editData, (val) => {
  if (val) {
    form.title = val.title || ''
    form.content = val.content || ''
    form.priority = val.priority || 'normal'
    form.business_type = val.business_type || 'system'
    form.notification_type = val.notification_type || 'specific'
    form.recipient_ids = val.recipient_ids || []
    form.recipient_roles = val.recipient_roles || []
    form.recipient_departments = val.recipient_departments || []
    
    // 加载附件列表
    if (val.attachments) {
      fileList.value = val.attachments.map(att => ({
        name: att.filename,
        url: att.file_url,
        id: att.id
      }))
    }
  } else {
    resetForm()
  }
}, { immediate: true })

const fetchDepartments = async () => {
  try {
    const res = await api.get('/rbac/departments/')
    departmentOptions.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('获取部门列表失败', e)
  }
}

const searchUsers = async (query) => {
  if (query.length < 1) return
  userLoading.value = true
  try {
    const res = await api.get('/users/', {
      params: { search: query, page_size: 20 }
    })
    userOptions.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('搜索用户失败', e)
  } finally {
    userLoading.value = false
  }
}

const handleTypeChange = () => {
  form.recipient_ids = []
  form.recipient_roles = []
  form.recipient_departments = []
  
  if (form.notification_type === 'department') {
    fetchDepartments()
  }
}

const beforeUpload = (file) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

const handleUploadSuccess = (response, file) => {
  if (response.url || response.data?.url) {
    uploadedFiles.value.push({
      name: file.name,
      url: response.url || response.data?.url
    })
    ElMessage.success(`${file.name} 上传成功`)
  }
}

const handleUploadError = (error, file) => {
  ElMessage.error(`${file.name} 上传失败`)
}

const handleRemove = (file, fileList) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.name !== file.name)
}

const validateRecipients = () => {
  if (form.notification_type === 'specific' && form.recipient_ids.length === 0) {
    ElMessage.error('请选择至少一个接收人')
    return false
  }
  if (form.notification_type === 'role' && form.recipient_roles.length === 0) {
    ElMessage.error('请选择至少一个角色')
    return false
  }
  if (form.notification_type === 'department' && form.recipient_departments.length === 0) {
    ElMessage.error('请选择至少一个部门')
    return false
  }
  // 检查是否为系统通知或广播通知
  if (form.notification_type === 'system' || form.notification_type === 'broadcast') {
    return true
  }
  return true
}

const handleSaveDraft = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (!validateRecipients()) return
    
    saving.value = true
    try {
      const data = {
        title: form.title,
        content: form.content,
        priority: form.priority,
        business_type: form.business_type,
        notification_type: form.notification_type,
        recipient_ids: form.recipient_ids,
        recipient_roles: form.recipient_roles,
        recipient_departments: form.recipient_departments
      }
      
      if (props.editData) {
        await api.put(`/notifications/${props.editData.id}/`, data)
      } else {
        await api.post('/notifications/', data)
      }
      
      ElMessage.success('保存草稿成功')
      emit('success')
      dialogVisible.value = false
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const handleSend = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (!validateRecipients()) return
    
    sending.value = true
    try {
      let notificationId = props.editData?.id
      
      // 如果没有ID，先创建草稿
      if (!notificationId) {
        const createRes = await api.post('/notifications/', {
          title: form.title,
          content: form.content,
          priority: form.priority,
          business_type: form.business_type,
          notification_type: form.notification_type,
          recipient_ids: form.recipient_ids,
          recipient_roles: form.recipient_roles,
          recipient_departments: form.recipient_departments
        })
        // 直接从响应数据中获取ID
        notificationId = createRes.data.id
      } else {
        // 更新草稿
        await api.put(`/notifications/${notificationId}/`, {
          title: form.title,
          content: form.content,
          priority: form.priority,
          business_type: form.business_type,
          notification_type: form.notification_type,
          recipient_ids: form.recipient_ids,
          recipient_roles: form.recipient_roles,
          recipient_departments: form.recipient_departments
        })
      }
      
      // 发送通知
      await api.post(`/notifications/${notificationId}/send/`)
      
      ElMessage.success('发送成功')
      emit('success')
      dialogVisible.value = false
    } catch (e) {
      ElMessage.error(e.response?.data?.error || e.response?.data?.detail || '发送失败')
    } finally {
      sending.value = false
    }
  })
}

// 初始化
fetchDepartments()
</script>

<style scoped>
:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>
