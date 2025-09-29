<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.username"
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
          v-for="(item, index) in statusOptions"
          :key="index"
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
    </div>

    <el-table
      ref="dragTable"
      v-loading="listLoading"
      :data="list"
      row-key="id"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column align="center" label="ID" width="80">
        <template slot-scope="{ row }">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="用户" width="100" align="center" prop="username" />
      <el-table-column label="电话" width="150" align="center" prop="phone" />
      <el-table-column label="邮箱" width="200" align="center" prop="email" />
      <el-table-column label="部门" width="200" align="center" prop="department" />
      <el-table-column label="职位" width="200" align="center" prop="position" />
      <el-table-column label="状态" class-name="status-col" width="100">
        <template slot-scope="{ row }">
          <el-tag :type="row.status | statusFilter">
            {{ row.status ? "启用" : "未启用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="200" align="center">
        <template slot-scope="scope">
          <el-tag
            v-for="(item, index) in scope.row.roles"
            :key="index"
            size="small"
            type="primary"
            style="cursor: pointer; margin: 2px;"
            @click="showPermissions(item)"
          >
            {{ item.name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Imp" width="100px">
        <template slot-scope="{ row }">
          <svg-icon
            v-for="n in +row.importance"
            :key="n"
            icon-class="star"
            class="meta-item__icon"
          />
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created_at" label="创建时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.created_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="updated_at" label="更新时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.updated_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="Drag" width="80">
        <template slot-scope>
          <svg-icon class="drag-handler" icon-class="drag" />
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="330" class-name="small-padding fixed-width">
        <template slot-scope="{ row, $index }">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            Edit
          </el-button>
          <el-button v-if="row.status !== 'deleted'" size="mini" type="danger" @click="handleDelete(row, $index)">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!-- 权限弹窗 -->
    <el-dialog
      :title="`角色「${selectedRole.name}」的权限列表`"
      :visible.sync="dialogVisible"
      width="400px"
    >
      <div v-if="selectedRole.permissions && selectedRole.permissions.length">
        <el-tag
          v-for="(perm, idx) in selectedRole.permissions"
          :key="idx"
          size="small"
          style="margin: 4px;"
          type="success"
        >
          {{ perm.name || perm.codename }}
        </el-tag>
      </div>
      <div v-else style="color: #999; text-align: center;">
        该角色暂无权限
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">关 闭</el-button>
      </span>
    </el-dialog>

    <!-- 用户弹窗 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="formRules"
        :model="temp"
        label-position="left"
        label-width="70px"
        style="width: 400px; margin-left: 50px;"
      >
        <el-form-item label="用户" prop="username">
          <el-input v-model="temp.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="temp.password" :placeholder="dialogStatus === 'update' ? '留空则不修改' : ''" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="temp.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="temp.department" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="temp.position" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="temp.status" class="filter-item" placeholder="请选择">
            <el-option
              v-for="(item, index) in statusOptions"
              :key="index"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
          <el-select
            v-model="temp.role_ids"
            class="filter-item"
            multiple
            placeholder="请选择"
            :loading="selectLoading"
            @visible-change="handleDropdownVisibleChange"
          >
            <el-option
              v-for="(item, index) in roleOptions"
              :key="index"
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
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          Confirm
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { userApi } from '@/api/user'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import Sortable from 'sortablejs'

const STATUS_OPTIONS = [
  { label: '启用', value: true },
  { label: '未启用', value: false }
]

export default {
  name: 'UserPage',
  components: { Pagination },
  directives: { waves },
  filters: {
    statusFilter(status) {
      return status ? 'success' : 'danger'
    }
  },
  data() {
    return {
      dialogVisible: false,
      selectedRole: { name: '', permissions: [] },
      importanceOptions: [1, 2, 3, 4, 5],
      statusOptions: STATUS_OPTIONS,
      sortOptions: [
        { label: 'ID Ascending', key: 'id' },
        { label: 'ID Descending', key: '-id' }
      ],
      textMap: { update: 'Edit', create: 'Create' },
      downloadLoading: false,
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        importance: undefined,
        username: undefined,
        ordering: 'id',
        status: undefined
      },
      sortable: null,
      temp: {},
      dialogFormVisible: false,
      dialogStatus: '',
      roleOptions: [],
      selectLoading: false,
      permissionLoaded: false
    }
  },
  computed: {
    formRules() {
      const rules = {
        username: [{ required: true, message: '用户名是必填项', trigger: 'blur' }]
      }
      if (this.dialogStatus === 'create') {
        rules.password = [{ required: true, message: '密码是必填项', trigger: 'blur' }]
      }
      return rules
    }
  },
  created() {
    this.getList()
  },
  beforeDestroy() {
    if (this.sortable) {
      this.sortable.destroy()
    }
  },
  methods: {
    showPermissions(role) {
      this.selectedRole = {
        name: role.name,
        permissions: role.permissions || []
      }
      this.dialogVisible = true
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    async getList() {
      this.listLoading = true
      try {
        const response = await userApi.list(this.listQuery)
        this.list = response.data.results || []
        this.total = response.data.count || 0
      } catch (error) {
        this.$message.error('获取用户列表失败')
        console.error(error)
      } finally {
        this.listLoading = false
        this.$nextTick(() => {
          if (!this.sortable) {
            this.setSort()
          }
        })
      }
    },
    setSort() {
      const el = this.$refs.dragTable?.$el.querySelector('.el-table__body-wrapper tbody')
      if (!el) return
      this.sortable = Sortable.create(el, {
        ghostClass: 'sortable-ghost',
        setData: (dataTransfer) => dataTransfer.setData('Text', ''),
        onEnd: (evt) => {
          const targetRow = this.list.splice(evt.oldIndex, 1)[0]
          this.list.splice(evt.newIndex, 0, targetRow)
          // TODO: 如需持久化排序，请在此调用 API
        }
      })
    },
    resetTemp() {
      this.temp = {
        username: '',
        password: '',
        phone: '',
        email: '',
        department: '',
        position: '',
        importance: 1,
        status: true,
        role_ids: []
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
    async createData() {
      this.$refs['dataForm'].validate(async(valid) => {
        if (!valid) return
        try {
          await userApi.create(this.temp)
          this.$message.success('创建成功')
          this.dialogFormVisible = false
          this.getList()
        } catch (error) {
          const msg = error.response?.data?.detail || error.message || '创建失败'
          this.$message.error(msg)
        }
      })
    },
    handleUpdate(row) {
      this.temp = {
        id: row.id,
        username: row.username,
        password: '', // 编辑时不传密码
        phone: row.phone,
        email: row.email,
        department: row.department,
        position: row.position,
        importance: row.importance,
        status: row.status,
        role_ids: (row.roles || []).map(r => r.id)
      }
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    async updateData() {
      this.$refs['dataForm'].validate(async(valid) => {
        if (!valid) return
        const payload = { ...this.temp }
        if (this.dialogStatus === 'update' && payload.password === '') {
          delete payload.password // 不更新密码
        }
        try {
          await userApi.update(payload.id, payload)
          this.$message.success('更新成功')
          this.dialogFormVisible = false
          this.getList()
        } catch (error) {
          const msg = error.response?.data?.detail || error.message || '更新失败'
          this.$message.error(msg)
        }
      })
    },
    async handleDropdownVisibleChange(visible) {
      if (visible && !this.permissionLoaded) {
        this.selectLoading = true
        try {
          const res = await userApi.roles()
          this.roleOptions = res.data.data || []
          this.permissionLoaded = true
        } catch (error) {
          this.$message.error('获取角色列表失败')
        } finally {
          this.selectLoading = false
        }
      }
    },
    async handleDelete(row, index) {
      try {
        await this.$confirm('此操作将永久删除该用户，是否继续？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          center: true
        })
        await userApi.delete(row.id)
        this.$notify.success({ title: '成功', message: '删除成功', duration: 2000 })
        this.list.splice(index, 1)
      } catch (error) {
        if (error !== 'cancel') {
          this.$notify.error({ title: '失败', message: '删除失败，请稍后重试', duration: 3000 })
        }
      }
    },
    async handleExport() {
      this.downloadLoading = true
      try {
        const res = await userApi.export(this.listQuery)
        const url = window.URL.createObjectURL(new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '用户列表.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.$message.error('导出失败')
        console.error(error)
      } finally {
        this.downloadLoading = false
      }
    }
  }
}
</script>

<style scoped>
.sortable-ghost {
  opacity: 0.8;
  color: #fff !important;
  background: #42b983 !important;
}
.drag-handler {
  width: 20px;
  height: 20px;
  cursor: pointer;
}
</style>
