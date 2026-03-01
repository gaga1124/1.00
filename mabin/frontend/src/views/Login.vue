<template>
  <div class="login-container">
    <div class="login-background">
      <div class="background-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
    </div>
    
    <div class="login-content">
      <div class="login-box">
        <div class="login-header">
          <div class="logo-container">
            <div class="logo-icon">
              <el-icon :size="48"><School /></el-icon>
            </div>
            <h1>学院OA办公系统</h1>
            <p class="subtitle">College OA System</p>
          </div>
        </div>
        
        <div class="login-form">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名/学号/工号"
                size="large"
                prefix-icon="User"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <el-form-item>
              <div class="login-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <el-link type="primary" :underline="false" @click="showForgotPassword = true">
                  忘记密码？
                </el-link>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                @click="handleLogin"
                class="login-button"
                style="width: 100%"
              >
                {{ loading ? '登录中...' : '登录' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
    
    <!-- 忘记密码对话框 -->
    <el-dialog v-model="showForgotPassword" title="找回密码" width="400px">
      <el-form :model="forgotForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="forgotForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="forgotForm.phone" placeholder="请输入注册手机号" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="code-input-group">
            <el-input v-model="forgotForm.code" placeholder="请输入验证码" />
            <el-button @click="handleSendForgotCode">获取验证码</el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="forgotForm.newPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgotPassword = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  School, User, Lock,
  Document, OfficeBuilding, Tools
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const rememberMe = ref(false)
const showForgotPassword = ref(false)

const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const forgotForm = reactive({
  username: '',
  phone: '',
  code: '',
  newPassword: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await userStore.login(loginForm.username, loginForm.password)
        if (result.success) {
          ElMessage.success('登录成功')
          if (rememberMe.value) {
            localStorage.setItem('rememberedUsername', loginForm.username)
          } else {
            localStorage.removeItem('rememberedUsername')
          }
          router.push('/')
        } else {
          ElMessage.error(result.error || '登录失败')
        }
      } catch (error) {
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleSendForgotCode = () => {
  if (!forgotForm.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }
  ElMessage.success('验证码已发送')
}

const handleResetPassword = () => {
  if (!forgotForm.username || !forgotForm.phone || !forgotForm.code || !forgotForm.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  ElMessage.success('密码重置成功，请使用新密码登录')
  showForgotPassword.value = false
}

const rememberedUsername = localStorage.getItem('rememberedUsername')
if (rememberedUsername) {
  loginForm.username = rememberedUsername
  rememberMe.value = true
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.background-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -50px;
  animation-delay: 5s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  bottom: -50px;
  left: 20%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 40px;
  align-items: center;
}

.login-box {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 10px;
}

.login-header h1 {
  font-size: 28px;
  color: #303133;
  margin: 0;
  font-weight: 600;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin: 5px 0 0 0;
}

.login-tabs {
  margin-top: 20px;
}

.login-form {
  margin-top: 20px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.login-button {
  width: 100%;
  margin-top: 10px;
  height: 44px;
  font-size: 16px;
}

.login-footer {
  margin-top: 20px;
}

.social-login {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
}

.code-input-group {
  display: flex;
  gap: 10px;
}

.code-button {
  white-space: nowrap;
}

.login-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(10px);
}

.feature-item .el-icon {
  font-size: 24px;
}

@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    padding: 20px;
  }
  
  .login-box {
    width: 100%;
    max-width: 420px;
  }
  
  .login-features {
    flex-direction: row;
    flex-wrap: wrap;
    width: 100%;
    max-width: 420px;
  }
  
  .feature-item {
    flex: 1;
    min-width: 150px;
  }
}
</style>
