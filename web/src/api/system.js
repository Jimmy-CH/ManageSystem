import request from '@/utils/request'

export const systemConfigApi = {
  list(params) {
    return request({
      url: '/system/system-config/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/system/system-config/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/system/system-config/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/system/system-config/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/system/system-config/${id}/`,
      method: 'delete'
    })
  }
}

export const menuApi = {
  list(params) {
    return request({
      url: '/system/menu/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/system/menu/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/system/menu/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/system/menu/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/system/menu/${id}/`,
      method: 'delete'
    })
  }
}

export const storageConfigApi = {
  list(params) {
    return request({
      url: '/system/storage-config/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/system/storage-config/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/system/storage-config/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/system/storage-config/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/system/storage-config/${id}/`,
      method: 'delete'
    })
  }
}
