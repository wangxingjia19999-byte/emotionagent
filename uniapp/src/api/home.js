import request from './request'

// ── 首页概览 ──────────────────────────────────
export const getHomeOverview = () => request.get('/home/overview')
