<!-- src/components/LogModal.vue -->
<template>
  <el-dialog
    title="人员进出日志"
    :visible.sync="dialogVisible"
    width="600px"
    @close="closeDialog"
  >
    <div class="log-container">
      <div v-for="(item, index) in formattedLogs" :key="index" class="log-item">
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
          <span :class="isAbnormal(item) ? 'warning' : 'normal'">
            门禁卡：{{ item.cardStatus }}
          </span>
        </div>

        <!-- 证件类型（非状态） -->
        <div class="id-type">
          <span class="normal">证件：{{ item.idType }}</span>
        </div>

        <!-- 质押状态（可选） -->
        <div class="pledge-status">
          <span :class="item.pledgedStatus.includes('未') ? 'normal' : 'warning'">
            质押状态：{{ item.pledgedStatus }}
          </span>
        </div>

        <!-- 备注或异常提示 -->
        <div v-if="item.remark || !item.isNormal" class="remark">
          <small>⚠️ {{ item.remark || (item.isNormal ? '' : '记录异常') }}</small>
        </div>
      </div>

      <div v-if="formattedLogs.length === 0" style="text-align: center; color: #999; padding: 20px;">
        暂无日志
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
    },
    formattedLogs() {
      return this.logs.map(log => {
        const isEntry = log.operation === '入场'
        const timeStr = isEntry ? log.entered_time : log.exited_time

        // 解析时间
        const time = timeStr ? timeStr.split(' ')[1] : '--:--:--'
        const date = timeStr ? timeStr.split(' ')[0] : '----'

        return {
          time,
          date,
          type: log.operation || '—',
          operator: log.create_user_name || '—',
          operatorId: log.create_user_code || '—',
          cardStatus: log.card_status_display || '—',
          idType: log.id_type_display || '—',
          pledgedStatus: log.pledged_status_display || '—',
          remark: log.remarks,
          isNormal: log.is_normal !== false // 后端 is_normal 为 true 或 undefined 表示正常
        }
      })
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close')
    },
    isAbnormal(item) {
      // 可根据业务逻辑扩展，例如 card_status 不是“已归还”等
      return !item.isNormal
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
}

.operation.in {
  color: #409eff;
}

.operation.out {
  color: #f56c6c;
}

.operator {
  color: #333;
}

.card-status,
.id-type,
.pledge-status {
  font-size: 12px;
}

.card-status.warning,
.pledge-status.warning {
  color: #f56c6c;
  font-weight: 500;
}

.card-status.normal,
.id-type.normal,
.pledge-status.normal {
  color: #666;
}

.remark {
  color: #f56c6c;
  font-size: 11px;
}

.dialog-footer {
  text-align: right;
  padding-top: 15px;
}
</style>
