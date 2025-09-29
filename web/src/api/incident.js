
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
  getFaults(incidentId) {
    return request({
      url: `/events/incidents/${incidentId}/faults/`,
      method: 'get'
    })
  },
  generalStatistics() {
    return request({
      url: '/events/incidents/statistics/general/',
      method: 'get'
    })
  },
  statsByCategory() {
    return request({
      url: '/events/incidents/statistics/by-category/',
      method: 'get'
    })
  },
  statsByPriority() {
    return request({
      url: '/events/incidents/statistics/by-priority/',
      method: 'get'
    })
  },
  incidentTrend() {
    return request({
      url: '/events/incidents/statistics/trend/',
      method: 'get'
    })
  }
}

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
