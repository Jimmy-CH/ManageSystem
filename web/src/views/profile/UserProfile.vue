<template>
  <div class="user-profile">
    <!-- 用户信息卡片 -->
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>个人资料</span>
      </div>

      <!-- 头像区域 -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          action=""
          :show-file-list="false"
          :before-upload="beforeAvatarUpload"
          :http-request="handleAvatarUpload"
        >
          <img v-if="form.avatar" :src="form.avatar" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon" />
        </el-upload>

        <el-button v-if="form.avatar" type="danger" size="small" @click="removeAvatar">删除头像</el-button>
      </div>

      <!-- 基本信息表单 -->
      <el-form ref="form" :model="form" label-width="100px">
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
          <el-button type="primary" @click="onSubmit">保存</el-button>
          <el-button @click="resetForm('form')">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      form: {
        username: '',
        phone: '',
        department: '',
        position: '',
        avatar: ''
      }
    }
  },
  mounted() {
    this.loadUserData()
  },
  methods: {
    // 初始化用户数据
    loadUserData() {
      // 模拟从Vuex或API获取用户数据
      const user = this.$store.state.user // 假设用户信息存储在Vuex中
      this.form = { ...user }
    },
    // 提交修改后的用户信息
    onSubmit() {
      this.$refs.form.validate(valid => {
        if (valid) {
          axios.patch('/api/users/' + this.form.id + '/', this.form)
            .then(response => {
              this.$message.success('保存成功')
              // 更新 Vuex 中的用户信息
              this.$store.commit('SET_USER_INFO', response.data)
            })
            .catch(error => {
              this.$message.error('保存失败，请稍后再试')
              console.error(error)
            })
        } else {
          this.$message.warning('请检查输入的信息')
          return false
        }
      })
    },
    // 重置表单
    resetForm(formName) {
      this.$refs[formName].resetFields()
      this.loadUserData() // 重新加载原始数据
    },
    // 上传头像前校验
    beforeAvatarUpload(file) {
      const isJPGorPNG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPGorPNG) {
        this.$message.error('上传头像只能是 JPG 或 PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传头像大小不能超过 2MB!')
      }
      return isJPGorPNG && isLt2M
    },
    // 自定义上传头像
    handleAvatarUpload(options) {
      const formData = new FormData()
      formData.append('avatar', options.file)

      axios.post('/api/users/' + this.form.id + '/avatar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }).then(response => {
        this.form.avatar = response.data.avatar
        this.$message.success('头像上传成功')
      }).catch(error => {
        this.$message.error('头像上传失败，请稍后再试')
        console.error(error)
      })
    },
    // 删除头像
    removeAvatar() {
      this.$confirm('确定要删除当前头像吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        axios.delete('/api/users/' + this.form.id + '/avatar/')
          .then(() => {
            this.form.avatar = ''
            this.$message.success('头像删除成功')
          }).catch(error => {
            this.$message.error('头像删除失败，请稍后再试')
            console.error(error)
          })
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    }
  }
}
</script>

<style scoped>
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}
.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>
