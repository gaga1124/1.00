/**
 * 常量定义
 */

// 政治面貌
export const POLITICAL_STATUS = {
  MASSES: 'masses',
  MEMBER: 'member',
  ACTIVIST: 'activist',
  PROBATIONARY: 'probationary',
  PARTY_MEMBER: 'party_member'
}

export const POLITICAL_STATUS_OPTIONS = [
  { label: '群众', value: POLITICAL_STATUS.MASSES },
  { label: '团员', value: POLITICAL_STATUS.MEMBER },
  { label: '入党积极分子', value: POLITICAL_STATUS.ACTIVIST },
  { label: '预备党员', value: POLITICAL_STATUS.PROBATIONARY },
  { label: '正式党员', value: POLITICAL_STATUS.PARTY_MEMBER }
]

// 请假类型
export const LEAVE_TYPE = {
  SICK: 'sick',
  PERSONAL: 'personal',
  BUSINESS: 'business',
  OTHER: 'other'
}

export const LEAVE_TYPE_OPTIONS = [
  { label: '病假', value: LEAVE_TYPE.SICK },
  { label: '事假', value: LEAVE_TYPE.PERSONAL },
  { label: '因公', value: LEAVE_TYPE.BUSINESS },
  { label: '其他', value: LEAVE_TYPE.OTHER }
]

// 报销类别
export const REIMBURSEMENT_CATEGORY = {
  OFFICE: 'office',
  TRAVEL: 'travel',
  RESEARCH: 'research',
  OTHER: 'other'
}

export const REIMBURSEMENT_CATEGORY_OPTIONS = [
  { label: '办公费', value: REIMBURSEMENT_CATEGORY.OFFICE },
  { label: '差旅费', value: REIMBURSEMENT_CATEGORY.TRAVEL },
  { label: '科研费', value: REIMBURSEMENT_CATEGORY.RESEARCH },
  { label: '其他', value: REIMBURSEMENT_CATEGORY.OTHER }
]

// 资源类型
export const RESOURCE_TYPE = {
  MEETING_ROOM: 'meeting_room',
  LECTURE_HALL: 'lecture_hall',
  LABORATORY: 'laboratory',
  CLASSROOM: 'classroom',
  OTHER: 'other'
}

export const RESOURCE_TYPE_OPTIONS = [
  { label: '会议室', value: RESOURCE_TYPE.MEETING_ROOM },
  { label: '学术报告厅', value: RESOURCE_TYPE.LECTURE_HALL },
  { label: '实验室', value: RESOURCE_TYPE.LABORATORY },
  { label: '教室', value: RESOURCE_TYPE.CLASSROOM },
  { label: '其他', value: RESOURCE_TYPE.OTHER }
]

// 审批状态
export const APPROVAL_STATUS = {
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CANCELLED: 'cancelled'
}

// 流程状态
export const WORKFLOW_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  APPROVED: 'approved',
  REJECTED: 'rejected',
  CANCELLED: 'cancelled'
}

// 分页配置
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZES: [10, 20, 50, 100]
}

// 文件上传配置
export const FILE_UPLOAD = {
  MAX_SIZE: 10, // MB
  ALLOWED_TYPES: ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.xls', '.xlsx']
}

// 日期时间格式
export const DATE_FORMAT = {
  DATE: 'YYYY-MM-DD',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  TIME: 'HH:mm:ss'
}
