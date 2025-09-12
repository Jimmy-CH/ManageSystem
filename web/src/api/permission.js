import request from '@/utils/request'

export function getPermissions(params) {
  return request({
    url: '/users/permissions/',
    method: 'get',
    params
  })
}

export function createPermission(data) {
  return request({
    url: '/users/permissions/',
    method: 'post',
    data
  })
}

export function updatePermission(id, data) {
  return request({
    url: `/users/permissions/${id}/`,
    method: 'put',
    data
  })
}

export function deletePermission(id) {
  return request({
    url: `/users/permissions/${id}/`,
    method: 'delete'
  })
}
