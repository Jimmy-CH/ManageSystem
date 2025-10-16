<template>
  <div class="personnel-list">
    <!-- 搜索区域 -->
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" size="small">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="人员类型">
          <el-select v-model="searchForm.type" placeholder="请选择" clearable>
            <el-option label="外部" value="external" />
            <el-option label="内部" value="internal" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件类型">
          <el-select v-model="searchForm.idType" placeholder="请选择" clearable>
            <el-option label="身份证" value="idcard" />
            <el-option label="护照" value="passport" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件号码">
          <el-input v-model="searchForm.idNo" placeholder="请输入证件号" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.department" placeholder="请选择" clearable>
            <el-option label="技术部" value="tech" />
            <el-option label="运营部" value="ops" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="已入" value="entered" />
            <el-option label="已出" value="exited" />
            <el-option label="未入" value="not_entered" />
          </el-select>
        </el-form-item>
        <el-form-item label="门禁卡状态">
          <el-select v-model="searchForm.cardStatus" placeholder="请选择" clearable>
            <el-option label="已激活" value="active" />
            <el-option label="已停用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item label="OA">
          <el-input v-model="searchForm.oa" placeholder="请输入OA" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="handleSearch">搜索</el-button>
          <el-button size="small" @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- ✅ 操作按钮栏：放在搜索和表格之间 -->
    <div class="action-bar">
      <el-button size="small" @click="exportData">导出</el-button>
      <el-button size="small" @click="openRegisterModal()">入场登记</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="tableData" border style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="index" label="序号" width="60" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="type" label="人员类型" width="100" />
        <el-table-column prop="idType" label="证件类型" width="100" />
        <el-table-column prop="idNo" label="证件号码" width="180" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="enterTime" label="进入时间" width="160" />
        <el-table-column prop="exitTime" label="离开时间" width="160" />
        <el-table-column prop="operator" label="操作人员" width="120" />
        <el-table-column prop="reason" label="出入原因" width="180" />
        <el-table-column prop="cardStatus" label="门禁卡状态" width="120" />
        <el-table-column prop="oaApprover" label="OA审批人" width="120" />
        <el-table-column prop="oaApproveTime" label="OA审批时间" width="160" />
        <el-table-column prop="oaApplicant" label="OA申请人" width="120" />
        <el-table-column prop="oaApplyTime" label="OA申请时间" width="160" />
        <el-table-column label="操作" width="300">
          <template slot-scope="scope">
            <!-- <el-button size="mini" @click="showDetail(scope.row)">详情</el-button> -->
            <el-button size="mini" @click="showLogs(scope.row)">日志</el-button>
            <el-button size="mini" type="primary" @click="openEntryModal(scope.row)">入场</el-button>
            <el-button size="mini" type="danger" @click="openExitModal(scope.row)">离场</el-button>
            <el-button size="small" @click="openOaModal(scope.row)">关联OA</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 入场弹窗 -->
    <EntryModal
      :visible.sync="entryVisible"
      :personnel="currentPersonnel"
      @submit="handleEntrySubmit"
    />
    <!-- 离场弹窗 -->
    <ExitModal
      :visible.sync="exitVisible"
      :personnel="currentPersonnel"
      @submit="handleExitSubmit"
    />

    <!-- 详情弹窗 -->
    <DetailModal
      :visible.sync="detailVisible"
      :personnel="currentPersonnel"
      @update-personnel="handlePersonnelUpdate"
    />

    <!-- 日志弹窗 -->
    <LogModal
      :visible="logVisible"
      :logs="logs"
      @close="logVisible = false"
    />
    <!-- 登记弹窗 -->
    <RegisterModal
      :visible="registerVisible"
      @submit="handleRegisterSubmit"
      @update:visible="registerVisible = $event"
    />
    <!-- OA 弹窗 -->
    <OaModal
      :visible.sync="oaModalVisible"
      @confirm="handleOaConfirm"
    />
  </div>
</template>

<script>
import DetailModal from './DetailModal.vue'
import LogModal from './LogModal.vue'
import EntryModal from './EntryModal.vue'
import ExitModal from './ExitModal.vue'
import RegisterModal from './RegisterModal.vue'
import OaModal from './OaModal.vue'

