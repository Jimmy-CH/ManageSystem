<template>
  <div class="app-container">
    <!-- 搜索与操作区域 -->
    <div class="filter-container">
      <el-input
        v-model="listQuery.name"
        placeholder="Name"
        clearable
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.importance"
        placeholder="Imp"
        clearable
        style="width: 90px"
        class="filter-item"
      >
        <el-option
          v-for="item in importanceOptions"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-select
        v-model="listQuery.status"
        placeholder="Status"
        clearable
        class="filter-item"
        style="width: 130px"
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="listQuery.ordering"
        style="width: 140px"
        class="filter-item"
        @change="handleFilter"
      >
        <el-option
          v-for="item in sortOptions"
          :key="item.key"
          :label="item.label"
          :value="item.key"
        />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        Add
      </el-button>
      <el-button
        v-waves
        :loading="downloadLoading"
        class="filter-item"
        type="primary"
        icon="el-icon-download"
        @click="handleExport"
      >
        Export
      </el-button>
      <el-checkbox v-model="showUpdated" class="filter-item" style="margin-left:15px;" @change="tableKey += 1">
        更新时间
      </el-checkbox>
    </div>

    <!-- 角色列表表格 -->
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @sort-change="sortChange"
    >
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="80" :class-name="getSortClass('id')">
        <template #default="{ row }">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="200px" align="center">
        <template #default="{ row }">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="描述" width="300px" align="center">
        <template #default="{ row }">
          <span style="color: red;">{{ row.description }}</span>
        </template>
      </el-table-column>
      <el-table-column label="权限" width="280px">
        <template #default="{ row }">
          <el-tag v-for="(item, index) in row.permissions" :key="index">{{ item.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" class-name="status-col" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status ? 'success' : 'danger'">
            {{ row.status ? "启用" : "未启用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Imp" width="180px">
        <template #default="{ row }">
          <svg-icon
            v-for="n in +row.importance"
            :key="n"
            icon-class="star"
            class="meta-item__icon"
          />
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_at" label="创建时间" width="250">
        <template #default="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.created_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="showUpdated" align="center" prop="updated_at" label="更新时间" width="250">
        <template #default="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.updated_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="330" class-name="small-padding fixed-width">
        <template #default="{ row, $index }">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            Edit
          </el-button>
          <el-button v-if="row.status !== 'deleted'" size="mini" type="danger" @click="handleDelete(row, $index)">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 编辑/新增弹窗 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="70px"
        style="width: 400px; margin-left: 50px;"
      >
        <el-form-item label="角色" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="temp.status" placeholder="Please select">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="权限" prop="permission_ids">
          <el-select
            v-model="temp.permission_ids"
            multiple
            placeholder="Please select"
            :loading="permissionLoading"
            @visible-change="handlePermissionDropdownVisibleChange"
          >
            <el-option
              v-for="item in permissionOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Imp">
          <el-rate
            v-model="temp.importance"
            :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
            :max="3"
            style="margin-top: 8px;"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="temp.description"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            placeholder="Please input"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmDialog">
          Confirm
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { roleApi } from '@/api/user'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'

export default {
  name: 'RolePage',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        importance: undefined,
        name: undefined,
        ordering: 'id',
        status: undefined
      },
      importanceOptions: [1, 2, 3],
      permissionOptions: [],
      permissionLoaded: false,
      permissionLoading: false,
      sortOptions: [
        { label: 'ID Ascending', key: 'id' },
        { label: 'ID Descending', key: '-id' }
      ],
      statusOptions: [
        { label: '启用', value: true },
        { label: '未启用', value: false }
      ],
      showUpdated: false,
      temp: {
        name: '',
        description: '',
        importance: 1,
        status: true,
        permission_ids: []
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      rules: {
        name: [{ required: true, message: 'name is required', trigger: 'blur' }],
        status: [{ required: true, message: 'status is required', trigger: 'change' }]
      },
      downloadLoading: false,
      rowID: null
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async handlePermissionDropdownVisibleChange(visible) {
      if (visible && !this.permissionLoaded) {
        this.permissionLoading = true
        try {
          const res = await roleApi.permissions()
          this.permissionOptions = res.data.data || []
          this.permissionLoaded = true
        } catch (error) {
          this.$message.error('获取权限列表失败')
        } finally {
          this.permissionLoading = false
        }
      }
    },

    async getList() {
      this.listLoading = true
      try {
        const response = await roleApi.list(this.listQuery)
        this.list = response.data.results || []
        this.total = response.data.count || 0
      } catch (error) {
        this.$message.error('获取角色列表失败')
        this.list = []
        this.total = 0
      } finally {
        this.listLoading = false
      }
    },

    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },

    resetTemp() {
      this.temp = {
        name: '',
        description: '',
        importance: 1,
        status: true,
        permission_ids: []
      }
    },

    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleUpdate(row) {
      // 深拷贝避免引用问题（特别是数组）
      this.temp = {
        name: row.name,
        description: row.description,
        importance: row.importance,
        status: row.status,
        permission_ids: [...(row.permission_ids || [])]
      }
      this.rowID = row.id
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    confirmDialog() {
      if (this.dialogStatus === 'create') {
        this.createData()
      } else {
        this.updateData()
      }
    },

    createData() {
      this.$refs['dataForm'].validate(async(valid) => {
        if (!valid) return
        try {
          await roleApi.create(this.temp)
          this.dialogFormVisible = false
          this.getList()
          this.$notify.success({ title: 'Success', message: 'Created Successfully', duration: 2000 })
        } catch (error) {
          this.$notify.error({ title: 'Error', message: '创建失败', duration: 2000 })
        }
      })
    },

    updateData() {
      this.$refs['dataForm'].validate(async(valid) => {
        if (!valid) return
        try {
          await roleApi.update(this.rowID, this.temp)
          this.dialogFormVisible = false
          this.getList()
          this.$notify.success({ title: 'Success', message: 'Update Successfully', duration: 2000 })
        } catch (error) {
          this.$notify.error({ title: 'Error', message: '更新失败', duration: 2000 })
        }
      })
    },

    async handleDelete(row, index) {
      try {
        await this.$confirm('此操作将永久删除该角色, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          center: true
        })
        await roleApi.delete(row.id)
        this.list.splice(index, 1)
        this.$notify.success({ title: '成功', message: '删除成功', duration: 2000 })
      } catch (error) {
        if (error !== 'cancel') {
          this.$notify.error({ title: '失败', message: '删除失败，请稍后重试', duration: 3000 })
        }
      }
    },

    async handleExport() {
      this.downloadLoading = true
      try {
        const res = await roleApi.export(this.listQuery)
        const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '角色列表.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.$message.error('导出失败')
      } finally {
        this.downloadLoading = false
      }
    },

    sortChange({ prop, order }) {
      if (prop === 'id') {
        this.listQuery.ordering = order === 'ascending' ? 'id' : '-id'
        this.handleFilter()
      }
    },

    getSortClass(key) {
      const sort = this.listQuery.ordering
      return sort === key ? 'ascending' : sort === `-${key}` ? 'descending' : ''
    }
  }
}
</script>

<style scoped>
.meta-item__icon {
  margin-right: 4px;
  color: #f7ba2a;
}
</style>
