<template>
  <div class="avatar-upload">
    <div class="avatar-preview">
      <img :src="avatarUrl" alt="头像" @error="onImgError">
    </div>
    <div class="upload-btn">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleFileChange"
      >
      <el-button type="primary" @click="$refs.fileInput.click()">
        选择头像
      </el-button>
      <el-button
        v-if="avatarUrl"
        type="danger"
        style="margin-left: 10px"
        @click="removeAvatar"
      >
        删除头像
      </el-button>
    </div>
    <p class="tip">支持 jpg/png/gif，大小不超过 5MB</p>
  </div>
</template>

<script>
export default {
  name: 'AvatarUpload',
  data() {
    return {
      avatarUrl: '',
      defaultAvatar: require('@/assets/default-avatar.png') // 可选默认头像
    }
  },
  async mounted() {
    await this.loadAvatar()
  },
  methods: {
    async loadAvatar() {
      const user = this.$store.state.user // 假设你将用户信息存在 Vuex
      if (user && user.avatar) {
        this.avatarUrl = user.avatar.startsWith('http') ? user.avatar : (process.env.VUE_APP_BASE_API + user.avatar)
      } else {
        this.avatarUrl = this.defaultAvatar
      }
    },
    onImgError() {
      this.avatarUrl = this.defaultAvatar
    },
    handleFileChange(event) {
      const file = event.target.files[0]
      if (!file) return

      const formData = new FormData()
      formData.append('avatar', file)

      this.$axios({
        method: 'post',
        url: '/api/upload-avatar/',
        data: formData,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(res => {
          this.$message.success('头像上传成功')
          this.avatarUrl = res.data.avatar_url
          // 可选：更新 Vuex 中的用户信息
          this.$store.commit('SET_USER_AVATAR', res.data.avatar_url)
        })
        .catch(err => {
          this.$message.error(err.response?.data?.error || '上传失败')
        })
        .finally(() => {
          // 清空 input，确保下次选择相同文件也能触发 change
          this.$refs.fileInput.value = ''
        })
    },
    async removeAvatar() {
      await this.$confirm('确定要删除头像吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      try {
        await this.$axios.delete('/api/delete-avatar/') // 可选：实现删除接口
        this.avatarUrl = this.defaultAvatar
        this.$store.commit('SET_USER_AVATAR', null)
        this.$message.success('头像已删除')
      } catch (err) {
        this.$message.error('删除失败')
      }
    }
  }
}
</script>

<style scoped>
.avatar-upload {
  text-align: center;
}
.avatar-preview img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
}
.upload-btn {
  margin-top: 16px;
}
.tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
</style>
