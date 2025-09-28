<template>
  <el-card>
    <div slot="header">
      <span>SLA 标准管理</span>
      <!-- 使用方法打开新增弹窗，而非直接设置 dialogVisible -->
      <el-button style="float:right" type="primary" @click="openCreateDialog">新增 SLA</el-button>
    </div>

    <el-table v-loading="loading" :data="tableData">
      <el-table-column prop="level_name" label="等级名称" />
      <el-table-column prop="priority_display" label="优先级" />
      <el-table-column prop="description" label="说明" />
      <el-table-column prop="response_time" label="响应时限(小时)" />
      <el-table-column prop="resolve_time" label="解决时限(小时)" />
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button size="mini" @click="openEditDialog(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="del(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      :title="isEdit ? '编辑 SLA' : '新增 SLA'"
      :visible.sync="dialogVisible"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="form" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="等级名称" prop="level_name">
          <el-input v-model="form.level_name" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择优先级">
            <el-option
              v-for="opt in priorityOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="响应时限(小时)" prop="response_time">
          <el-input-number v-model="form.response_time" :min="0" :precision="1" :step="0.5" />
        </el-form-item>
        <el-form-item label="解决时限(小时)" prop="resolve_time">
          <el-input-number v-model="form.resolve_time" :min="0" :precision="1" :step="1" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submit">保存</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script>
import { slaApi } from '@/api/sla'

export default {
  name: 'SLAStandardList',
  data() {
    return {
      tableData: [],
      loading: false,
      submitting: false,
      dialogVisible: false,
      isEdit: false,
      form: {
        id: null,
        level_name: '',
        priority: 2,
        response_time: 2,
        resolve_time: 24,
        description: ''
      },
      rules: {
        level_name: [{ required: true, message: '请输入等级名称', trigger: 'blur' }],
        priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
        response_time: [
          { required: true, message: '请输入响应时限', trigger: 'blur' },
          { type: 'number', message: '必须为数字' }
        ],
        resolve_time: [
          { required: true, message: '请输入解决时限', trigger: 'blur' },
          { type: 'number', message: '必须为数字' }
        ]
      },
      priorityOptions: [
        { value: 1, label: '低' },
        { value: 2, label: '中' },
        { value: 3, label: '高' },
        { value: 4, label: '紧急' },
        { value: 5, label: '测试' }
      ]
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const res = await slaApi.list()
        // 兼容 DRF 分页（有 results）和非分页（直接数组）
        this.tableData = res.data.results || res.data || []
      } catch (err) {
        this.$message.error('加载数据失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    openCreateDialog() {
      this.isEdit = false
      this.resetForm()
      this.dialogVisible = true
    },

    openEditDialog(row) {
      this.isEdit = true
      this.form = { ...row } // 深拷贝，避免引用
      this.dialogVisible = true
    },

    resetForm() {
      this.form = {
        id: null,
        level_name: '',
        priority: 2,
        response_time: 2,
        resolve_time: 24,
        description: ''
      }
      if (this.$refs.form) {
        this.$refs.form.clearValidate()
      }
    },

    async submit() {
      this.$refs.form.validate(async(valid) => {
        if (!valid) return
        const payload = { ...this.form }
        if (!this.isEdit) {
          delete payload.id // 👈 删除 id 字段
        }

        this.submitting = true
        try {
          if (this.isEdit) {
            await slaApi.update(payload.id, payload)
          } else {
            await slaApi.create(payload)
          }
          this.$message.success('操作成功')
          this.dialogVisible = false
          await this.fetchData() // 刷新列表
        } catch (err) {
          this.$message.error('操作失败')
          console.error(err)
        } finally {
          this.submitting = false
        }
      })
    },

    async del(id) {
      try {
        await this.$confirm('确定删除该 SLA 标准？此操作不可恢复。', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await slaApi.delete(id)
        this.$message.success('删除成功')
        await this.fetchData()
      } catch (err) {
        // 用户取消或接口错误，静默处理
      }
    }
  }
}
</script>

<style scoped>
/* 可选：微调样式 */
.el-card {
  margin: 16px;
}
</style>
