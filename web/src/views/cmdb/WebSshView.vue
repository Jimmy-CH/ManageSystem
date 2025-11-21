
<template>
  <div style="padding: 20px; height: calc(100vh - 40px);">
    <el-button icon="el-icon-arrow-left" @click="goBack">返回资产列表</el-button>
    <h2>WebSSH 终端 - {{ assetName || '加载中...' }}</h2>
    <div style="height: calc(100% - 60px); margin-top: 10px;">
      <web-ssh-terminal
        v-if="assetId"
        :asset-id="assetId"
        style="width: 100%; height: 100%;"
      />
    </div>
  </div>
</template>

<script>
import WebSshTerminal from './components/WebSshTerminal.vue'
import { cmdbApi } from '@/api/cmdb'

export default {
  name: 'WebSshView',
  components: { WebSshTerminal },
  data() {
    return {
      assetId: null,
      assetName: ''
    }
  },
  async mounted() {
    const id = parseInt(this.$route.params.assetId, 10)
    if (!id || id <= 0) {
      this.$message.error('无效的资产ID')
      this.$router.push('/cmdb')
      return
    }
    this.assetId = id
    await this.loadAssetName(id)
  },
  methods: {
    async loadAssetName(id) {
      try {
        const res = await cmdbApi.detail(id)
        console.log(res)
        this.assetName = res.data.name
      } catch (err) {
        console.warn('无法加载资产名称:', err)
      }
    },
    goBack() {
      this.$router.go(-1) // 或 this.$router.push('/cmdb')
    }
  },
  beforeRouteLeave(to, from, next) {
    // 可选：离开页面时提示确认（如连接中）
    next()
  }
}
</script>
