// 常量定义
export const API_BASE_URL = 'http://127.0.0.1:8000/api'

export const MOOD_TAGS = [
  '开心', '难过', '焦虑', '愤怒', '温暖', '平静', '孤独', '恐惧', '惊讶', '感激',
]

export const POST_CATEGORIES = [
  '情绪倾诉', '学习生活', '人际关系', '校园日常', '其他',
]

export const ORDER_STATUS_MAP = {
  pending_payment: '待支付',
  paid: '已支付',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消',
}

export const ORDER_STATUS_COLOR = {
  pending_payment: '#faad14',
  paid: '#1890ff',
  shipped: '#7c6ff6',
  completed: '#52c41a',
  cancelled: '#8a8fa3',
}

export const SCALE_TYPES = {
  daily_mood: { name: '每日心情快评', count: 4 },
  phq9: { name: 'PHQ-9 抑郁筛查', count: 9 },
  gad7: { name: 'GAD-7 焦虑筛查', count: 7 },
}

export const EMOTION_COLORS = {
  '开心': '#ff9500',
  '难过': '#5b9cf5',
  '焦虑': '#ff6b6b',
  '愤怒': '#e74c3c',
  '温暖': '#ff9f43',
  '平静': '#6ec6a0',
  '孤独': '#95a5a6',
  '恐惧': '#9b59b6',
  '惊讶': '#f39c12',
  '感激': '#2ecc71',
}

export const CRISIS_HOTLINE = '400-161-9995'
