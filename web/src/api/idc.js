import request from '@/utils/request'

export const idcApi = {
  list(params) {
    return request({
      url: '/idc/devices/',
      method: 'get',
      params
    })
  },
  register(data) {
    return request({
      url: '/record/process-records/register/',
      method: 'post',
      data
    })
  },
  detail(id) {
    return request({
      url: `/record/process-records/${id}/`,
      method: 'get'
    })
  },
  logs(id) {
    return request({
      url: `/record/process-records/${id}/logs`,
      method: 'get'
    })
  },
  link(id, data) {
    return request({
      url: `/record/process-records/${id}/link/`,
      method: 'post',
      data
    })
  },
  enter(id, data) {
    return request({
      url: `/record/process-records/${id}/enter/`,
      method: 'post',
      data
    })
  },
  exit(id, data) {
    return request({
      url: `/record/process-records/${id}/exit/`,
      method: 'post',
      data
    })
  },
  export(params) {
    return request({
      url: '/record/process-records/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },
  OAInfo(params) {
    return request({
      url: '/record/oa-infos/',
      method: 'get',
      params
    })
  }
}
