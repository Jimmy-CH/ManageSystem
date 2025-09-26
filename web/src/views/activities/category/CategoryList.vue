<template>
  <el-card>
    <div slot="header">
      <span>分类管理</span>
      <el-button style="float:right" type="primary" @click="handleAdd">新增分类</el-button>
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
      cascaderOptions: [],
      flatList: [], // 👈 新增：用于快速查找路径
      dialogVisible: false,
      isEdit: false,
      form: {
        name: '',
        parent: [], // 👈 必须是数组，供 cascader 使用
        order: 0,
        is_active: true
      },
      rules: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
      }
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    // 通用构建树方法（用于 tree 和 cascader）
    buildTree(list, parentId = null) {
      return list
        .filter(item => item.parent === parentId)
        .map(item => ({
          ...item,
          children: this.buildTree(list, item.id)
        }))
    },

    // 根据 parent ID 构建路径 [rootId, ..., parentId]
    findPathById(targetId) {
      if (!targetId) return []
      const idMap = {}
      this.flatList.forEach(item => {
        idMap[item.id] = item
      })

      const path = []
      let current = targetId
      while (current) {
        const node = idMap[current]
        if (!node) break
        path.unshift(current)
        current = node.parent // 继续向上找
      }
      return path
    },

    async fetchData() {
      try {
        const res = await categoryApi.list()
        // 兼容分页（DRF）和非分页
        const list = Array.isArray(res.data)
          ? res.data
          : (res.data?.results || [])

        this.flatList = list
        this.treeData = this.buildTree(list)
        this.cascaderOptions = this.buildTree(list) // ✅ 直接复用 buildTree
      } catch (err) {
        console.error('获取分类失败:', err)
        this.$message.error('加载分类失败')
      }
    },

    handleAdd() {
      this.isEdit = false
      this.form = {
        name: '',
        parent: [], // 空数组，cascader 可识别
        order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },

    editCategory(data) {
      this.isEdit = true
      // 👇 关键：将 parent ID 转为路径数组
      const parentPath = data.parent ? this.findPathById(data.parent) : []
      this.form = {
        ...data,
        parent: parentPath // cascader 需要数组
      }
      this.dialogVisible = true
    },

    async submitForm() {
      this.$refs.form.validate(async(valid) => {
        if (!valid) return

        // 👇 从路径数组中提取父级 ID（最后一个）
        const parentId = this.form.parent?.length
          ? this.form.parent[this.form.parent.length - 1]
          : null

        const payload = {
          name: this.form.name,
          parent: parentId, // ✅ 提交 ID 或 null
          order: this.form.order,
          is_active: this.form.is_active
        }

        try {
          if (this.isEdit) {
            await categoryApi.update(this.form.id, payload)
          } else {
            await categoryApi.create(payload)
          }
          this.$message.success(this.isEdit ? '更新成功' : '新增成功')
          this.dialogVisible = false
          await this.fetchData()
        } catch (err) {
          const msg = err?.response?.data?.message || '操作失败'
          this.$message.error(msg)
        }
      })
    },

    async deleteCategory(id) {
      try {
        await this.$confirm('确定删除该分类？', '提示', { type: 'warning' })
        await categoryApi.delete(id)
        this.$message.success('删除成功')
        await this.fetchData()
      } catch (err) {
        if (err !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
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
