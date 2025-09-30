<template>
  <el-card>
    <div slot="header">
      <span>系统参数配置</span>
      <el-button style="float:right" type="primary" @click="handleAdd">新增</el-button>
    </div>
    <el-table v-loading="loading" :data="list">
      <el-table-column prop="key" label="键名" width="180" />
      <el-table-column prop="label" label="标签" />
      <el-table-column prop="value" label="值" />
      <el-table-column prop="type" label="类型" width="100" />
      <el-table-column prop="group" label="分组" width="120" />
      <el-table-column label="操作" width="150">
        <template #default="{row}">
          <el-button size="mini" @click="handleEdit(row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="form.id ? '编辑' : '新增'" :visible.sync="dialogVisible" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="键名">
          <el-input v-model="form.key" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.label" />
        </el-form-item>
        <el-form-item label="值">
          <el-input v-model="form.value" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option value="text" label="文本" />
            <el-option value="number" label="数字" />
            <el-option value="boolean" label="布尔" />
            <el-option value="textarea" label="多行文本" />
            <el-option value="image" label="图片" />
          </el-select>
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="form.group" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script>
import { systemConfigApi } from '@/api/system'

export default {
  name: 'SystemConfig',
  data() {
    return {
      list: [],
      loading: false,
      dialogVisible: false,
      form: { key: '', label: '', value: '', type: 'text', group: '' }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const res = await systemConfigApi.list()
        this.list = res.data.results || []
      } finally {
        this.loading = false
      }
    },
    handleAdd() {
      this.form = { key: '', label: '', value: '', type: 'text', group: '' }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.form = { ...row }
      this.dialogVisible = true
    },
    async handleDelete(id) {
      try {
        await this.$confirm('确定删除？')
        await systemConfigApi.delete(id)
        this.$message.success('删除成功')
        this.fetchData()
      } catch (e) {
        // 取消或错误
      }
    },
    async submit() {
      try {
        if (this.form.id) {
          await systemConfigApi.update(this.form.id, this.form)
        } else {
          await systemConfigApi.create(this.form)
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
