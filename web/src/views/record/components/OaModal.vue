<template>
  <el-dialog title="关联OA" :visible.sync="localVisible" width="1400px" @close="handleClose">
    <el-form :inline="true" :model="form" size="small">
      <el-form-item label="申请人">
        <el-input v-model="form.applicant" placeholder="请输入申请人" clearable />
      </el-form-item>
      <el-form-item label="进入时间">
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
        v-loading="loading"
        :data="oaList"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="OA标题" width="300" :show-overflow-tooltip="true">
          <template #default="{ row }">
            {{ row.oa_link_info || row.applicant + '的进出申请' }}
          </template>
        </el-table-column>
        <el-table-column prop="applicant" label="申请人" width="100" />
        <el-table-column label="申请进入时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.apply_enter_time) }}
          </template>
        </el-table-column>
        <el-table-column label="申请离开时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.apply_leave_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="apply_count" label="申请人数" width="80" />
        <el-table-column prop="connected_count" label="关联人数" width="80" />
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.applicant_time) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.create_time) }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div slot="footer" class="dialog-footer">
      <el-button @click="localVisible = false">取 消</el-button>
      <el-button type="primary" :disabled="!selectedRow" @click="confirm">确 认</el-button>
    </div>
  </el-dialog>
</template>

<script>
import { recordApi } from '@/api/record' // 请根据实际路径调整，例如 '@/api/record'

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
      oaList: [],
      selectedRow: null,
      loading: false
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
  watch: {
    visible(newVal) {
      if (newVal) {
        // 弹窗打开时自动查询（可选：重置表单）
        // 可选：每次打开清空筛选条件
        this.queryOA()
      }
    }
  },
  methods: {
    async queryOA() {
      this.loading = true
      const params = {}

      if (this.form.applicant) {
        params.applicant = this.form.applicant
      }

      if (this.form.dateRange && this.form.dateRange.length === 2) {
        const [start, end] = this.form.dateRange
        params.apply_enter_time_after = `${start}T00:00:00`
        params.apply_enter_time_before = `${end}T23:59:59`
      }

      try {
        const res = await recordApi.OAInfo(params)
        this.oaList = res.data?.results || []
      } catch (error) {
        console.error('查询OA信息失败:', error)
        this.$message.error('查询OA信息失败，请重试')
        this.oaList = []
      } finally {
        this.loading = false
      }
    },

    resetOA() {
      this.form = { applicant: '', dateRange: [] }
      this.oaList = []
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
    },

    formatDate(isoStr) {
      if (!isoStr) return ''
      return isoStr.replace('T', ' ').substring(0, 16) // 例如：2025-10-15 15:00
    }
  }
}
</script>
