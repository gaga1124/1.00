<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>财务报销申请</span>
        <el-button @click="$router.back()">返回</el-button>
      </div>
    </template>
    
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      style="max-width: 800px"
    >
      <el-form-item label="报销类别" prop="category">
        <el-select v-model="form.category" placeholder="请选择报销类别" style="width: 100%">
          <el-option label="办公费" value="office" />
          <el-option label="差旅费" value="travel" />
          <el-option label="科研费" value="research" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="报销标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入报销标题" />
      </el-form-item>
      
      <el-form-item label="报销金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :precision="2"
          :min="0.01"
          :step="100"
          style="width: 100%"
        >
          <template #prepend>¥</template>
        </el-input-number>
      </el-form-item>
      
      <el-form-item label="经费卡号" prop="fund_card_number">
        <el-input v-model="form.fund_card_number" placeholder="请输入经费卡号" />
        <div class="form-tip">可选，如有经费卡请填写</div>
      </el-form-item>
      
      <el-form-item label="报销描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="请详细说明报销事由和明细"
        />
      </el-form-item>
      
      <el-form-item label="发票附件" prop="invoices">
        <FileUpload
          v-model="form.invoices"
          :limit="10"
          accept=".pdf,.jpg,.jpeg,.png"
          tip="请上传发票扫描件或照片（PDF或图片格式）"
        />
        <div class="form-tip">至少上传一张发票，最多10张</div>
      </el-form-item>

      <el-form-item label="抄送给">
        <el-select
          v-model="form.cc_user_ids"
          multiple
          filterable
          remote
          reserve-keyword
          placeholder="请输入用户名搜索"
          :remote-method="searchUsers"
          :loading="userLoading"
          style="width: 100%"
        >
          <el-option
            v-for="item in userOptions"
            :key="item.id"
            :label="item.real_name || item.username"
            :value="item.id"
          />
        </el-select>
        <div class="form-tip">抄送对象将收到通知并可查看申请详情</div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">提交申请</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'
import FileUpload from '@/components/FileUpload.vue'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  category: '',
  title: '',
  amount: null,
  fund_card_number: '',
  description: '',
  invoices: [],
  cc_user_ids: []
})

const userOptions = ref([])
const userLoading = ref(false)

const searchUsers = async (query) => {
  if (query) {
    userLoading.value = true
    try {
      const response = await api.get('/users/', { params: { search: query } })
      userOptions.value = response.data.results || response.data
    } catch (error) {
      console.error(error)
    } finally {
      userLoading.value = false
    }
  } else {
    userOptions.value = []
  }
}

onMounted(() => {
  // Pre-load logic if needed
})

const rules = {
  category: [
    { required: true, message: '请选择报销类别', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入报销标题', trigger: 'blur' }
  ],
  amount: [
    { required: true, message: '请输入报销金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '报销金额必须大于0', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入报销描述', trigger: 'blur' },
    { min: 10, message: '报销描述至少10个字符', trigger: 'blur' }
  ],
  invoices: [
    { required: true, message: '请至少上传一张发票', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少上传一张发票', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      // 验证发票
      if (!form.invoices || form.invoices.length === 0) {
        ElMessage.warning('请至少上传一张发票')
        return
      }
      
      loading.value = true
      try {
        const data = {
          ...form,
          invoices: form.invoices.map(f => ({
            name: f.name,
            url: f.url,
            size: f.size,
            amount: form.amount / form.invoices.length // 平均分配金额（实际应该手动输入每张发票金额）
          }))
        }
        
        await api.post('/approval/reimbursement/', data)
        ElMessage.success('报销申请提交成功')
        router.push('/approval')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '提交失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  form.invoices = []
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
