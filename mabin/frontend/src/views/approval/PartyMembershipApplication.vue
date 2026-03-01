<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>入党/入团申请</span>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </template>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="auto"
      class="application-form"
    >
      <el-alert
        title="申请须知"
        type="info"
        description="请如实填写申请信息并上传相关证明材料。申请提交后将进入审批流程，您可以在审批列表中查看进度。"
        show-icon
        style="margin-bottom: 20px"
      />

      <el-form-item label="申请类型" prop="application_type">
        <el-radio-group v-model="form.application_type">
          <el-radio label="party">入党申请</el-radio>
          <el-radio label="league">入团申请</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="申请书" prop="application_form">
        <FileUpload
          v-model="form.application_form"
          :limit="1"
          accept=".pdf,.doc,.docx"
          tip="请上传手写申请书的扫描件（PDF或图片）"
        />
      </el-form-item>
      
      <el-form-item label="思想汇报" prop="thought_reports">
        <FileUpload
          v-model="form.thought_reports"
          :limit="10"
          accept=".pdf,.doc,.docx"
          tip="可上传多份思想汇报"
        />
      </el-form-item>
      
      <el-form-item label="其他材料">
        <FileUpload
          v-model="form.other_materials"
          :limit="5"
          tip="可上传获奖证书、社会实践证明等"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">提交申请</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import FileUpload from '@/components/FileUpload.vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  application_type: 'party',
  application_form: '',
  thought_reports: [],
  other_materials: []
})

const rules = {
  application_type: [
    { required: true, message: '请选择申请类型', trigger: 'change' }
  ],
  application_form: [
    { required: true, message: '请上传申请书', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await ElMessageBox.confirm('确认提交申请吗？提交后将无法修改。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        loading.value = true
        // 注意：由于后端 PartyMembershipApplicationViewSet.perform_create 还没自动关联学生
        // 我们需要在前端传或者等后端完善。这里先尝试提交。
        const response = await api.post('/approval/party-applications/', form)
        ElMessage.success('申请提交成功')
        router.push('/approval')
      } catch (error) {
        if (error !== 'cancel') {
          console.error(error)
          ElMessage.error(error.response?.data?.detail || '提交失败，请检查输入')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.thought_reports = []
  form.other_materials = []
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
