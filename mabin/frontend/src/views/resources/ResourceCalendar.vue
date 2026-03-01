<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>资源预约日历</span>
        <div>
          <el-select v-model="selectedResource" placeholder="选择资源" style="width: 200px; margin-right: 10px">
            <el-option
              v-for="resource in resources"
              :key="resource.id"
              :label="resource.name"
              :value="resource.id"
            />
          </el-select>
          <el-button type="primary" @click="handleToday">今天</el-button>
          <el-button @click="handlePrevWeek">上一周</el-button>
          <el-button @click="handleNextWeek">下一周</el-button>
        </div>
      </div>
    </template>
    
    <div class="calendar-container" v-loading="loading">
      <div class="calendar-header">
        <div class="time-column">
          <div class="time-label">时间</div>
          <div class="time-slots">
            <div v-for="hour in 24" :key="hour" class="time-slot">
              {{ String(hour - 1).padStart(2, '0') }}:00
            </div>
          </div>
        </div>
        
        <div class="days-container">
          <div v-for="(day, index) in weekDays" :key="index" class="day-column">
            <div class="day-header">
              <div class="day-name">{{ day.name }}</div>
              <div class="day-date">{{ day.date }}</div>
              <!-- 占用率指示器 -->
              <div class="occupancy-indicator">
                <el-tooltip
                  :content="`当日占用率: ${getOccupancyRate(day.date)}%`"
                  placement="top"
                >
                  <div class="occupancy-bar">
                    <div 
                      class="occupancy-fill" 
                      :style="{ width: getOccupancyRate(day.date) + '%', backgroundColor: getOccupancyColor(getOccupancyRate(day.date)) }"
                    ></div>
                  </div>
                </el-tooltip>
              </div>
            </div>
            <div class="day-slots">
              <!-- 背景小时格 -->
              <div
                v-for="hour in 24"
                :key="hour"
                class="hour-slot"
                :class="getSlotClass(day.date, hour - 1)"
                @click="handleSlotClick(day.date, hour - 1)"
              ></div>
              
            <!-- 预约项（绝对定位） -->
              <el-popover
                v-for="booking in getBookingsForDay(day.date)"
                :key="booking.id"
                placement="right"
                :width="250"
                trigger="hover"
              >
                <template #reference>
                  <div
                    class="booking-item"
                    :style="getBookingStyle(booking)"
                    @click.stop="handleBookingClick(booking)"
                  >
                    <div class="booking-title">{{ booking.title }}</div>
                    <div class="booking-time">{{ formatTimeRange(booking) }}</div>
                  </div>
                </template>
                <div class="booking-detail-popover">
                  <h4 style="margin: 0 0 10px 0">{{ booking.title }}</h4>
                  <p><strong>申请人:</strong> {{ booking.applicant_name }}</p>
                  <p><strong>时间:</strong> {{ formatFullTime(booking) }}</p>
                  <p><strong>状态:</strong> 
                    <el-tag size="small" :type="getStatusType(booking.status)">
                      {{ booking.status_display }}
                    </el-tag>
                  </p>
                  <p v-if="booking.description"><strong>描述:</strong> {{ booking.description }}</p>
                </div>
              </el-popover>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 预约对话框 -->
    <el-dialog v-model="bookingDialogVisible" title="资源预约" width="600px">
      <el-form :model="bookingForm" label-width="100px">
        <el-form-item label="资源">
          <el-input :value="selectedResourceName" disabled />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="bookingForm.start_time"
            type="datetime"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="bookingForm.end_time"
            type="datetime"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="预约标题" required>
          <el-input v-model="bookingForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="bookingForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bookingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitBooking">提交</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/utils/api'

const loading = ref(false)
const selectedResource = ref(null)
const resources = ref([])
const bookings = ref([])
const currentWeek = ref(dayjs())
const bookingDialogVisible = ref(false)
const selectedSlot = ref(null)

const bookingForm = reactive({
  resource: null,
  title: '',
  description: '',
  start_time: null,
  end_time: null
})

