<template>
  <el-card>
    <div slot="header">
      <span>分类管理</span>
      <el-button style="float:right" type="primary" @click="dialogVisible = true">新增分类</el-button>
    </div>

    <el-tree
      :data="treeData"
      node-key="id"
      default-expand-all
      :props="{ label: 'name', children: 'children' }"
    >
      <span slot-scope="{ node, data }" class="custom-tree-node">
        <span>{{ node.label }}</span>
        <span>
          <el-button type="text" size="mini" @click="editCategory(data)">编辑</el-button>
          <el-button type="text" size="mini" @click="deleteCategory(data.id)">删除</el-button>
        </span>
      </span>
    </el-tree>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="isEdit ? '编辑分类' : '新增分类'" :visible.sync="dialogVisible">
      <el-form ref="form" :model="form" label-width="80px" :rules="rules">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-cascader
            v-model="form.parent"
            :options="cascaderOptions"
            :props="{ checkStrictly: true, value: 'id', label: 'name', children: 'children' }"
            clearable
            placeholder="请选择父分类（可选）"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.order" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script>
import { categoryApi } from '@/api/category'

export default {
  data() {
    return {
      treeData: [],
      dialogVisible: false,
      isEdit: false,
      form: { name: '', parent: null, order: 0, is_active: true },
      rules: { name: [{ required: true, message: '请输入名称' }] },
      cascaderOptions: []
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      const res = await categoryApi.list()
      this.treeData = this.buildTree(res.data.results || [])
      this.cascaderOptions = this.buildTreeForCascader(res.data.results || [])
    },
    buildTree(list, parentId = null) {
      return list
        .filter(item => item.parent === parentId)
        .map(item => ({
          ...item,
          children: this.buildTree(list, item.id)
        }))
    },
    buildTreeForCascader(list) {
      const map = {}
      list.forEach(item => {
        map[item.id] = { ...item, children: [] }
      })
      const roots = []
      list.forEach(item => {
        if (item.parent) {
          if (map[item.parent]) map[item.parent].children.push(map[item.id])
        } else {
          roots.push(map[item.id])
        }
      })
      return roots
    },
    async submitForm() {
      // 关键修复：将 [] 转为 null
      const payload = {
        ...this.form,
        parent: Array.isArray(this.form.parent) && this.form.parent.length > 0
          ? this.form.parent[this.form.parent.length - 1] // 取最后一级 ID（级联选择）
          : null
      }

      // 如果你的 cascader 是单选（非级联路径），可能直接是 [id] 或 []
      // 更简单的方式（如果你只选一个节点）：
      // parent: this.form.parent && this.form.parent.length ? this.form.parent[0] : null
      try {
        if (this.isEdit) {
          await categoryApi.update(this.form.id, payload)
        } else {
          await categoryApi.create(payload)
        }
        this.$message.success('操作成功')
        this.dialogVisible = false
        this.fetchData()
      } catch (err) {
        this.$message.error('操作失败')
      }
    },
    editCategory(data) {
      this.isEdit = true
      this.form = { ...data, parent: data.parent || null }
      this.dialogVisible = true
    },
    async deleteCategory(id) {
      await this.$confirm('确定删除？')
      await categoryApi.delete(id)
      this.fetchData()
    }
  }
}
</script>

<style scoped>
.custom-tree-node {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
