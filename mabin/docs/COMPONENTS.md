# 组件使用指南

## 前端组件

### 1. FileUpload - 文件上传组件

通用的文件上传组件，支持多文件、类型验证、大小限制。

**示例：**
```vue
<template>
  <FileUpload
    v-model="files"
    :limit="5"
    :max-size="10"
    accept=".pdf,.jpg,.png"
    tip="支持PDF和图片格式，单个文件不超过10MB"
  />
</template>
```

### 2. DataTable - 数据表格组件

增强的数据表格组件，内置搜索、分页、工具栏等功能。

**示例：**
```vue
<template>
  <DataTable
    :data="students"
    :loading="loading"
    @add="handleAdd"
    @search="handleSearch"
  >
    <el-table-column prop="name" label="姓名" />
    <el-table-column prop="student_id" label="学号" />
  </DataTable>
</template>
```

### 3. StatusTag - 状态标签组件

统一的状态显示组件，自动根据状态类型显示不同颜色。

**示例：**
```vue
<StatusTag status="approved" type="approval" />
```

## 工具函数

### format.js - 格式化工具

提供日期、时间、文件大小、金额等格式化函数。

**示例：**
```javascript
import { formatDateTime, formatFileSize, formatCurrency } from '@/utils/format'

formatDateTime(new Date()) // "2024-01-01 12:00:00"
formatFileSize(1024) // "1 KB"
formatCurrency(1000) // "¥1,000.00"
```

### validator.js - 验证工具

提供常用的表单验证规则。

**示例：**
```javascript
import { validatePhone, validateEmail, validateFileSize } from '@/utils/validator'

// 在Element Plus表单中使用
rules: {
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  file: [{ validator: validateFileSize(10), trigger: 'change' }]
}
```

### constants.js - 常量定义

统一的常量定义，包括状态、类型、配置等。

**示例：**
```javascript
import { POLITICAL_STATUS_OPTIONS, LEAVE_TYPE_OPTIONS } from '@/utils/constants'

// 在组件中使用
<el-select v-model="form.political_status">
  <el-option
    v-for="option in POLITICAL_STATUS_OPTIONS"
    :key="option.value"
    :label="option.label"
    :value="option.value"
  />
</el-select>
```

### export.js - 导出工具

提供Excel和CSV导出功能。

**示例：**
```javascript
import { exportToExcel, exportToCSV } from '@/utils/export'

// 导出Excel
exportToExcel(data, '学生列表.xlsx', [
  { key: 'name', label: '姓名' },
  { key: 'student_id', label: '学号' }
])

// 导出CSV
exportToCSV(data, '学生列表.csv')
```

## 指令

### v-permission - 权限指令

根据用户权限控制元素显示。

**示例：**
```vue
<el-button v-permission="'student:edit'">编辑</el-button>
```

## 最佳实践

1. **组件复用**：优先使用通用组件，保持UI一致性
2. **工具函数**：使用统一的格式化函数，避免重复代码
3. **常量管理**：使用constants.js统一管理常量
4. **错误处理**：使用统一的错误处理机制
5. **类型检查**：使用TypeScript或PropTypes进行类型检查
