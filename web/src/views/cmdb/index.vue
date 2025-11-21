<template>
  <div style="padding: 20px">
    <h2>CMDB 资产管理</h2>
    <el-table :data="assets" border style="width: 100%">
      <el-table-column prop="name" label="资产名称" width="180" />
      <el-table-column prop="ip" label="IP 地址" width="150" />
      <el-table-column prop="port" label="SSH 端口" width="120" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="primary"
            @click="openWebSSH(scope.row.id)"
          >
            WebSSH
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- WebSSH 弹窗 -->
    <el-dialog
      :visible.sync="sshVisible"
      title="WebSSH 终端"
      width="1200px"
      :before-close="handleClose"
    >
      <web-ssh-terminal
        v-if="currentAssetId"
        ref="terminal"
        :asset-id="currentAssetId"
      />
    </el-dialog>
  </div>
</template>

<script>
import WebSshTerminal from './components/WebSshTerminal.vue'
import { cmdbApi } from '@/api/cmdb'

export default {
  name: 'CmdbView',
  components: { WebSshTerminal },
  data() {
    return {
      assets: [],
      sshVisible: false,
      currentAssetId: null
    }
  },
  async mounted() {
    await this.loadAssets()
  },
  methods: {
    async loadAssets() {
      try {
        const res = await cmdbApi.list()
        this.assets = res.data.results || []
      } catch (err) {
        this.$message.error('加载资产失败')
        console.error(err)
      }
    },
    openWebSSH(assetId) {
      if (!Number.isInteger(assetId) || assetId <= 0) {
        this.$message.warning('无效的资产ID')
        return
      }
      // 弹窗
      // this.currentAssetId = assetId
      // this.sshVisible = true
      // 跳转到新页面
      this.$router.push(`/webssh/${assetId}`)
    },
    handleClose(done) {
      // 如果需要确认关闭，可在这里调用 done() 或取消
      this.sshVisible = false
      this.$nextTick(() => {
        this.currentAssetId = null
      })
      // WebSshTerminal 会在销毁时自动 disconnect（靠 beforeDestroy）
      done() // 👈 el-dialog 的 before-close 需要调用 done()
    }
  }
}
</script>
