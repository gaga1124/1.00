/**
 * 格式化工具函数
 */
import dayjs from 'dayjs'

/**
 * 格式化日期时间
 */
export const formatDateTime = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 */
export const formatDate = (date, format = 'YYYY-MM-DD') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化时间
 */
export const formatTime = (date, format = 'HH:mm:ss') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 相对时间（如：3天前）
 */
export const formatRelativeTime = (date) => {
  if (!date) return '-'
  return dayjs(date).fromNow()
}

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 格式化金额
 */
export const formatCurrency = (amount, currency = 'CNY') => {
  if (amount === null || amount === undefined) return '-'
  const formatter = new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: currency
  })
  return formatter.format(amount)
}

/**
 * 格式化数字（千分位）
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return '-'
  return new Intl.NumberFormat('zh-CN').format(num)
}

/**
 * 截断文本
 */
export const truncate = (text, length = 50, suffix = '...') => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + suffix
}

/**
 * 格式化手机号（中间4位隐藏）
 */
export const formatPhone = (phone) => {
  if (!phone) return '-'
  if (phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

/**
 * 格式化身份证号（中间隐藏）
 */
export const formatIdCard = (idCard) => {
  if (!idCard) return '-'
  if (idCard.length === 18) {
    return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
  }
  return idCard
}

/**
 * 获取状态文本
 */
export const getStatusText = (status, type = 'default') => {
  const statusMap = {
    default: {
      pending: '待处理',
      processing: '处理中',
      approved: '已通过',
      rejected: '已驳回',
      cancelled: '已取消',
      completed: '已完成'
    },
    approval: {
      pending: '待审批',
      approved: '已批准',
      rejected: '已驳回',
      cancelled: '已取消'
    }
  }
  
  const map = statusMap[type] || statusMap.default
  return map[status] || status
}
