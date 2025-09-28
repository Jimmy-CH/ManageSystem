<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
      :row-key="row => row.id"
    >
      <el-table-column align="center" label="ID" :width="COL_WIDTH.ID">
        <template #default="{ row }">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column :width="COL_WIDTH.NAME" align="center" label="名称">
        <template #default="{ row }">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column :width="COL_WIDTH.CODE" align="center" label="Code">
        <template #default="{ row }">
          <span>{{ row.codename }}</span>
        </template>
      </el-table-column>

      <el-table-column :width="COL_WIDTH.DESC" align="center" label="描述">
        <template #default="{ row }">
          <span>{{ row.description }}</span>
        </template>
      </el-table-column>

      <el-table-column :width="COL_WIDTH.CATEGORY" align="center" label="分类">
        <template #default="{ row }">
          <span>{{ row.category }}</span>
        </template>
      </el-table-column>

      <el-table-column label="状态" class-name="status-col" :width="COL_WIDTH.STATUS">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'danger'">
            {{ row.status ? "启用" : "未启用" }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Imp" :width="COL_WIDTH.IMP">
        <template #default="{ row }">
          <svg-icon
            v-for="n in +row.importance"
            :key="n"
            icon-class="star"
            class="meta-item__icon"
          />
        </template>
      </el-table-column>

      <el-table-column align="center" prop="created_at" label="创建时间" :width="COL_WIDTH.TIME">
        <template #default="{ row }">
          <i class="el-icon-time" />
          <span>{{ row.created_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" prop="updated_at" label="更新时间" :width="COL_WIDTH.TIME">
        <template #default="{ row }">
          <i class="el-icon-time" />
          <span>{{ row.updated_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column min-width="200px" label="Title">
        <template #default="{ row }">
          <div v-if="row.editing" class="edit-cell">
            <el-input v-model="row.editTitle" class="edit-input" size="small" />
            <div class="edit-actions">
              <el-button
                size="small"
                icon="el-icon-refresh"
                type="warning"
                @click="cancelEdit(row)"
              >
                Cancel
              </el-button>
              <el-button
                size="small"
                icon="el-icon-circle-check-outline"
                type="success"
                @click="confirmEdit(row)"
              >
                OK
              </el-button>
            </div>
          </div>
          <span v-else>{{ row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Actions" :width="COL_WIDTH.ACTIONS">
        <template #default="{ row }">
          <el-button
            v-if="!row.editing"
            type="primary"
            size="small"
            icon="el-icon-edit"
            @click="startEdit(row)"
          >
            Edit
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { permissionApi } from '@/api/user'

const COL_WIDTH = {
  ID: 80,
  NAME: 200,
  CODE: 200,
  DESC: 200,
  CATEGORY: 200,
  STATUS: 100,
  IMP: 80,
  TIME: 250,
  ACTIONS: 120
}

export default {
  name: 'PermissionPage',
  filters: {
    statusFilter(status) {
      return status ? 'success' : 'danger'
    }
  },
  data() {
    return {
      list: [],
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10
      },
      COL_WIDTH
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const { data } = await permissionApi.list(this.listQuery)
        this.list = data.map(item => ({
          ...item,
          editing: false,
          editTitle: item.title // 临时编辑值
        }))
      } catch (error) {
        console.error('Failed to fetch permissions:', error)
        this.$message.error('获取权限列表失败')
      } finally {
        this.listLoading = false
      }
    },
    startEdit(row) {
      row.editing = true
      row.editTitle = row.title // 初始化编辑值
    },
    cancelEdit(row) {
      row.editing = false
      this.$message.warning('标题已恢复为原始值')
    },
    confirmEdit(row) {
      // 这里可以调用 API 更新 title
      row.title = row.editTitle // 提交后更新原始值
      row.editing = false
      this.$message.success('标题已更新')
    }
  }
}
</script>

<style scoped>
.edit-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.edit-input {
  flex: 1;
}
.edit-actions {
  display: flex;
  gap: 4px;
}
</style>
