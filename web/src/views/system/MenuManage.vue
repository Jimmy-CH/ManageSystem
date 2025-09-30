<template>
  <el-card>
    <div slot="header" class="clearfix">
      <span>菜单管理</span>
      <el-button style="float: right;" type="primary" size="mini" @click="handleAddRoot">新增根菜单</el-button>
    </div>

    <!-- 树形菜单 -->
    <el-tree
      :data="treeData"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      :props="{ label: 'title', children: 'children' }"
      class="menu-tree"
    >
      <span slot-scope="{ node, data }" class="custom-tree-node">
        <span>
          <i v-if="data.icon" :class="data.icon" style="margin-right: 6px;" />
          {{ data.title }}
          <small v-if="data.path" style="color: #999; margin-left: 8px;">({{ data.path }})</small>
        </span>
        <span>
          <el-button type="text" size="mini" @click="handleAddChild(data)">+子菜单</el-button>
          <el-button type="text" size="mini" @click="handleEdit(data)">编辑</el-button>
          <el-button type="text" size="mini" style="color: #f56c6c" @click="handleDelete(data)">删除</el-button>
        </span>
      </span>
    </el-tree>

    <!-- 编辑/新增弹窗 -->
    <el-dialog
      :title="form.id ? '编辑菜单' : '新增菜单'"
      :visible.sync="dialogVisible"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="menuForm" :model="form" :rules="rules" label-width="80px">
        <el-form-item v-if="!isRoot" label="上级菜单">
          <el-tag>{{ parentTitle }}</el-tag>
        </el-form-item>
        <el-form-item label="菜单名称" prop="title">
          <el-input v-model="form.title" placeholder="如：用户管理" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="form.icon" placeholder="如：el-icon-user" />
          <small style="color: #999;">Element UI 图标类名，如 el-icon-setting</small>
        </el-form-item>
        <el-form-item label="路径" prop="path">
          <el-input v-model="form.path" placeholder="/user/list" />
        </el-form-item>
        <el-form-item label="组件路径" prop="component">
          <el-input v-model="form.component" placeholder="views/UserList.vue" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
          <el-input-number v-model="form.order" :min="0" :max="999" controls-position="right" />
        </el-form-item>
        <el-form-item label="是否启用">
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
import { menuApi } from '@/api/system'

export default {
  name: 'MenuManage',
  data() {
    return {
      treeData: [],
      dialogVisible: false,
      isRoot: true, // 是否为根菜单
      parentTitle: '',
      form: {
        id: null,
        title: '',
        icon: '',
        path: '',
        component: '',
        parent: null,
        order: 0,
        is_active: true
      },
      rules: {
        title: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
        path: [{ required: true, message: '请输入路径', trigger: 'blur' }],
        component: [{ required: true, message: '请输入组件路径', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.loadMenus()
  },
  methods: {
    async loadMenus() {
      try {
        const res = await menuApi.list()
        // 后端已返回嵌套结构，直接赋值
        this.treeData = res.data.results || []
      } catch (err) {
        this.$message.error('加载菜单失败')
        console.error(err)
      }
    },

    handleAddRoot() {
      this.isRoot = true
      this.parentTitle = ''
      this.form = {
        id: null,
        title: '',
        icon: '',
        path: '',
        component: '',
        parent: null,
        order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },

    handleAddChild(parentNode) {
      this.isRoot = false
      this.parentTitle = parentNode.title
      this.form = {
        id: null,
        title: '',
        icon: '',
        path: '',
        component: '',
        parent: parentNode.id,
        order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },

    handleEdit(node) {
      this.isRoot = !node.parent
      this.parentTitle = node.parent ? this.findNodeTitle(node.parent) : ''
      this.form = { ...node }
      this.dialogVisible = true
    },

    findNodeTitle(id) {
      const find = (nodes) => {
        for (const node of nodes) {
          if (node.id === id) return node.title
          if (node.children) {
            const found = find(node.children)
            if (found) return found
          }
        }
        return ''
      }
      return find(this.treeData)
    },

    async handleDelete(node) {
      try {
        await this.$confirm(`确定删除菜单 "${node.title}" 及其所有子菜单？`, '警告', {
          type: 'warning'
        })
        await menuApi.delete(node.id)
        this.$message.success('删除成功')
        this.loadMenus()
      } catch (e) {
        // 取消或错误
      }
    },

    submitForm() {
      this.$refs.menuForm.validate(async(valid) => {
        if (!valid) return
        try {
          if (this.form.id) {
            await menuApi.update(this.form.id, this.form)
          } else {
            await menuApi.create(this.form)
          }
          this.$message.success('保存成功')
          this.dialogVisible = false
          this.loadMenus()
        } catch (err) {
          this.$message.error('操作失败')
        }
      })
    },

    resetForm() {
      this.$refs.menuForm && this.$refs.menuForm.resetFields()
    }
  }
}
</script>

<style scoped>
.menu-tree {
  margin-top: 10px;
}
.custom-tree-node {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  padding: 4px 0;
}
</style>
