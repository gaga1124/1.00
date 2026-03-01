# 组件文档

## 通用组件

### FileUpload
文件上传组件

**Props:**
- `modelValue` (Array): 文件列表
- `limit` (Number): 最大上传数量，默认10
- `maxSize` (Number): 最大文件大小(MB)，默认10
- `accept` (String): 允许的文件类型
- `multiple` (Boolean): 是否支持多选
- `disabled` (Boolean): 是否禁用
- `tip` (String): 提示文本

**Events:**
- `update:modelValue`: 文件列表更新

**Usage:**
```vue
<FileUpload
  v-model="files"
  :limit="5"
  :max-size="5"
  accept=".pdf,.jpg,.png"
/>
```

### DataTable
数据表格组件（增强版）

**Props:**
- `data` (Array): 表格数据
- `loading` (Boolean): 加载状态
- `showToolbar` (Boolean): 显示工具栏
- `showAdd` (Boolean): 显示新增按钮
- `showSearch` (Boolean): 显示搜索框
- `showSelection` (Boolean): 显示多选
- `showIndex` (Boolean): 显示序号
- `showPagination` (Boolean): 显示分页

**Slots:**
- `toolbar`: 自定义工具栏
- `default`: 表格列定义

**Events:**
- `add`: 新增事件
- `search`: 搜索事件
- `selection-change`: 选择变化
- `page-change`: 页码变化

**Usage:**
```vue
<DataTable
  :data="tableData"
  :loading="loading"
  @add="handleAdd"
>
  <el-table-column prop="name" label="姓名" />
</DataTable>
```

### StatusTag
状态标签组件

**Props:**
- `status` (String): 状态值
- `type` (String): 状态类型 (default, approval, booking, leave, reimbursement)
- `effect` (String): 效果 (light, dark, plain)
- `size` (String): 尺寸

**Usage:**
```vue
<StatusTag status="approved" type="approval" />
```
