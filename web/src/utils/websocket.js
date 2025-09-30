let ws = null

export function connectWebSocket(onMessage) {
  if (ws && ws.readyState === WebSocket.OPEN) return

  // console.log(process.env.VUE_APP_WS_URL)
  ws = new WebSocket(process.env.VUE_APP_WS_CONFIG)

  ws.onopen = () => {
    console.log('WebSocket connected')
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'config_update') {
      onMessage(data.data)
    }
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...')
    setTimeout(() => connectWebSocket(onMessage), 3000) // 自动重连
  }
}

export function closeWebSocket() {
  if (ws) ws.close()
}
