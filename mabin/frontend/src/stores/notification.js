import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref([])
    const unreadCount = ref(0)
    const loading = ref(false)

    const fetchUnreadCount = async () => {
        try {
            const response = await api.get('/notifications/unread_count/')
            unreadCount.value = response.data.count
        } catch (error) {
            console.error('获取未读通知数量失败', error)
        }
    }

    const fetchNotifications = async () => {
        loading.value = true
        try {
            const response = await api.get('/notifications/')
            // 适配 DRF 分页
            notifications.value = response.data.results || response.data
        } catch (error) {
            console.error('获取通知列表失败', error)
        } finally {
            loading.value = false
        }
    }

    const markAsRead = async (id) => {
        try {
            await api.post(`/notifications/${id}/mark_read/`)
            // 更新本地状态
            const index = notifications.value.findIndex(n => n.id === id)
            if (index !== -1 && !notifications.value[index].is_read) {
                notifications.value[index].is_read = true
                unreadCount.value = Math.max(0, unreadCount.value - 1)
            }
        } catch (error) {
            console.error('标记已读失败', error)
        }
    }

    const markAllAsRead = async () => {
        try {
            await api.post('/notifications/mark_all_read/')
            notifications.value.forEach(n => n.is_read = true)
            unreadCount.value = 0
        } catch (error) {
            console.error('标记全部已读失败', error)
        }
    }

    const deleteNotification = async (id) => {
        try {
            await api.delete(`/notifications/${id}/`)
            const index = notifications.value.findIndex(n => n.id === id)
            if (index !== -1) {
                if (!notifications.value[index].is_read) {
                    unreadCount.value = Math.max(0, unreadCount.value - 1)
                }
                notifications.value.splice(index, 1)
            }
        } catch (error) {
            console.error('删除通知失败', error)
        }
    }

    return {
        notifications,
        unreadCount,
        loading,
        fetchUnreadCount,
        fetchNotifications,
        markAsRead,
        markAllAsRead,
        deleteNotification
    }
})
