<template>
  <div>
    <h1>用户管理</h1>
    <div class="app-container">
      <el-table
        v-loading="listLoading"
        :data="list"
        element-loading-text="Loading"
        border
        fit
        highlight-current-row
      >
        <el-table-column align="center" label="ID" width="95">
          <template slot-scope="scope">
            {{ scope.$index }}
          </template>
        </el-table-column>
        <el-table-column label="用户" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.username }}
          </template>
        </el-table-column>
        <el-table-column label="头像" width="200" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.avatar }}</span>
          </template>
        </el-table-column>
        <el-table-column label="电话" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.phone }}
          </template>
        </el-table-column>
        <el-table-column label="邮箱" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.email }}
          </template>
        </el-table-column>
        <el-table-column label="部门" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.department }}
          </template>
        </el-table-column>
        <el-table-column label="职位" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.position }}
          </template>
        </el-table-column>
        <el-table-column label="是否活跃" width="200" align="center">
          <template slot-scope="scope">
            {{ scope.row.is_active }}
          </template>
        </el-table-column>
        <el-table-column label="角色" width="200" align="center" prop="roles">
          <template slot-scope="scope">
            <div v-for="(item, index) in scope.row.roles" :key="index">
              {{ item.name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column align="center" prop="created_at" label="创建时间" width="250">
          <template slot-scope="scope">
            <i class="el-icon-time" />
            <span>{{ scope.row.created_at }}</span>
          </template>
        </el-table-column>
        <el-table-column align="center" prop="updated_at" label="更新时间" width="250">
          <template slot-scope="scope">
            <i class="el-icon-time" />
            <span>{{ scope.row.updated_at }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { getUsers } from '@/api/user'
export default {
  name: 'UserIndex',
  data() {
    return {
      list: null,
      listLoading: true
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getUsers().then(response => {
        console.log(response)
        this.list = response.data
        this.listLoading = false
      })
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
