/**
 * 数据导出工具
 */
import * as XLSX from 'xlsx'

/**
 * 导出Excel
 * @param {Array} data - 数据数组
 * @param {String} filename - 文件名
 * @param {Array} columns - 列配置 [{key: 'name', label: '姓名'}]
 */
import { ElMessage } from 'element-plus'

/**
 * 脱敏处理函数
 * @param {String} key - 字段名
 * @param {Any} value - 字段值
 * @returns {Any} 脱敏后的值
 */
const maskSensitiveData = (key, value) => {
  if (!value) return value
  const strValue = String(value)

  // 手机号 (包含 phone, mobile, tel)
  if (/phone|mobile|tel/i.test(key)) {
    return strValue.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
  }

  // 身份证 (包含 id_card, idcard, identity)
  if (/id_?card|identity/i.test(key)) {
    // 保留前6后4 (即使是15位也能大致匹配，这里主要针对18位)
    if (strValue.length > 10) {
      return strValue.replace(/^(\d{6}).+(\d{4})$/, '$1********$2')
    }
  }

  // 邮箱
  if (/email|mail/i.test(key)) {
    return strValue.replace(/(^.).*(@.*$)/, '$1***$2')
  }

  return value
}

/**
 * 格式化数据，处理日期等特殊字段
 * @param {Array} data - 原数据
 * @param {Array} columns - 列配置
 * @param {Object} options - 配置项 { mask: boolean }
 * @returns {Array} 格式化后的数据
 */
const formatData = (data, columns, options = {}) => {
  if (!data || !Array.isArray(data)) return []
  const shouldMask = options.mask !== false // 默认开启脱敏

  return data.map(item => {
    const row = {}

    // 如果指定了列配置
    if (columns && columns.length > 0) {
      columns.forEach(col => {
        let value = item[col.key]

        // 脱敏处理
        if (shouldMask) {
          value = maskSensitiveData(col.key, value)
        }

        // 简单的日期检测与处理
        if (value instanceof Date) {
          value = value.toLocaleString()
        }
        row[col.label] = value
      })
    } else {
      // 否则导出所有属性
      Object.keys(item).forEach(key => {
        let value = item[key]

        // 脱敏处理
        if (shouldMask) {
          value = maskSensitiveData(key, value)
        }

        if (value instanceof Date) {
          value = value.toLocaleString()
        }
        row[key] = value
      })
    }
    return row
  })
}

/**
 * 导出Excel
 * @param {Array} data - 数据数组
 * @param {String} filename - 文件名
 * @param {Array} columns - 列配置 [{key: 'name', label: '姓名'}]
 * @param {Object} options - 导出配置 { mask: boolean }
 */
export const exportToExcel = (data, filename = 'export.xlsx', columns = null, options = {}) => {
  try {
    if (!data || data.length === 0) {
      ElMessage.warning('暂无数据可导出')
      return
    }

    const exportData = formatData(data, columns, options)

    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)

    // 设置列宽
    const colWidths = columns ? columns.map(() => ({ wch: 15 })) : []
    ws['!cols'] = colWidths

    // 添加工作表
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')

    // 导出文件
    XLSX.writeFile(wb, filename)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export Excel Error:', error)
    ElMessage.error('导出Excel失败')
  }
}

/**
 * 导出CSV
 * @param {Array} data - 数据数组
 * @param {String} filename - 文件名
 * @param {Array} columns - 列配置
 * @param {Object} options - 导出配置 { mask: boolean }
 */
export const exportToCSV = (data, filename = 'export.csv', columns = null, options = {}) => {
  try {
    if (!data || data.length === 0) {
      ElMessage.warning('暂无数据可导出')
      return
    }

    const exportData = formatData(data, columns, options)

    // 获取表头
    const headers = columns ? columns.map(col => col.label) : Object.keys(exportData[0] || {})

    // 构建CSV内容
    let csvContent = headers.join(',') + '\n'

    exportData.forEach(row => {
      const values = headers.map(header => {
        const value = row[header] || ''
        // 处理包含逗号的值
        return `"${String(value).replace(/"/g, '""')}"`
      })
      csvContent += values.join(',') + '\n'
    })

    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    link.click()
    URL.revokeObjectURL(link.href)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export CSV Error:', error)
    ElMessage.error('导出CSV失败')
  }
}
