<template>
  <div>
    <svg-icon
      :icon-class="isFullscreen ? 'exit-fullscreen' : 'fullscreen'"
      class="screenfull-svg"
      @click="toggleFullscreen"
    />
  </div>
</template>

<script>
import screenfull from 'screenfull'

export default {
  name: 'Screenfull',
  data() {
    return {
      isFullscreen: false
    }
  },
  mounted() {
    this.init()
  },
  beforeDestroy() {
    this.destroy()
  },
  methods: {
    toggleFullscreen() {
      if (!screenfull.isEnabled) {
        this.$message({
          message: 'Fullscreen is not supported in your browser.',
          type: 'warning'
        })
        return
      }
      screenfull.toggle()
    },
    onFullscreenChange() {
      this.isFullscreen = screenfull.isFullscreen
    },
    init() {
      if (screenfull.isEnabled) {
        screenfull.on('change', this.onFullscreenChange)
      }
    },
    destroy() {
      if (screenfull.isEnabled) {
        screenfull.off('change', this.onFullscreenChange)
      }
    }
  }
}
</script>

<style scoped>
.screenfull-svg {
  display: inline-block;
  cursor: pointer;
  fill: #5a5e66;
  width: 20px;
  height: 20px;
  vertical-align: middle; /* 更推荐用 middle 而不是固定 10px */
}
</style>
