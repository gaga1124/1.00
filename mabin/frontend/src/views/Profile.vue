<template>
  <el-card>
    <template #header>
      <span>个人中心</span>
    </template>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="info">
        <el-form
          ref="infoFormRef"
          :model="infoForm"
          :rules="infoRules"
          label-width="120px"
          style="max-width: 600px"
        >
          <el-form-item label="用户名">
            <el-input v-model="userStore.user.username" disabled />
          </el-form-item>
          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="infoForm.real_name" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="infoForm.gender">
              <el-radio label="M">男</el-radio>
              <el-radio label="F">女</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="infoForm.phone" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="infoForm.email" />
          </el-form-item>
          <el-form-item label="头像">
            <el-upload
              :action="uploadUrl"
              :headers="uploadHeaders"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              :show-file-list="false"
            >
              <el-avatar :src="infoForm.avatar" :size="100">
                {{ userStore.user?.real_name?.[0] || 'U' }}
              </el-avatar>
              <template #tip>
                <div class="el-upload__tip">点击头像上传，支持jpg/png格式，大小不超过2MB</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleUpdateInfo" :loading="saving">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <el-tab-pane label="修改密码" name="password">
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="120px"
          style="max-width: 600px"
        >
          <el-form-item label="原密码" prop="old_password">
            <el-input v-model="passwordForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="passwordForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input v-model="passwordForm.confirm_password" type="password" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleChangePassword" :loading="saving">修改密码</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()

const userStore = useUserStore()
const activeTab = ref('info')
const saving = ref(false)

const infoFormRef = ref(null)
const passwordFormRef = ref(null)

const infoForm = reactive({
  real_name: userStore.user?.real_name || '',
  gender: userStore.user?.gender || '',
  phone: userStore.user?.phone || '',
  email: userStore.user?.email || '',
  avatar: userStore.user?.avatar || ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const infoRules = {
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
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

const handleAvatarSuccess = (response) => {
  if (response.success || response.url) {
    infoForm.avatar = response.url || response.data?.url
    ElMessage.success('头像上传成功')
  }
}

const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }
  return true
}

const handleUpdateInfo = async () => {
  if (!infoFormRef.value) return
  
  await infoFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await api.put('/users/me/', infoForm)
        await userStore.fetchUserInfo()
        ElMessage.success('信息更新成功')
      } catch (error) {
        ElMessage.error(error.response?.data?.message || error.response?.data?.detail || '更新失败')
        console.error(error)
      } finally {
        saving.value = false
      }
    }
  })
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        await api.post('/users/change-password/', {
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        })
        ElMessage.success('密码修改成功，请重新登录')
        passwordFormRef.value.resetFields()
        setTimeout(() => {
          userStore.logout()
          router.push('/login')
        }, 1500)
      } catch (error) {
        ElMessage.error(error.response?.data?.error || error.response?.data?.detail || '密码修改失败')
        console.error(error)
      } finally {
        saving.value = false
      }
    }
  })
}
</script>

<style scoped>
</style>
