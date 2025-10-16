<!-- src/components/DetailModal.vue -->
<template>
  <el-dialog
    title="圆通云中心进出登记"
    :visible.sync="localVisible"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="personnel" label-width="100px" label-position="left">
      <el-form-item label="姓名">
        <el-input v-model="personnel.name" disabled />
      </el-form-item>
      <el-form-item label="人员类型">
        <el-select v-model="personnel.type" disabled>
          <el-option label="外部人员" value="external" />
          <el-option label="内部人员" value="internal" />
        </el-select>
      </el-form-item>
      <el-form-item label="部门">
        <el-input v-model="personnel.department" disabled />
      </el-form-item>
      <el-form-item label="证件号码">
        <el-input v-model="personnel.idNo" disabled />
      </el-form-item>
      <el-form-item label="电话">
        <el-input v-model="personnel.phone" disabled />
      </el-form-item>
      <el-form-item label="进入时间">
        <el-date-picker
          v-model="personnel.enterTime"
          type="datetime"
          value-format="yyyy-MM-dd HH:mm"
          format="yyyy-MM-dd HH:mm"
          disabled
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="离开时间">
        <el-date-picker
          v-model="personnel.exitTime"
          type="datetime"
          value-format="yyyy-MM-dd HH:mm"
          format="yyyy-MM-dd HH:mm"
          disabled
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="出入原因">
        <el-input v-model="personnel.reason" type="textarea" :rows="3" disabled />
      </el-form-item>
      <el-form-item label="关联OA">
        <el-button size="small" @click="openOaModal">选择OA</el-button>
        <span v-if="personnel.oaTitle" style="margin-left: 10px;">{{ personnel.oaTitle }}</span>
      </el-form-item>
      <el-form-item label="门禁卡信息">
        <el-select v-model="personnel.cardInfo" placeholder="请选择" disabled>
          <el-option label="已激活" value="active" />
          <el-option label="已停用" value="inactive" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="personnel.notes" type="textarea" :rows="3" disabled />
      </el-form-item>
    </el-form>

    <div slot="footer" class="dialog-footer">
      <el-button @click="localVisible = false">取 消</el-button>
      <el-button type="primary" @click="confirm">确 定</el-button>
    </div>

    <!-- OA 弹窗 -->
    <OaModal
      :visible.sync="oaModalVisible"
      @confirm="handleOaConfirm"
    />
  </el-dialog>
</template>

<script>
import OaModal from './OaModal.vue'

export default {
  name: 'DetailModal',
  components: {
    OaModal
  },
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
      localPersonnel: { ...this.personnel },
      oaModalVisible: false
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
    personnel: {
      handler(newVal) {
        this.localPersonnel = { ...newVal }
      },
      deep: true
    }
  },
  methods: {
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
    confirm() {
      this.$message.success('保存成功')
      this.localVisible = false
    },
    handleClose() {
      this.oaModalVisible = false
    }
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>
