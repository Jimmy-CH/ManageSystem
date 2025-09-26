
import request from '@/utils/request'

export const incidentApi = {
  list(params) {
    return request({
      url: '/events/incidents/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/events/incidents/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/events/incidents/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/events/incidents/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/events/incidents/${id}/`,
      method: 'delete'
    })
  },
  // ✅ 新增：获取事件关联的故障列表
  getFaults(incidentId) {
    return request({
      url: `/events/incidents/${incidentId}/faults/`,
      method: 'get'
    })
  }
}
