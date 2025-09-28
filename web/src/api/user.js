import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/users/login/',
    method: 'post',
    data
  })
}

export function getInfo() {
  return request({
    url: '/users/info/',
    method: 'get'
  })
}

export function logout(data) {
  return request({
    url: '/users/logout/',
    method: 'post',
    data
  })
}

export function getUsers(params) {
  return request({
    url: '/users/user/',
    method: 'get',
    params
  })
}

export function createUser(data) {
  return request({
    url: '/users/user/',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/users/user/${id}/`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/users/user/${id}/`,
    method: 'delete'
  })
}

export function getUserRoles() {
  return request({
    url: '/users/roles/all/',
    method: 'get'
  })
}

export function exportUsers(params) {
  return request({
    url: '/users/user/export/',
    method: 'get',
    params,
    responseType: 'blob' // ← 关键！下载文件
  })
}

export const permissionApi = {
  list(params) {
    return request({
      url: '/users/permissions/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/users/permissions/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/users/permissions/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/users/permissions/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/users/permissions/${id}/`,
      method: 'delete'
    })
  }
}

export const roleApi = {
  list(params) {
    return request({
      url: '/users/roles/',
      method: 'get',
      params
    })
  },
  create(data) {
    return request({
      url: '/users/roles/',
      method: 'post',
      data
    })
  },
  update(id, data) {
    return request({
      url: `/users/roles/${id}/`,
      method: 'put',
      data
    })
  },
  detail(id) {
    return request({
      url: `/users/roles/${id}/`,
      method: 'get'
    })
  },
  delete(id) {
    return request({
      url: `/users/roles/${id}/`,
      method: 'delete'
    })
  },
  permissions() {
    return request({
      url: `/users/permissions/all/`,
      method: 'get'
    })
  },
  export(params) {
    return request({
      url: '/users/roles/export/',
      method: 'get',
      params,
      responseType: 'blob' // ← 关键！下载文件
    })
  }
}