export default {
  name: 'PersonnelList',
  components: {
    DetailModal,
    LogModal,
    EntryModal,
    ExitModal,
    RegisterModal,
    OaModal
  },
  data() {
    return {
      searchForm: {},
      tableData: [
        {
          index: 1,
          name: '王明',
          phone: '17800001234',
          type: 'external',
          idType: '身份证',
          idNo: '110101199001011234',
          department: '技术部',
          status: 'entered',
          enterTime: '2025-08-07 09:00',
          exitTime: '2025-08-07 18:00',
          operator: '张三',
          reason: '参观访问',
          cardStatus: 'active',
          oaApprover: '李四',
          oaApproveTime: '2025-08-07 09:00',
          oaApplicant: '王明',
          oaApplyTime: '2025-08-07 08:30',
          oaTitle: '',
          oaId: '',
          logs: [
            { time: '2025-08-07 09:00', type: 'entry', operator: '张三', cardStatus: '已发放', remarks: '正常入场' },
            { time: '2025-08-07 18:00', type: 'exit', operator: '李四', cardStatus: '已回收', remarks: '正常离场' }
          ]
        }
      ],
      detailVisible: false,
      logVisible: false,
      entryVisible: false,
      exitVisible: false,
      registerVisible: false,
      oaModalVisible: false,
      currentPersonnel: {},
      currentLogs: [],
      logs: [
        {
          time: '17:30',
          date: '2025-09-19',
          type: '离场',
          operator: '陈永超',
          operatorId: '02540871',
          cardStatus: '未归还 (卡4)',
          idStatus: '已归还(身份证)',
          remark: ''
        },
        {
          time: '15:55',
          date: '2025-09-19',
          type: '入场',
          operator: '陈永超',
          operatorId: '02540871',
          cardStatus: '已发卡 (卡4)',
          idStatus: '已质押(身份证)',
          remark: ''
        },
        {
          time: '09:50',
          date: '2025-09-19',
          type: '离场',
          operator: '陈永超',
          operatorId: '02540871',
          cardStatus: '未归还 (卡3)',
          idStatus: '已归还(身份证)',
          remark: '访客将卡遗失，已报备'
        },
        {
          time: '09:30',
          date: '2025-09-19',
          type: '入场',
          operator: '陈永超',
          operatorId: '02540871',
          cardStatus: '已发卡 (卡3)',
          idStatus: '已质押(身份证)',
          remark: ''
        }
      ]
    }
  },
  methods: {
    exportData() {
      console.log('导出数据:', this.searchForm)
      // 实际应用中可调用后端接口导出数据
    },
    openOaModal() {
      this.oaModalVisible = true
    },
    handleOaConfirm(selected) {
      if (selected && selected.title) {
        this.$set(this.localPersonnel, 'oaTitle', selected.title)
        this.$set(this.localPersonnel, 'oaId', selected.id)
        // 向父组件同步更新（可选）
        this.$emit('update-personnel', this.localPersonnel)
      }
    },
    openRegisterModal() {
      this.registerVisible = true
    },
    handleRegisterSubmit(data) {
      console.log('登记成功:', data)
      // 可选：更新表格数据
    },
    openEntryModal(row) {
      this.currentPersonnel = { ...row } // 深拷贝避免引用问题
      this.entryVisible = true
    },
    openExitModal(row) {
      this.currentPersonnel = { ...row }
      this.exitVisible = true
    },
    handleEntrySubmit(data) {
      console.log('入场登记成功:', data)
      // 可选：更新表格数据
    },
    handleExitSubmit(data) {
      console.log('离场登记成功:', data)
      // 可选：更新表格数据
    },
    handleSearch() {
      this.$emit('search', this.searchForm)
    },
    resetSearch() {
      this.searchForm = {}
      this.$emit('search', this.searchForm)
    },
    showDetail(row) {
      this.currentPersonnel = { ...row }
      this.detailVisible = true
    },
    showLogs(row) {
      this.logVisible = true
    },
    handlePersonnelUpdate(updated) {
      // 可选：更新 tableData 中对应行的数据
      const index = this.tableData.findIndex(item => item.index === updated.index)
      if (index !== -1) {
        this.$set(this.tableData, index, { ...updated })
      }
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
