<!-- src/components/EntryModal.vue -->
<template>
  <el-dialog
    title="园通云中心进出登记"
    :visible.sync="dialogVisible"
    width="800px"
    @close="resetForm"
  >
    <!-- 人员信息（只读） -->
    <div class="info-section">
      <h4>人员信息</h4>
      <el-form :model="form" label-width="100px" size="small">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名">
              <el-input v-model="form.name" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="人员类型">
              <el-select v-model="form.type" disabled>
                <el-option label="内部人员" value="internal" />
                <el-option label="外部人员" value="external" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="form.unit" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门">
              <el-input v-model="form.department" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证件类型">
              <el-select v-model="form.idType" disabled>
                <el-option label="身份证" value="idcard" />
                <el-option label="护照" value="passport" />
                <!-- 如有“工牌”等，可扩展 -->
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="证件号码">
              <el-input v-model="form.idNo" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话">
              <el-input v-model="form.phone" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进入原因">
              <el-input v-model="form.reason" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="携带物品">
              <el-input v-model="form.items" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联OA">
              <el-input v-model="form.oa" readonly />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- 入场登记表单 -->
    <div class="entry-form">
      <el-tabs v-model="activeTab" type="card" style="margin-top: 15px;">
        <el-tab-pane label="入场登记" name="entry">
          <el-form
            ref="entryForm"
            :model="form"
            label-width="100px"
            size="small"
          >
            <el-form-item label="陪同人员">
              <el-select v-model="form.accompany" placeholder="请选择或留空">
                <el-option label="无" value="" />
                <el-option label="王晶晶(02540885)" value="王晶晶" />
                <el-option label="黄海龙(02540886)" value="黄海龙" />
                <!-- 可动态加载 -->
              </el-select>
            </el-form-item>

            <el-form-item label="* 门禁卡信息" prop="cardInfo">
              <el-select v-model="form.cardInfo" placeholder="请选择" style="width: 100%;">
                <el-option label="无需发卡" value="none" />
                <el-option label="已发卡" value="issued" />
              </el-select>
            </el-form-item>

            <!-- 卡类型：仅当选择“已发卡”时显示 -->
            <el-form-item
              v-if="form.cardInfo === 'issued'"
              label="* 卡类型"
              prop="cardType"
            >
              <el-select v-model="form.cardType" placeholder="请选择卡类型" style="width: 100%;">
                <el-option label="卡1" :value="1" />
                <el-option label="卡2" :value="2" />
                <el-option label="卡3" :value="3" />
                <el-option label="卡4" :value="4" />
                <el-option label="卡5" :value="5" />
              </el-select>
            </el-form-item>

            <el-form-item label="* 证件质押" prop="idDeposit">
              <el-select v-model="form.idDeposit" placeholder="请选择" style="width: 100%;">
                <el-option label="未押证" value="not_deposited" />
                <el-option label="已押证" value="deposited" />
              </el-select>
            </el-form-item>

            <!-- 证件类型：仅当“已押证”时显示 -->
            <el-form-item
              v-if="form.idDeposit === 'deposited'"
              label="* 证件类型"
              prop="idDepositType"
            >
              <el-select v-model="form.idDepositType" placeholder="请选择" style="width: 100%;">
                <el-option label="身份证" value="idcard" />
                <el-option label="护照" value="passport" />
                <!-- 可扩展 -->
              </el-select>
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
  name: 'EntryModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    personnel: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      activeTab: 'entry',
      form: {
        // 只读信息
        name: '',
        type: 'external',
        unit: '',
        department: '',
        idType: 'idcard',
        idNo: '',
        phone: '',
        reason: '',
        items: '',
        oa: '',

        // 可编辑字段
        accompany: '',
        cardInfo: 'none', // 'none' / 'issued'
        cardType: 3, // 默认卡3，1~5
        idDeposit: 'not_deposited', // 'not_deposited' / 'deposited'
        idDepositType: 'idcard' // 'idcard' / 'passport'
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
        if (!newVal || !newVal.person_name) return

        this.form.name = newVal.person_name || ''
        this.form.unit = newVal.unit || ''
        this.form.department = newVal.department || ''
        this.form.idNo = newVal.id_number || ''
        this.form.phone = newVal.phone_number || ''
        this.form.reason = newVal.reason || ''
        this.form.items = newVal.carried_items || ''
        this.form.oa = newVal.applicant || ''

        // 人员类型：1=内部，2=外部
        this.form.type = newVal.person_type === 1 ? 'internal' : 'external'

        // 证件类型：假设 1=身份证，2=护照
        if (newVal.id_type === 1) {
          this.form.idType = 'idcard'
        } else if (newVal.id_type === 2) {
          this.form.idType = 'passport'
        } else {
          this.form.idType = 'idcard'
        }
      },
      immediate: true
    }
  },
  methods: {
    resetForm() {
      this.form.accompany = ''
      this.form.cardInfo = 'none'
      this.form.cardType = 3
      this.form.idDeposit = 'not_deposited'
      this.form.idDepositType = 'idcard'
    },

    submitForm() {
      // 转换逻辑
      const card_status = this.form.cardInfo === 'issued' ? 2 : 1
      const pledged_status = this.form.idDeposit === 'deposited' ? 2 : 1

      // 校验条件字段
      if (card_status === 2 && !this.form.cardType) {
        this.$message.warning('请选择门禁卡类型')
        return
      }

      if (pledged_status === 2 && !this.form.idDepositType) {
        this.$message.warning('请选择押证类型')
        return
      }

      // 构造提交数据
      const payload = {
        companion: this.form.accompany || '无',
        card_status: card_status,
        pledged_status: pledged_status
      }

      if (card_status === 2) {
        payload.card_type = this.form.cardType
      }

      if (pledged_status === 2) {
        payload.id_type = this.form.idDepositType === 'idcard' ? 1 : 2
      }

      // 触发提交事件，由父组件调用 API
      this.$emit('submit', {
        data: payload
      })

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

.entry-form {
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
