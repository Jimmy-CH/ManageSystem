<!-- src/components/WebSshTerminal.vue -->
<template>
  <div ref="terminalContainer" style="width: 100%; height: 100%; background: #000;" />
</template>

<script>
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

export default {
  name: 'WebSshTerminal',
  props: {
    assetId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      socket: null,
      term: null
    }
  },
  watch: {
    assetId(newId) {
      // 如果未来支持动态切换资产（当前每次新开弹窗）
      this.disconnect()
      this.$nextTick(() => {
        this.initTerminal()
        this.connectWebSocket()
      })
    }
  },
  mounted() {
    this.initTerminal()
    this.connectWebSocket()
  },
  beforeDestroy() {
    this.disconnect()
  },
  methods: {
    initTerminal() {
      this.term = new Terminal({
        cols: 120,
        rows: 30,
        theme: { background: '#000', foreground: '#fff' }
      })

      const fitAddon = new FitAddon()
      this.term.loadAddon(fitAddon)
      this.term.open(this.$refs.terminalContainer)
      fitAddon.fit()

      // 监听键盘输入并发送到后端
      this.term.onData(data => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.socket.send(data)
        }
      })
    },

    connectWebSocket() {
      console.log('Connecting to Menu WebSocket...', process.env.VUE_APP_WS_SSH)
      const wsUrl = `${process.env.VUE_APP_WS_SSH}${this.assetId}/`
      console.log(wsUrl)
      this.socket = new WebSocket(wsUrl)

      this.socket.onmessage = event => {
        if (this.term) {
          this.term.write(event.data)
        }
      }

      this.socket.onopen = () => {
        console.log('WebSocket connected')
        this.term?.write('\r\n✅ SSH 连接已建立\r\n')
      }

      this.socket.onerror = err => {
        console.error('WebSocket error:', err)
        this.term?.write('\r\n❌ 连接出错\r\n')
      }

      this.socket.onclose = () => {
        this.term?.write('\r\n🔌 连接已关闭\r\n')
      }
    },

    disconnect() {
      if (this.socket) {
        this.socket.close()
        this.socket = null
      }
      if (this.term) {
        this.term.dispose()
        this.term = null
      }
    }
  }
}
</script>
