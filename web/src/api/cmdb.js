import request from '@/utils/request'

export const cmdbApi = {
  list(params) {
    return request({
      url: '/cmdb/assets/',
      method: 'get',
      params
    })
  },
  detail(id) {
    return request({
      url: `/cmdb/assets/${id}/`,
      method: 'get'
    })
  },
  export(params) {
    return request({
      url: '/cmdb/assets/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  }
}
