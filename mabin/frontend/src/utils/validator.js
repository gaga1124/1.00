/**
 * 表单验证工具
 */

/**
 * 验证手机号
 */
export const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号'))
  } else {
    callback()
  }
}

/**
 * 验证邮箱
 */
export const validateEmail = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入正确的邮箱地址'))
  } else {
    callback()
  }
}

/**
 * 验证身份证号
 */
export const validateIdCard = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入身份证号'))
  } else if (!/^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/.test(value)) {
    callback(new Error('请输入正确的身份证号'))
  } else {
    callback()
  }
}

/**
 * 验证学号
 */
export const validateStudentId = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入学号'))
  } else if (!/^\d{8,12}$/.test(value)) {
    callback(new Error('学号应为8-12位数字'))
  } else {
    callback()
  }
}

/**
 * 验证金额
 */
export const validateAmount = (rule, value, callback) => {
  if (value === null || value === undefined || value === '') {
    callback(new Error('请输入金额'))
  } else if (value <= 0) {
    callback(new Error('金额必须大于0'))
  } else if (value > 99999999.99) {
    callback(new Error('金额不能超过99999999.99'))
  } else {
    callback()
  }
}

/**
 * 验证文件大小
 */
export const validateFileSize = (maxSize = 10) => {
  return (rule, file, callback) => {
    if (!file) {
      callback()
    } else if (file.size / 1024 / 1024 > maxSize) {
      callback(new Error(`文件大小不能超过${maxSize}MB`))
    } else {
      callback()
    }
  }
}

/**
 * 验证文件类型
 */
export const validateFileType = (allowedTypes = ['.pdf', '.jpg', '.png']) => {
  return (rule, file, callback) => {
    if (!file) {
      callback()
    } else {
      const fileName = file.name.toLowerCase()
      const isValid = allowedTypes.some(type => fileName.endsWith(type.toLowerCase()))
      if (!isValid) {
        callback(new Error(`只支持${allowedTypes.join(', ')}格式的文件`))
      } else {
        callback()
      }
    }
  }
}

/**
 * 验证必填（用于动态表单）
 */
export const validateRequired = (message = '此字段为必填项') => {
  return { required: true, message, trigger: 'blur' }
}
