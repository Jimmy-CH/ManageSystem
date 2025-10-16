<!-- src/components/ExitModal.vue -->
<template>
  <el-dialog
    title="园通云中心进出登记"
    :visible.sync="dialogVisible"
    width="800px"
    @close="resetForm"
  >
    <!-- 人员信息 -->
    <div class="info-section">
      <h4>人员信息</h4>
      <!-- 👇 包裹只读信息的 el-form -->
      <el-form :model="form" label-width="100px" size="small">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="人员类型" prop="type">
              <el-select v-model="form.type" disabled>
                <el-option label="外部人员" value="external" />
                <el-option label="内部人员" value="internal" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-input v-model="form.department" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证件类型" prop="idType">
              <el-select v-model="form.idType" disabled>
                <el-option label="身份证" value="idcard" />
                <el-option label="护照" value="passport" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证件号码" prop="idNo">
              <el-input v-model="form.idNo" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="form.phone" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进出时间" prop="timeRange">
              <el-date-picker
                v-model="form.timeRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="yyyy-MM-dd HH:mm"
                format="yyyy-MM-dd HH:mm"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进入原因" prop="reason">
              <el-input v-model="form.reason" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="携带物品" prop="items">
              <el-input v-model="form.items" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="关联OA" prop="oa">
              <el-input v-model="form.oa" readonly />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- 离场登记表单 -->
    <div class="exit-form">
      <el-tabs v-model="activeTab" type="card" style="margin-top: 15px;">
        <el-tab-pane label="离场登记" name="exit">
          <!-- 👇 关键：Tab 内必须有自己的 el-form -->
          <el-form
            ref="exitForm"
            :model="form"
            label-width="100px"
            size="small"
          >
            <el-form-item label="* 门禁卡信息" prop="exitCardInfo">
              <el-select v-model="form.exitCardInfo" placeholder="请选择" style="width: 100%;">
                <el-option label="无需发卡" value="none" />
                <el-option label="已发卡" value="issued" />
              </el-select>
            </el-form-item>

            <el-form-item label="* 证件质押" prop="exitIdDeposit">
              <el-select v-model="form.exitIdDeposit" placeholder="请选择" style="width: 100%;">
                <el-option label="未质押" value="not_deposited" />
                <el-option label="已质押" value="deposited" />
              </el-select>
            </el-form-item>

            <el-form-item label="* 离场情况" prop="exitStatus">
              <el-radio-group v-model="form.exitStatus">
                <el-radio label="正常">正常</el-radio>
                <el-radio label="异常">异常</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="* 备注" prop="remark">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
                style="width: 100%;"
              />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitForm">确定</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'ExitModal',
  props: {
    visible: Boolean,
    personnel: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      activeTab: 'exit',
      form: {
        name: '',
        type: 'external',
        unit: '',
        department: '',
        idType: 'idcard',
        idNo: '',
        phone: '',
        timeRange: [],
        reason: '',
        items: '',
        oa: '',
        exitCardInfo: 'none',
        exitIdDeposit: 'not_deposited',
        exitStatus: '正常',
        remark: ''
      }
    }
  },
  computed: {
    dialogVisible: {
      get() {
        return this.visible
      },
      set(val) {
        this.$emit('update:visible', val)
      }
    }
  },
  watch: {
    personnel: {
      handler(newVal) {
        if (newVal && newVal.name) {
          this.form.name = newVal.name || ''
          this.form.type = newVal.type || 'external'
          this.form.unit = newVal.unit || ''
          this.form.department = newVal.department || ''
          this.form.idType = newVal.idType || 'idcard'
          this.form.idNo = newVal.idNo || ''
          this.form.phone = newVal.phone || ''
          this.form.reason = newVal.reason || ''
          this.form.items = newVal.items || ''
          this.form.oa = newVal.oa || ''
        }
      },
      immediate: true
    }
  },
  methods: {
    resetForm() {
      this.form.exitCardInfo = 'none'
      this.form.exitIdDeposit = 'not_deposited'
      this.form.exitStatus = '正常'
      this.form.remark = ''
      this.form.timeRange = []
    },
    submitForm() {
      const payload = {
        ...this.form,
        status: 'exited'
      }
      this.$emit('submit', payload)
      this.dialogVisible = false
    }
  }
}
</script>

<style scoped>
.info-section {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.info-section h4 {
  margin-top: 0;
  color: #333;
  font-size: 14px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.exit-form {
  background: white;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.dialog-footer {
  text-align: right;
  padding-top: 15px;
}
</style>