const weekDays = computed(() => {
  const startOfWeek = currentWeek.value.startOf('week')
  const days = []
  for (let i = 0; i < 7; i++) {
    const day = startOfWeek.add(i, 'day')
    days.push({
      name: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][day.day()],
      date: day.format('YYYY-MM-DD')
    })
  }
  return days
})

const selectedResourceName = computed(() => {
  const resource = resources.value.find(r => r.id === selectedResource.value)
  return resource?.name || ''
})

const fetchResources = async () => {
  try {
    const response = await api.get('/resources/')
    resources.value = response.data.results || response.data
    if (resources.value.length > 0 && !selectedResource.value) {
      selectedResource.value = resources.value[0].id
    }
  } catch (error) {
    ElMessage.error('获取资源列表失败')
    console.error(error)
  }
}

const fetchBookings = async () => {
  if (!selectedResource.value) return
  
  loading.value = true
  try {
    const startDate = currentWeek.value.startOf('week').format('YYYY-MM-DD')
    const endDate = currentWeek.value.endOf('week').format('YYYY-MM-DD')
    
    const response = await api.get(`/resources/${selectedResource.value}/calendar/`, {
      params: {
        start_date: startDate,
        end_date: endDate
      }
    })
    bookings.value = response.data || []
  } catch (error) {
    ElMessage.error('获取预约数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getBookingsForDay = (date) => {
  return bookings.value.filter(booking => {
    return dayjs(booking.start_time).format('YYYY-MM-DD') === date
  })
}

const getSlotClass = (date, hour) => {
  const now = dayjs()
  const slotTime = dayjs(`${date} ${String(hour).padStart(2, '0')}:00:00`)
  
  if (slotTime.isBefore(now, 'hour')) {
    return 'past-slot'
  }
  return 'available-slot'
}

const getBookingStyle = (booking) => {
  const start = dayjs(booking.start_time)
  const end = dayjs(booking.end_time)
  
  // 计算在当天中的分钟偏移量
  const startOfDay = start.startOf('day')
  const startMinutes = start.diff(startOfDay, 'minute')
  const durationMinutes = end.diff(start, 'minute')
  
  // 每小时 40px，即每分钟 40/60 px
  const top = (startMinutes * 40) / 60
  const height = (durationMinutes * 40) / 60
  
  // 检查是否有冲突
  const isConflict = bookings.value.some(b => 
    b.id !== booking.id && 
    dayjs(b.start_time).isBefore(end) && 
    dayjs(b.end_time).isAfter(start)
  )
  
  let backgroundColor = '#409eff' // 默认蓝色
  if (booking.status === 'approved') backgroundColor = '#67c23a' // 绿色
  if (booking.status === 'pending') backgroundColor = '#e6a23c' // 黄色
  if (isConflict) backgroundColor = '#f56c6c' // 红色 (冲突优先显示)

  return {
    top: `${top}px`,
    height: `${height}px`,
    backgroundColor: backgroundColor,
    zIndex: isConflict ? 2 : 1,
    opacity: 0.85
  }
}

const formatTimeRange = (booking) => {
  return `${dayjs(booking.start_time).format('HH:mm')} - ${dayjs(booking.end_time).format('HH:mm')}`
}

const formatFullTime = (booking) => {
  return `${dayjs(booking.start_time).format('MM-DD HH:mm')} 至 ${dayjs(booking.end_time).format('HH:mm')}`
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getOccupancyRate = (date) => {
  const dayBookings = getBookingsForDay(date)
  if (dayBookings.length === 0) return 0
  
  // 计算总占用分钟数（简单累加，不考虑重叠，重叠在冲突检测中处理）
  let totalMinutes = 0
  dayBookings.forEach(booking => {
    const start = dayjs(booking.start_time)
    const end = dayjs(booking.end_time)
    totalMinutes += end.diff(start, 'minute')
  })
  
  // 假设工作时间是 08:00 - 22:00 (14小时 = 840分钟)
  const workMinutes = 14 * 60
  const rate = Math.round((totalMinutes / workMinutes) * 100)
  return Math.min(rate, 100)
}

const getOccupancyColor = (rate) => {
  if (rate < 30) return '#67C23A' // 绿色
  if (rate < 70) return '#E6A23C' // 黄色
  return '#F56C6C' // 红色
}

const checkConflict = (start, end) => {
  return bookings.value.some(booking => {
    const bStart = dayjs(booking.start_time)
    const bEnd = dayjs(booking.end_time)
    const s = dayjs(start)
    const e = dayjs(end)
    return s.isBefore(bEnd) && e.isAfter(bStart)
  })
}

const handleSlotClick = (date, hour) => {
  if (!selectedResource.value) {
    ElMessage.warning('请先选择资源')
    return
  }
  
  const start = `${date} ${String(hour).padStart(2, '0')}:00:00`
  const end = `${date} ${String(hour + 1).padStart(2, '0')}:00:00`
  
  if (checkConflict(start, end)) {
    ElMessage.warning('该时间段已有预约冲突')
    // 仍然允许打开对话框，但可以给个提示
  }
  
  selectedSlot.value = { date, hour }
  bookingForm.resource = selectedResource.value
  bookingForm.start_time = start
  bookingForm.end_time = end
  bookingForm.title = ''
  bookingForm.description = ''
  bookingDialogVisible.value = true
}

const handleBookingClick = (booking) => {
  const statusMap = {
    'pending': '待审批',
    'approved': '已批准',
    'rejected': '已驳回',
    'cancelled': '已取消'
  }
  ElMessage.info({
    message: `预约详情：${booking.title}\n申请人：${booking.applicant_name}\n状态：${statusMap[booking.status] || booking.status}`,
    duration: 5000,
    showClose: true
  })
}

const handleSubmitBooking = async () => {
  if (!bookingForm.title) {
    ElMessage.warning('请输入预约标题')
    return
  }
  
  try {
    await api.post('/resources/bookings/', bookingForm)
    ElMessage.success('预约提交成功')
    bookingDialogVisible.value = false
    fetchBookings()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '预约失败')
    console.error(error)
  }
}

const handleToday = () => {
  currentWeek.value = dayjs()
  fetchBookings()
}

const handlePrevWeek = () => {
  currentWeek.value = currentWeek.value.subtract(1, 'week')
  fetchBookings()
}

const handleNextWeek = () => {
  currentWeek.value = currentWeek.value.add(1, 'week')
  fetchBookings()
}

watch(selectedResource, () => {
  fetchBookings()
})

watch(currentWeek, () => {
  fetchBookings()
})

onMounted(() => {
  fetchResources()
})
</script>

<style scoped>
.calendar-container {
  overflow-x: auto;
}

.calendar-header {
  display: flex;
  min-width: 1200px;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
}

.time-label {
  height: 60px;
  line-height: 60px;
  text-align: center;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  font-weight: bold;
}

.time-slots {
  border-right: 1px solid #e4e7ed;
}

.time-slot {
  height: 40px;
  line-height: 40px;
  text-align: center;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #e4e7ed;
}

.days-container {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  min-width: 150px;
}

.day-header {
  height: 60px;
  text-align: center;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  padding: 10px;
}

.day-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.day-date {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.occupancy-indicator {
  margin-top: 5px;
}

.occupancy-bar {
  height: 4px;
  background-color: #ebeef5;
  border-radius: 2px;
  overflow: hidden;
}

.occupancy-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.day-slots {
  border-right: 1px solid #e4e7ed;
  position: relative;
  height: 960px; /* 24 * 40px */
}

.hour-slot {
  height: 40px;
  border-bottom: 1px solid #e4e7ed;
  box-sizing: border-box;
  cursor: pointer;
  transition: background-color 0.2s;
}

.hour-slot:hover {
  background-color: #f0f9ff;
}

.available-slot {
  background-color: #fff;
}

.past-slot {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.booking-item {
  position: absolute;
  left: 2px;
  right: 2px;
  padding: 4px 8px;
  color: #fff;
  font-size: 12px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.booking-title {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.booking-time {
  font-size: 10px;
  opacity: 0.9;
}

.booking-item:hover {
  opacity: 0.8;
}
</style>
