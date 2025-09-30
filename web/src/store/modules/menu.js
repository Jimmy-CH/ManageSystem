// src/store/modules/menu.js
import { menuApi } from '@/api/system'
import { connectMenuWebSocket, closeMenuWebSocket } from '@/utils/ws-menu'
import { Message } from 'element-ui' // 可替换为你用的 UI 库，如 ElMessage、ant-design-vue 等

const state = {
  menuTree: [], // 菜单树数据
  loading: false, // 加载状态
  wsConnected: false // WebSocket 是否已连接
}

const mutations = {
  SET_MENU_TREE(state, tree) {
    state.menuTree = tree
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_WS_CONNECTED(state, connected) {
    state.wsConnected = connected
  }
}

const actions = {
  // 初始化：加载菜单 + 连接 WebSocket
  async initMenu({ dispatch, commit }) {
    await dispatch('loadMenuTree')
    dispatch('connectWebSocket')
  },

  // 加载菜单树
  async loadMenuTree({ commit }) {
    commit('SET_LOADING', true)
    try {
      const response = await menuApi.list()
      commit('SET_MENU_TREE', response.data.results || [])
    } catch (error) {
      console.error('Failed to load menu tree:', error)
      Message.error('菜单加载失败')
      commit('SET_MENU_TREE', [])
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 连接 WebSocket 监听菜单变更
  connectWebSocket({ commit, dispatch }) {
    if (state.wsConnected) return

    connectMenuWebSocket((update) => {
      console.log('🔔 收到菜单更新通知:', update)
      Message.success({
        message: '系统菜单已更新，正在刷新...',
        duration: 2000
      })

      // 自动重新加载完整菜单树（简单可靠）
      dispatch('loadMenuTree')
    })

    commit('SET_WS_CONNECTED', true)
  },

  // 手动断开（可选，如登出时）
  disconnectWebSocket({ commit }) {
    closeMenuWebSocket()
    commit('SET_WS_CONNECTED', false)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
