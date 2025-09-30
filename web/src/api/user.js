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
      responseType: 'blob'
    })
  }
}

export const userApi = {
  /**
   * 获取用户列表（支持分页、搜索、过滤）
   * @param {Object} params - 查询参数（如 page, page_size, search, ordering 等）
   */
  list(params) {
    return request({
      url: '/users/user/',
      method: 'get',
      params
    })
  },

  /**
   * 获取单个用户详情
   * @param {number} id - 用户ID
   */
  detail(id) {
    return request({
      url: `/users/user/${id}/`,
      method: 'get'
    })
  },

  /**
   * 创建新用户
   * @param {Object} data - 用户数据（含 username, password, phone 等）
   */
  create(data) {
    return request({
      url: '/users/user/',
      method: 'post',
      data
    })
  },

  /**
   * 更新用户信息（不含头像）
   * @param {number} id - 用户ID
   * @param {Object} data - 更新的数据
   */
  update(id, data) {
    return request({
      url: `/users/user/${id}/`,
      method: 'patch', // 或 'put'，根据后端实现
      data
    })
  },

  /**
   * 删除用户
   * @param {number} id - 用户ID
   */
  delete(id) {
    return request({
      url: `/users/user/${id}/`,
      method: 'delete'
    })
  },

  /**
   * 上传用户头像
   * @param {number} id - 用户ID
   * @param {File} file - 头像文件
   */
  uploadAvatar(id, file) {
    const formData = new FormData()
    formData.append('avatar', file)

    return request({
      url: `/users/user/${id}/upload-avatar/`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 删除用户头像
   * @param {number} id - 用户ID
   */
  deleteAvatar(id) {
    return request({
      url: `/users/user/${id}/delete-avatar/`,
      method: 'delete'
    })
  },

  /**
   * 导出用户数据（已有）
   * @param {Object} params - 导出条件（如过滤、搜索等）
   */
  export(params) {
    return request({
      url: '/users/user/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  roles() {
    return request({
      url: '/users/roles/all/',
      method: 'get'
    })
  }
}
