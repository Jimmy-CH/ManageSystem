
import request from '@/utils/request'

export const slaApi = {
  list(params) {
    return request({
      url: '/events/sla-standards/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/events/sla-standards/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/events/sla-standards/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/events/sla-standards/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/events/sla-standards/${id}/`,
      method: 'delete'
    })
  }
}
