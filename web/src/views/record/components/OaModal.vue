<template>
  <el-dialog title="关联OA" :visible.sync="localVisible" width="1200px" @close="handleClose">
    <el-form :inline="true" :model="form" size="small">
      <el-form-item label="申请人">
        <el-input v-model="form.applicant" placeholder="请输入申请人" clearable />
      </el-form-item>
      <el-form-item label="时间">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="yyyy-MM-dd"
          format="yyyy-MM-dd"
          style="width: 200px;"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="small" @click="queryOA">查询</el-button>
        <el-button size="small" @click="resetOA">重置</el-button>
      </el-form-item>
    </el-form>

    <div style="margin-top: 20px;">
      <el-table
        :data="oaList"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="OA标题" width="300" />
        <el-table-column prop="applicant" label="申请人" width="100" />
        <el-table-column prop="applyTime" label="申请时间" width="160" />
        <el-table-column prop="peopleCount" label="人数" width="80" />
        <el-table-column prop="approveTime" label="批准时间" width="160" />
      </el-table>
    </div>

    <div slot="footer" class="dialog-footer">
      <el-button @click="localVisible = false">取 消</el-button>
      <el-button type="primary" :disabled="!selectedRow" @click="confirm">确 认</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'OaModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      form: {
        applicant: '',
        dateRange: []
      },
      oaList: [
        {
          id: 1,
          title: '关于临时访客进入园区的申请',
          applicant: '王明',
          applyTime: '2025-08-07',
          peopleCount: 1,
          approveTime: '2025-08-07'
        },
        {
          id: 2,
          title: '设备维护人员入园申请',
          applicant: '李四',
          applyTime: '2025-08-06',
          peopleCount: 2,
          approveTime: '2025-08-06'
        }
      ],
      selectedRow: null
    }
  },
  computed: {
    localVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    }
  },
  methods: {
    queryOA() {
      console.log('查询OA:', this.form)
    },
    resetOA() {
      this.form = { applicant: '', dateRange: [] }
    },
    handleSelectionChange(selection) {
      // 只允许单选
      this.selectedRow = selection.length > 0 ? selection[0] : null
    },
    confirm() {
      if (this.selectedRow) {
        this.$emit('confirm', this.selectedRow)
        this.localVisible = false
      }
    },
    handleClose() {
      this.selectedRow = null
    }
  }
}
</script>
