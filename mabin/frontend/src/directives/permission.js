/**
 * 权限指令
 * 用法: v-permission="'student:edit'"
 */
import { useUserStore } from '@/stores/user'

const checkPermission = (el, binding) => {
  const userStore = useUserStore()
  const { value } = binding
  
  if (!value) {
    return
  }
  
  // 超级管理员拥有所有权限
  if (userStore.user?.is_superuser) {
    return
  }
  
  // TODO: 从用户权限列表中检查
  // 这里需要根据实际的权限系统实现
  const hasPermission = true // 临时返回true，实际应该检查用户权限
  
  if (!hasPermission) {
    el.style.display = 'none'
    // 或者移除元素
    // el.parentNode && el.parentNode.removeChild(el)
  }
}

export default {
  mounted(el, binding) {
    checkPermission(el, binding)
  },
  updated(el, binding) {
    checkPermission(el, binding)
  }
}
