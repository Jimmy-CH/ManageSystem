<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { connectWebSocket, closeWebSocket } from '@/utils/websocket'
import { mapActions } from 'vuex'
export default {
  name: 'App',
  async created() {
    // 用户登录后才初始化（确保有权限）
    // if (this.$store.getters.isLoggedIn) {

    // }
    await this.initMenu()
    this.updateConfig()
  },
  beforeDestroy() {
    // 关闭连接
    closeWebSocket()
  },
  methods: {
    ...mapActions('menu', ['initMenu']),
    updateConfig() {
      connectWebSocket((configUpdate) => {
        console.log('收到配置更新:', configUpdate)

        if (configUpdate.action === 'updated') {
          this.$message.success('ws收到更新操作，系统配置已更新，部分功能可能需要刷新页面生效')
        }

        // 示例：刷新菜单
        if (configUpdate.key === 'menu' || configUpdate.action === 'menu_updated') {
        // this.$store.dispatch('loadMenu') // 重新加载菜单
          this.$message.success('菜单已更新')
        }

      // 示例：更新系统参数
      // this.$store.commit('UPDATE_SYSTEM_CONFIG', configUpdate)
      })
    }
  }
}
</script>
