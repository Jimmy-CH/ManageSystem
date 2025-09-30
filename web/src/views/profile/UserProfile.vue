<template>
  <div class="user-profile">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>个人资料</span>
      </div>

      <!-- 头像区域 -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          :action="''"
          :show-file-list="false"
          :before-upload="beforeAvatarUpload"
          :http-request="handleAvatarUpload"
          :disabled="uploading"
        >
          <img v-if="form.avatar" :src="getAvatarUrl(form.avatar)" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon" />
        </el-upload>

        <el-button
          v-if="form.avatar"
          type="danger"
          size="small"
          :loading="deleting"
          @click="removeAvatar"
        >
          删除头像
        </el-button>
      </div>

      <!-- 基本信息表单 -->
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="saving"
            @click="onSubmit"
          >
            保存
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { userApi } from '@/api/user' // 引入统一 API

export default {
  name: 'UserProfile',
  data() {
    // 手机号校验规则
    const validatePhone = (rule, value, callback) => {
      if (!value) {
        callback()
      } else if (!/^1[3-9]\d{9}$/.test(value)) {
        callback(new Error('请输入正确的手机号'))
      } else {
        callback()
      }
    }

    return {
      form: {
        id: null,
        username: '',
        phone: '',
        department: '',
        position: '',
        avatar: ''
      },
      rules: {
        phone: [{ validator: validatePhone, trigger: 'blur' }]
      },
      saving: false,
      uploading: false,
      deleting: false
    }
  },
  mounted() {
    this.loadUserData()
  },
  methods: {
    // 获取完整头像 URL（兼容相对路径）
    getAvatarUrl(avatar) {
      if (!avatar) return ''
      // 如果 avatar 是完整 URL（如 http://...），直接返回
      if (avatar.startsWith('http')) return avatar
      // 否则拼接后端 MEDIA_URL（假设为 /media/）
      return `${process.env.VUE_APP_AVATAR_URL}${avatar.startsWith('/') ? '' : '/'}${avatar}`
    },

    async loadUserData() {
      try {
        // 模拟从Vuex或API获取用户数据
        const user = this.$store.state.user.info // 假设用户信息存储在Vuex中
        this.form = { ...user }
      } catch (error) {
        this.$message.error('加载用户信息失败')
        console.error('Load user error:', error)
      }
    },

    async onSubmit() {
      this.$refs.formRef.validate(async(valid) => {
        if (!valid) return

        this.saving = true
        try {
          const res = await userApi.update(this.form.id, {
            username: this.form.username,
            phone: this.form.phone,
            department: this.form.department,
            position: this.form.position
          })
          this.$store.commit('user/SET_INFO', res.data)
          this.$message.success('保存成功')
        } catch (error) {
          this.$message.error('保存失败，请稍后再试')
        } finally {
          this.saving = false
        }
      })
    },

    resetForm() {
      this.$refs.formRef.resetFields()
      this.loadUserData()
    },

    beforeAvatarUpload(file) {
      const isJPGorPNG = ['image/jpeg', 'image/png'].includes(file.type)
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPGorPNG) {
        this.$message.error('头像仅支持 JPG/PNG 格式！')
      }
      if (!isLt2M) {
        this.$message.error('头像大小不能超过 2MB！')
      }
      return isJPGorPNG && isLt2M
    },

    async handleAvatarUpload(options) {
      this.uploading = true
      try {
        const res = await userApi.uploadAvatar(this.form.id, options.file)
        this.form.avatar = res.data.avatar
        this.$store.commit('user/SET_USER_INFO', { ...this.form })
        this.$message.success('头像上传成功')
      } catch (error) {
        this.$message.error('头像上传失败')
      } finally {
        this.uploading = false
      }
    },

    async removeAvatar() {
      try {
        await this.$confirm('确定要删除当前头像吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        this.deleting = true
        await userApi.deleteAvatar(this.form.id)
        this.form.avatar = ''
        this.$store.commit('user/SET_USER_INFO', { ...this.form })
        this.$message.success('头像删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('头像删除失败')
        }
      } finally {
        this.deleting = false
      }
    }
  }
}
</script>

<style scoped>
.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
}
.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100%;
  height: 100%;
  line-height: 178px;
  text-align: center;
}
.avatar {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
}
</style>
