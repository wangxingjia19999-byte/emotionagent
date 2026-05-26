import request from './request'

export function getHomeOverview() {
  return request.get('/home/overview')
}