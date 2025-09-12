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
