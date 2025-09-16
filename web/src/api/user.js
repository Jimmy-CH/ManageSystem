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
