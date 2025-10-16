<!-- src/components/EntryModal.vue -->
<template>
  <el-dialog
    title="园通云中心进出登记"
    :visible.sync="dialogVisible"
    width="800px"
    @close="resetForm"
  >
    <el-form
      ref="entryForm"
      :model="form"
      :rules="rules"
      label-width="100px"
      size="small"
      style="padding: 20px;"
    >
      <!-- 基本信息 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="入场时间" prop="entryTime">
            <el-date-picker
              v-model="form.entryTime"
              type="datetime"
              placeholder="选择入场时间"
              value-format="yyyy-MM-dd HH:mm"
              format="yyyy-MM-dd HH:mm"
              style="width: 100%;"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="进入原因" prop="reason">
            <el-input v-model="form.reason" placeholder="请输入进入原因" style="width: 100%;" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="携带物品" prop="items">
            <el-input v-model="form.items" placeholder="请输入携带物品" style="width: 100%;" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="陪同人员" prop="accompany">
            <el-select v-model="form.accompany" placeholder="请选择陪同人员" style="width: 100%;">
              <el-option label="无" value="" />
              <el-option label="张三" value="zhangsan" />
              <el-option label="李四" value="lisi" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="关联OA" prop="oa">
        <el-input v-model="form.oa" placeholder="请输入OA编号" style="width: 100%;" />
      </el-form-item>

      <!-- 人员信息区域 -->
      <div class="person-info-section">
        <div class="section-header">
          <span>共 {{ form.persons.length }} 人</span>
          <el-button type="text" size="mini" style="color: #409eff;" @click="addPerson">新增</el-button>
        </div>

        <div v-for="(person, index) in form.persons" :key="index" class="person-item">
          <!-- 人员头部：序号 + 操作按钮 -->
          <div class="person-header">
            <span>第 {{ index + 1 }} 个</span>
            <div>
              <el-button
                v-if="index > 0"
                type="text"
                size="mini"
                style="color: #409eff; margin-right: 8px;"
                @click="copyPrevious(index)"
              >
                复制上一条
              </el-button>
              <el-button
                v-if="form.persons.length > 1"
                type="text"
                size="mini"
                style="color: #f56c6c;"
                @click="removePerson(index)"
              >
                删除
              </el-button>
            </div>
          </div>

          <!-- 表单项 -->
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                label="* 姓名"
                :prop="'persons.' + index + '.name'"
                :rules="rules.name"
              >
                <el-input v-model="person.name" placeholder="请输入姓名" style="width: 100%;" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="* 人员类型"
                :prop="'persons.' + index + '.type'"
                :rules="rules.type"
              >
                <el-select v-model="person.type" placeholder="请选择" style="width: 100%;">
                  <el-option label="外部" value="external" />
                  <el-option label="内部" value="internal" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item
                label="* 单位"
                :prop="'persons.' + index + '.unit'"
                :rules="rules.unit"
              >
                <el-input v-model="person.unit" placeholder="请输入单位" style="width: 100%;" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="部门" :prop="'persons.' + index + '.department'">
                <el-input v-model="person.department" placeholder="请输入部门" style="width: 100%;" />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item
                label="* 证件类型"
                :prop="'persons.' + index + '.idType'"
                :rules="rules.idType"
              >
                <el-select v-model="person.idType" placeholder="请选择" style="width: 100%;">
                  <el-option label="身份证" value="idcard" />
                  <el-option label="护照" value="passport" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="* 证件号码"
                :prop="'persons.' + index + '.idNo'"
                :rules="rules.idNo"
              >
                <el-input v-model="person.idNo" placeholder="请输入证件号码" style="width: 100%;" />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item
                label="* 电话"
                :prop="'persons.' + index + '.phone'"
                :rules="rules.phone"
              >
                <el-input v-model="person.phone" placeholder="请输入电话" style="width: 100%;" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="* 门禁卡信息"
                :prop="'persons.' + index + '.cardInfo'"
                :rules="rules.cardInfo"
              >
                <el-select v-model="person.cardInfo" placeholder="请选择" style="width: 100%;">
                  <el-option label="已发卡" value="issued" />
                  <el-option label="未发卡" value="not_issued" />
                </el-select>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item
                label="证件质押"
                :prop="'persons.' + index + '.idDeposit'"
                :rules="rules.idDeposit"
              >
                <el-select v-model="person.idDeposit" placeholder="请选择" style="width: 100%;">
                  <el-option label="已质押" value="deposited" />
                  <el-option label="未质押" value="not_deposited" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="质押的证件类型" :prop="'persons.' + index + '.depositIdType'">
                <el-select v-model="person.depositIdType" placeholder="请选择" style="width: 100%;">
                  <el-option label="身份证" value="idcard" />
                  <el-option label="护照" value="passport" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-form>

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
    visible: Boolean
  },
  data() {
    return {
      // ✅ 关键修改：把 persons 合并进 form
      form: {
        entryTime: '',
        reason: '',
        items: '',
        accompany: '',
        oa: '',
        persons: [
          {
            name: '',
            type: 'external',
            unit: '',
            department: '',
            idType: 'idcard',
            idNo: '',
            phone: '',
            cardInfo: 'issued',
            idDeposit: 'deposited',
            depositIdType: 'idcard'
          }
        ]
      },
      // ❌ 删除独立的 persons 数组
      rules: {
        entryTime: [{ required: true, message: '请输入入场时间', trigger: 'blur' }],
        reason: [{ required: true, message: '请输入进入原因', trigger: 'blur' }],
        items: [{ required: true, message: '请输入携带物品', trigger: 'blur' }],
        // 注意：name/type/unit 等规则用于动态表单项，通过 :rules 传入，无需放在 form.rules 顶层
        name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        type: [{ required: true, message: '请选择人员类型', trigger: 'change' }],
        unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
        idType: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
        idNo: [{ required: true, message: '请输入证件号码', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入电话', trigger: 'blur' }],
        cardInfo: [{ required: true, message: '请选择门禁卡信息', trigger: 'change' }],
        idDeposit: [{ required: true, message: '请选择证件质押状态', trigger: 'change' }]
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
  methods: {
    resetForm() {
      this.$refs.entryForm.resetFields()
      // ✅ 重置时也要重置 form.persons
      this.form.persons = [
        {
          name: '',
          type: 'external',
          unit: '',
          department: '',
          idType: 'idcard',
          idNo: '',
          phone: '',
          cardInfo: 'issued',
          idDeposit: 'deposited',
          depositIdType: 'idcard'
        }
      ]
    },

    addPerson() {
      this.form.persons.push({
        name: '',
        type: 'external',
        unit: '',
        department: '',
        idType: 'idcard',
        idNo: '',
        phone: '',
        cardInfo: 'issued',
        idDeposit: 'deposited',
        depositIdType: 'idcard'
      })
    },

    copyPrevious(index) {
      const prev = { ...this.form.persons[index - 1] }
      this.form.persons.splice(index, 0, prev)
    },

    removePerson(index) {
      if (this.form.persons.length <= 1) {
        this.$message.warning('至少需要保留一位登记人员')
        return
      }
      this.form.persons.splice(index, 1)
    },

    submitForm() {
      this.$refs.entryForm.validate(valid => {
        if (valid) {
          // ✅ 直接提交 this.form，已包含所有数据
          this.$emit('submit', { ...this.form })
          this.dialogVisible = false
        } else {
          console.warn('表单校验失败')
        }
      })
    }
  }
}
</script>

<style scoped>
.person-info-section {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
  border: 1px solid #ddd;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  font-size: 12px;
  color: #666;
}

.section-header span {
  color: #333;
  font-weight: bold;
}

.person-item {
  margin-bottom: 20px;
  padding: 12px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.person-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #ebeef5;
  font-size: 12px;
  color: #666;
}

.person-header span {
  font-weight: bold;
}

.dialog-footer {
  text-align: right;
  padding-top: 15px;
}
</style>
