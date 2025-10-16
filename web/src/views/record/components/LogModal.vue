<!-- src/components/LogModal.vue -->
<template>
  <el-dialog
    title="人员进出日志"
    :visible.sync="dialogVisible"
    width="600px"
    @close="closeDialog"
  >
    <!-- 日志列表 -->
    <div class="log-container">
      <div v-for="(item, index) in logs" :key="index" class="log-item">
        <!-- 时间和日期 -->
        <div class="time">
          <strong>{{ item.time }}</strong>
          <div class="date">{{ item.date }}</div>
        </div>

        <!-- 操作类型 -->
        <div class="operation">
          <span :class="item.type === '入场' ? 'in' : 'out'">
            {{ item.type }}
          </span>
        </div>

        <!-- 操作人 -->
        <div class="operator">
          操作人：{{ item.operator }} ({{ item.operatorId }})
        </div>

        <!-- 门禁卡状态 -->
        <div class="card-status">
          <span :class="item.cardStatus.includes('未') || item.cardStatus.includes('损') ? 'warning' : 'normal'">
            {{ item.cardStatus }}
          </span>
        </div>

        <!-- 身份证状态 -->
        <div class="id-status">
          <span :class="item.idStatus.includes('未') || item.idStatus.includes('损') ? 'warning' : 'normal'">
            {{ item.idStatus }}
          </span>
        </div>

        <!-- 备注（异常信息） -->
        <div v-if="item.remark" class="remark">
          <small>⚠️ {{ item.remark }}</small>
        </div>
      </div>
    </div>

    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogVisible = false">关闭</el-button>
    </div>
  </el-dialog>
</template>

<script>
export default {
  name: 'LogModal',
  props: {
    visible: Boolean,
    logs: {
      type: Array,
      default: () => []
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
    closeDialog() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.log-container {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px 0;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 15px;
}

.log-item {
  padding: 12px 15px;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.time {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time strong {
  font-size: 14px;
  color: #333;
}

.date {
  font-size: 10px;
  color: #999;
}

.operation {
  font-weight: bold;
  color: #409eff;
}

.operation.in {
  color: #409eff;
}

.operation.out {
  color: #f56c6c;
}

.operator {
  margin-top: 4px;
  color: #333;
}

.card-status,
.id-status {
  margin-top: 4px;
  font-size: 12px;
}

.card-status.normal,
.id-status.normal {
  color: #666;
}

.card-status.warning,
.id-status.warning {
  color: #f56c6c;
  font-weight: 500;
}

.remark {
  margin-top: 4px;
  color: #f56c6c;
  font-size: 11px;
}

.dialog-footer {
  text-align: right;
  padding-top: 15px;
}
</style>
