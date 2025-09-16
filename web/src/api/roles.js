import request from '@/utils/request'

export function getRoles(params) {
  return request({
    url: '/users/roles/',
    method: 'get',
    params
  })
}

export function createRole(data) {
  return request({
    url: '/users/roles/',
    method: 'post',
    data
  })
}

export function updateRole(id, data) {
  return request({
    url: `/users/roles/${id}/`,
    method: 'put',
    data
  })
}

export function deleteRole(id) {
  return request({
    url: `/users/roles/${id}/`,
    method: 'delete'
  })
}

export function getRolePermissions() {
  return request({
    url: `/users/permissions/all/`,
    method: 'get'
  })
}

export function exportRoles(params) {
  return request({
    url: '/users/roles/export/',
    method: 'get',
    params,
    responseType: 'blob' // ← 关键！下载文件
  })
}
