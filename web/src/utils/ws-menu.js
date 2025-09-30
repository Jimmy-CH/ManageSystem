// src/utils/ws-menu.js
let menuWs = null

export function connectMenuWebSocket(onUpdate) {
  if (menuWs?.readyState === WebSocket.OPEN) {
    console.log('Menu WebSocket already connected')
    return
  }
  console.log('Connecting to Menu WebSocket...', process.env.VUE_APP_WS_MENU)

  menuWs = new WebSocket(process.env.VUE_APP_WS_MENU)

  menuWs.onopen = () => {
    console.log('✅ Menu WebSocket connected')
  }

  menuWs.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'menu.update') {
        onUpdate(data)
      }
    } catch (e) {
      console.error('WebSocket message parse error:', e)
    }
  }

  menuWs.onclose = () => {
    console.log('🔌 Menu WebSocket disconnected. Reconnecting in 5s...')
    setTimeout(() => connectMenuWebSocket(onUpdate), 5000)
  }

  menuWs.onerror = (err) => {
    console.error('❌ Menu WebSocket error:', err)
    menuWs?.close()
  }
}

export function closeMenuWebSocket() {
  if (menuWs) {
    menuWs.close()
    menuWs = null
  }
}
