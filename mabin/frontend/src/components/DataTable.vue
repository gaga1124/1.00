<template>
  <div class="data-table">
    <div class="table-header" v-if="showToolbar">
      <div class="table-toolbar">
        <slot name="toolbar">
          <el-button type="primary" @click="$emit('add')" v-if="showAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </slot>
      </div>
      <div class="table-search" v-if="showSearch">
        <el-input
          v-model="searchText"
          placeholder="搜索..."
          clearable
          @input="handleSearch"
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>
    
    <el-table
      :data="tableData"
      v-loading="loading"
      :stripe="stripe"
      :border="border"
      :height="height"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
      />
      <el-table-column
        v-if="showIndex"
        type="index"
        label="序号"
        width="60"
      />
      <slot></slot>
    </el-table>
    
    <div class="table-footer" v-if="showPagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  showAdd: {
    type: Boolean,
    default: true
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  showIndex: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  stripe: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: true
  },
  height: {
    type: [String, Number],
    default: null
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  }
})

const emit = defineEmits(['add', 'search', 'selection-change', 'sort-change', 'page-change', 'size-change'])

const searchText = ref('')
const tableData = ref(props.data)
const selectedRows = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

watch(() => props.data, (newData) => {
  tableData.value = newData
  pagination.total = newData.length
}, { immediate: true })

const handleSearch = (value) => {
  emit('search', value)
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

const handleSortChange = ({ column, prop, order }) => {
  emit('sort-change', { column, prop, order })
}

const handlePageChange = (page) => {
  pagination.page = page
  emit('page-change', page)
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  emit('size-change', size)
}

defineExpose({
  selectedRows,
  pagination
})
</script>

<style scoped>
.data-table {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-toolbar {
  display: flex;
  gap: 10px;
}

.table-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
