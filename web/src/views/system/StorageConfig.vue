<template>
  <el-card>
    <div slot="header">
      <span>存储配置</span>
      <el-button style="float:right" type="primary" @click="handleAdd">新增</el-button>
    </div>
    <el-table v-loading="loading" :data="list">
      <el-table-column prop="name" label="名称" />
      <el-table-column label="类型">
        <template #default="{row}">{{ typeMap[row.type] }}</template>
      </el-table-column>
      <el-table-column prop="base_url" label="域名" />
      <el-table-column label="默认">
        <template #default="{row}">
          <el-tag v-if="row.is_default" type="success">是</el-tag>
          <span v-else>否</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{row}">
          <el-button size="mini" @click="edit(row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="del(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="form.id ? '编辑' : '新增'" :visible.sync="dialogVisible" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" @change="onTypeChange">
            <el-option v-for="t in types" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="域名">
          <el-input v-model="form.base_url" />
        </el-form-item>
        <el-form-item label="默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>

        <div v-if="form.type === 'local'">
          <el-form-item label="上传路径">
            <el-input v-model="form.config.upload_path" />
          </el-form-item>
        </div>
        <div v-else-if="form.type === 'minio'">
          <el-form-item label="Endpoint">
            <el-input v-model="form.config.endpoint" />
          </el-form-item>
          <el-form-item label="AccessKey">
            <el-input v-model="form.config.access_key" />
          </el-form-item>
          <el-form-item label="SecretKey">
            <el-input v-model="form.config.secret_key" type="password" />
          </el-form-item>
          <el-form-item label="Bucket">
            <el-input v-model="form.config.bucket" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script>
import { storageConfigApi } from '@/api/system'

export default {
  name: 'StorageConfig',
  data() {
    return {
      list: [],
      loading: false,
      dialogVisible: false,
      form: {
        name: '',
        type: 'local',
        is_default: false,
        base_url: '',
        config: {}
      },
      types: [
        { value: 'local', label: '本地存储' },
        { value: 'minio', label: 'MinIO' }
      ],
      typeMap: {
        local: '本地存储',
        minio: 'MinIO'
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    onTypeChange(type) {
      const defaults = {
        local: { upload_path: '/uploads' },
        minio: { endpoint: '', access_key: '', secret_key: '', bucket: '' }
      }
      this.form.config = { ...defaults[type] }
    },
    async fetchData() {
      this.loading = true
      try {
        const res = await storageConfigApi.list()
        this.list = res.data.results || []
      } finally {
        this.loading = false
      }
    },
    handleAdd() {
      this.form = {
        name: '',
        type: 'local',
        is_default: false,
        base_url: '',
        config: { upload_path: '/uploads' }
      }
      this.dialogVisible = true
    },
    edit(row) {
      this.form = { ...row }
      this.dialogVisible = true
    },
    async del(id) {
      await this.$confirm('确定删除？')
      await storageConfigApi.delete(id)
      this.$message.success('删除成功')
      this.fetchData()
    },
    async save() {
      try {
        if (this.form.id) {
          await storageConfigApi.update(this.form.id, this.form)
        } else {
          await storageConfigApi.create(this.form)
        }
        this.$message.success('保存成功')
        this.dialogVisible = false
        this.fetchData()
      } catch (err) {
        this.$message.error('操作失败')
      }
    }
  }
}
</script>
