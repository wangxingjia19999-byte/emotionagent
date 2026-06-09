// Storage 工具 — 对 uni.storage API 的轻量封装
export function getStorage(key, defaultValue = null) {
  try {
    const value = uni.getStorageSync(key)
    return value !== '' && value !== undefined ? value : defaultValue
  } catch {
    return defaultValue
  }
}

export function setStorage(key, value) {
  try {
    uni.setStorageSync(key, value)
    return true
  } catch {
    return false
  }
}

export function removeStorage(key) {
  try {
    uni.removeStorageSync(key)
    return true
  } catch {
    return false
  }
}

export function getJSON(key, defaultValue = null) {
  try {
    const raw = uni.getStorageSync(key)
    return raw ? JSON.parse(raw) : defaultValue
  } catch {
    return defaultValue
  }
}

export function setJSON(key, value) {
  try {
    uni.setStorageSync(key, JSON.stringify(value))
    return true
  } catch {
    return false
  }
}
