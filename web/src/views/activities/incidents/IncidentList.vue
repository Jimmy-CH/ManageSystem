<!-- src/views/IncidentList.vue -->
<template>
  <div>
    <el-card>
      <div slot="header">
        <span>事件管理</span>
        <el-button style="float: right" type="primary" @click="handleCreate">新建事件</el-button>
      </div>

      <!-- 搜索条件 -->
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="标题">
          <el-input v-model="searchForm.title" placeholder="事件标题" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="tableData" style="width: 100%">
        <el-table-column prop="title" label="标题" width="200" />
        <el-table-column prop="category.name" label="分类" />
        <el-table-column prop="get_priority_display" label="优先级">
          <template slot-scope="scope">
            {{ priorityMap[scope.row.priority] }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template slot-scope="scope">
            {{ statusMap[scope.row.status] }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="occurred_at" label="发生时间" width="160">
          <template slot-scope="scope">
            {{ formatDate(scope.row.occurred_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleView(scope.row.id)">详情</el-button>
            <el-button size="mini" type="primary" @click="handleEdit(scope.row.id)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        :current-page="page"
        :page-size="10"
        layout="total, prev, pager, next"
        :total="total"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script>
import { incidentApi } from '@/api/incident'
import moment from 'moment'

export default {
  data() {
    return {
      loading: false,
      tableData: [],
      total: 0,
      page: 1,
      searchForm: {
        title: '',
        status: ''
      },
      statusOptions: [
        { value: 0, label: '待处理' },
        { value: 1, label: '处理中' },
        { value: 2, label: '已解决' },
        { value: 3, label: '已关闭' }
      ],
      priorityMap: { 1: 'P1', 2: 'P2', 3: 'P3', 4: 'P4' },
      statusMap: { 0: '待处理', 1: '处理中', 2: '已解决', 3: '已关闭' }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    formatDate(date) {
      return date ? moment(date).format('YYYY-MM-DD HH:mm') : ''
    },
    fetchData() {
      this.loading = true
      incidentApi.list({
        page: this.page,
        ...this.searchForm
      }).then(res => {
        this.tableData = res.data.results || []
        this.total = res.data.count || 0
      }).finally(() => {
        this.loading = false
      })
    },
    handlePageChange(page) {
      this.page = page
      this.fetchData()
    },
    resetSearch() {
      this.searchForm = { title: '', status: '' }
      this.fetchData()
    },
    handleView(id) {
      this.$router.push(`/incidents/${id}`)
    },
    handleEdit(id) {
      this.$router.push(`/incidents/${id}/edit`)
    },
    handleCreate() {
      this.$router.push('/incidents/create')
    }
  }
}
</script>
