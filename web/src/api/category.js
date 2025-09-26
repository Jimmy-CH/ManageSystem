
import request from '@/utils/request'

export const categoryApi = {
  list(params) {
    return request({
      url: '/events/categories/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/events/categories/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/events/categories/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/events/categories/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/events/categories/${id}/`,
      method: 'delete'
    })
  }
}
