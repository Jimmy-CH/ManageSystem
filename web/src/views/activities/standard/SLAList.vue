<template>
  <el-card>
    <div slot="header">
      <span>SLA 标准管理</span>
      <el-button style="float:right" type="primary" @click="dialogVisible = true">新增 SLA</el-button>
    </div>

    <el-table :data="tableData">
      <el-table-column prop="level_name" label="等级名称" />
      <el-table-column prop="priority" label="优先级">
        <template slot-scope="scope">P{{ scope.row.priority }}</template>
      </el-table-column>
      <el-table-column prop="response_time" label="响应时限(小时)" />
      <el-table-column prop="resolve_time" label="解决时限(小时)" />
      <el-table-column label="操作" width="150">
        <template slot-scope="scope">
          <el-button size="mini" @click="edit(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="del(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="isEdit ? '编辑 SLA' : '新增 SLA'" :visible.sync="dialogVisible">
      <el-form ref="form" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="等级名称" prop="level_name">
          <el-input v-model="form.level_name" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="form.priority" placeholder="请选择">
            <el-option label="P1" :value="1" />
            <el-option label="P2" :value="2" />
            <el-option label="P3" :value="3" />
            <el-option label="P4" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="响应时限(小时)" prop="response_time">
          <el-input-number v-model="form.response_time" :min="0" :precision="1" />
        </el-form-item>
        <el-form-item label="解决时限(小时)" prop="resolve_time">
          <el-input-number v-model="form.resolve_time" :min="0" :precision="1" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" />
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
import { slaApi } from '@/api/sla'

export default {
  data() {
    return {
      tableData: [],
      dialogVisible: false,
      isEdit: false,
      form: {
        level_name: '',
        priority: 2,
        response_time: 2,
        resolve_time: 24,
        description: ''
      },
      rules: {
        level_name: [{ required: true }],
        priority: [{ required: true }],
        response_time: [{ required: true }],
        resolve_time: [{ required: true }]
      }
    }
  },
  async created() {
    const res = await slaApi.list()
    this.tableData = res.data.results || []
  },
  methods: {
    async submit() {
      try {
        if (this.isEdit) {
          await slaApi.update(this.form.id, this.form)
        } else {
          await slaApi.create(this.form)
        }
        this.$message.success('成功')
        this.dialogVisible = false
        const res = await slaApi.list()
        this.tableData = res.data
      } catch (err) {
        this.$message.error('失败')
      }
    },
    edit(row) {
      this.isEdit = true
      this.form = { ...row }
      this.dialogVisible = true
    },
    del(id) {
      this.$confirm('确定删除？').then(async() => {
        await slaApi.delete(id)
        this.tableData = this.tableData.filter(x => x.id !== id)
      })
    }
  }
}
</script>
