// 表单校验工具
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export function isValidPassword(password) {
  // 至少 8 位，包含字母和数字
  return password.length >= 8 && /[a-zA-Z]/.test(password) && /\d/.test(password)
}

export function isValidVerificationCode(code) {
  return /^\d{6}$/.test(code)
}

export function isNotEmpty(value) {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  return true
}

export function isValidPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}
