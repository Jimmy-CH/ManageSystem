<template>
  <div class="personnel-list">
    <!-- 搜索区域 -->
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" size="small">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.person_name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="人员类型">
          <el-select v-model="searchForm.person_type" placeholder="请选择" clearable>
            <el-option label="内部" :value="1" />
            <el-option label="外部" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件类型">
          <el-select v-model="searchForm.id_type" placeholder="请选择" clearable>
            <el-option label="身份证" :value="1" />
            <el-option label="护照" :value="2" />
            <!-- 可根据后端枚举扩展 -->
          </el-select>
        </el-form-item>
        <el-form-item label="证件号码">
          <el-input v-model="searchForm.id_number" placeholder="请输入证件号" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="searchForm.department" placeholder="请输入部门" clearable />
          <!-- 如果后端是下拉枚举，可改用 el-select -->
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.registration_status" placeholder="请选择" clearable>
            <el-option label="未入" :value="0" />
            <el-option label="已入" :value="1" />
            <el-option label="已出" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="门禁卡状态">
          <el-select v-model="searchForm.card_status" placeholder="请选择" clearable>
            <el-option label="已激活" :value="1" />
            <el-option label="已停用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="OA申请人">
          <el-input v-model="searchForm.applicant" placeholder="请输入OA申请人" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="handleSearch">搜索</el-button>
          <el-button size="small" @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮栏 -->
    <div class="action-bar">
      <el-button size="small" @click="exportData">导出</el-button>
      <el-button size="small" @click="openRegisterModal">入场登记</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column label="序号" width="60">
          <template #default="scope">
            {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="person_name" label="姓名" width="120" />
        <el-table-column prop="phone_number" label="电话" width="120" />
        <el-table-column prop="person_type_display" label="人员类型" width="100" />
        <el-table-column prop="id_type_display" label="证件类型" width="100" />
        <el-table-column prop="id_number" label="证件号码" width="180" />
        <el-table-column prop="unit" label="单位" width="150" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="registration_status_display" label="状态" width="100" />
        <el-table-column prop="apply_enter_time" label="申请进入时间" width="160" />
        <el-table-column prop="apply_leave_time" label="申请离开时间" width="160" />
        <el-table-column prop="entered_time" label="进入时间" width="160" />
        <el-table-column prop="exited_time" label="离开时间" width="160" />
        <el-table-column prop="change_user_name" label="操作人员" width="120" />
        <el-table-column prop="reason" label="出入原因" width="180" />
        <el-table-column prop="card_status_display" label="门禁卡状态" width="120" />
        <el-table-column prop="applicant" label="OA申请人" width="120" />
        <el-table-column prop="applicant_time" label="OA申请时间" width="160" />
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button size="mini" @click="showLogs(scope.row)">日志</el-button>
            <el-button size="mini" type="primary" @click="openEntryModal(scope.row)">入场</el-button>
            <el-button size="mini" type="danger" @click="openExitModal(scope.row)">离场</el-button>
            <el-button size="small" @click="openOaModal(scope.row)">关联OA</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页组件 -->
    <div class="pagination">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :current-page.sync="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 弹窗组件 -->
    <EntryModal
      :visible.sync="entryVisible"
      :personnel="currentPersonnel"
      @submit="handleEntrySubmit"
    />
    <ExitModal
      :visible.sync="exitVisible"
      :personnel="currentPersonnel"
      @submit="handleExitSubmit"
    />
    <LogModal
      :visible.sync="logVisible"
      :logs="logs"
    />
    <RegisterModal
      :visible.sync="registerVisible"
      @submit="handleRegisterSubmit"
    />
    <OaModal
      :visible.sync="oaModalVisible"
      @confirm="handleOaConfirm"
    />
  </div>
</template>

<script>
import LogModal from './LogModal.vue'
import EntryModal from './EntryModal.vue'
import ExitModal from './ExitModal.vue'
import RegisterModal from './RegisterModal.vue'
import OaModal from './OaModal.vue'
import { recordApi } from '@/api/record'

export default {
  name: 'PersonnelList',
  components: {
    LogModal,
    EntryModal,
    ExitModal,
    RegisterModal,
    OaModal
  },
  data() {
    return {
      searchForm: {
        person_name: '',
        person_type: null, // 1=内部, 2=外部
        id_type: null, // 1=身份证, 2=护照
        id_number: '',
        department: '',
        registration_status: null, // 0/1/2
        card_status: null,
        applicant: ''
      },
      tableData: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      detailVisible: false,
      logVisible: false,
      entryVisible: false,
      exitVisible: false,
      registerVisible: false,
      oaModalVisible: false,
      currentPersonnel: null,
      logs: []
    }
  },
  async created() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const res = await recordApi.list({
          ...this.searchForm,
          page: this.currentPage,
          limit: this.pageSize
        })
        this.tableData = res.data.results || []
        this.total = res.data.count || 0
      } catch (error) {
        this.$message.error('加载数据失败')
        console.error(error)
      }
    },

    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },

    resetSearch() {
      this.searchForm = {
        person_name: '',
        person_type: null,
        id_type: null,
        id_number: '',
        department: '',
        registration_status: null,
        card_status: null,
        applicant: ''
      }
      this.handleSearch()
    },

    async exportData() {
      try {
        const res = await recordApi.export(this.searchForm)
        const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = '人员记录.xlsx'
        a.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.$message.error('导出失败')
        console.error(error)
      }
    },

    openRegisterModal() {
      this.registerVisible = true
    },

    async handleRegisterSubmit(data) {
      try {
        await recordApi.register(data)
        this.$message.success('登记成功')
        this.registerVisible = false
        await this.loadData()
      } catch (error) {
        this.$message.error('登记失败')
        console.error(error)
      }
    },

    openEntryModal(row) {
      this.currentPersonnel = { ...row }
      this.entryVisible = true
    },

    async handleEntrySubmit(data) {
      try {
        await recordApi.enter(this.currentPersonnel.id, data)
        this.$message.success('入场成功')
        this.entryVisible = false
        await this.loadData()
      } catch (error) {
        this.$message.error('入场失败')
        console.error(error)
      }
    },

    openExitModal(row) {
      this.currentPersonnel = { ...row }
      this.exitVisible = true
    },

    async handleExitSubmit(data) {
      try {
        await recordApi.exit(this.currentPersonnel.id, data)
        this.$message.success('离场成功')
        this.exitVisible = false
        await this.loadData()
      } catch (error) {
        this.$message.error('离场失败')
        console.error(error)
      }
    },

    async showDetail(row) {
      try {
        const res = await recordApi.detail(row.id)
        this.currentPersonnel = this.formatTableData([res.data])[0]
        this.detailVisible = true
      } catch (error) {
        this.$message.error('加载详情失败')
        console.error(error)
      }
    },

    async showLogs(row) {
      try {
        const res = await recordApi.logs(row.id)
        this.logs = res.data.data || []
        this.logVisible = true
      } catch (error) {
        this.$message.error('加载日志失败')
        console.error(error)
      }
    },

    openOaModal(row) {
      this.currentPersonnel = { ...row }
      this.oaModalVisible = true
    },

    async handleOaConfirm(selectedOa) {
      if (!selectedOa?.id) return
      try {
        await recordApi.link(this.currentPersonnel.id, { oa_info_id: selectedOa.id })
        this.$message.success('OA关联成功')
        this.oaModalVisible = false
        await this.loadData()
      } catch (error) {
        this.$message.error('OA关联失败')
        console.error(error)
      }
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.loadData()
    },

    handleCurrentChange(page) {
      this.currentPage = page
      this.loadData()
    }
  }
}
</script>

<style scoped>
.personnel-list {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.search-bar {
  background: white;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  margin-bottom: 16px;
}

.action-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  justify-content: flex-start;
}

.table-container {
  background: white;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
</style>
