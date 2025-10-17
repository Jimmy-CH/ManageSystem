import request from '@/utils/request'

export const recordApi = {
  list(params) {
    return request({
      url: '/record/process-records/',
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

export const summaryApi = {
  getCards(params) {
    return request({
      url: '/record/summary/cards/',
      method: 'get',
      params
    })
  },
  getUnitDistribution(params) {
    return request({
      url: '/record/summary/unit-distribution/',
      method: 'get',
      params
    })
  },
  getApplicantCount(params) {
    return request({
      url: '/record/summary/applicant-count/',
      method: 'get',
      params
    })
  }
}
