<!-- src/views/PersonnelSummary.vue -->
<template>
  <div class="summary-page">
    <!-- 顶部筛选区 -->
    <div class="filter-bar">
      <el-radio-group v-model="timeRange" size="small" style="margin-right: 20px;">
        <el-radio-button label="本周">本周</el-radio-button>
        <el-radio-button label="本月">本月</el-radio-button>
        <el-radio-button label="本年">本年</el-radio-button>
        <el-radio-button label="上一周">上一周</el-radio-button>
        <el-radio-button label="上个月">上个月</el-radio-button>
      </el-radio-group>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="yyyy-MM-dd"
        format="yyyy-MM-dd"
        style="width: 240px; margin-right: 10px;"
      />

      <el-button type="primary" size="small" @click="queryData">查询</el-button>
      <el-button size="small" @click="reset">重置</el-button>
    </div>

    <!-- 指标卡片 -->
    <div class="cards-container">
      <div class="card">
        <div class="icon"><i class="el-icon-user-solid" /></div>
        <div class="title">实际进出总人数</div>
        <div class="value">{{ totalPeople }}<span class="trend">环比 ↑20%</span></div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-user-solid" /></div>
        <div class="title">实际进出总次数</div>
        <div class="value">{{ totalTimes }}<span class="trend">环比 ↑20%</span></div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-s-custom" /></div>
        <div class="title">进出单位数量</div>
        <div class="value">{{ unitCount }}<span class="trend">环比 ↑20%</span></div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-warning" /></div>
        <div class="title">进出正常占比</div>
        <div class="value">{{ normalRate }}%<span class="trend">环比 ↑2%</span></div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 左侧：进入单位分布 -->
      <div class="chart-wrapper">
        <h3>进入单位分布</h3>
        <div class="chart-content">
          <div class="pie-chart">
            <div class="pie" :style="{ '--percent': piePercent }" />
            <div class="legend">
              <div v-for="(item, idx) in pieData" :key="idx" class="item">
                <span class="color" :style="{ backgroundColor: item.color }" />
                <span>{{ item.name }} {{ item.value }}</span>
              </div>
            </div>
          </div>
          <div class="table">
            <el-table :data="unitTableData" border style="width: 100%">
              <el-table-column prop="name" label="单位" width="120" />
              <el-table-column prop="count" label="人员数量" width="120" />
              <el-table-column prop="percent" label="占比" width="100" />
            </el-table>
          </div>
        </div>
      </div>

      <!-- 右侧：申请人次数 -->
      <div class="chart-wrapper">
        <h3>申请人次数</h3>
        <div class="bar-chart">
          <div v-for="(item, idx) in barData" :key="idx" class="bar-item">
            <div class="label">{{ item.name }}</div>
            <div class="bar" :style="{ width: `${item.width}%` }">
              <div class="value">{{ item.value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PersonnelSummary',
  data() {
    return {
      timeRange: '本月',
      dateRange: ['2025-04-01', '2025-04-21'],
      totalPeople: 300,
      totalTimes: 280,
      unitCount: 200,
      normalRate: 90,

      pieData: [
        { name: '联通', value: 100, color: '#8d72e6' },
        { name: '华为', value: 50, color: '#f56c6c' },
        { name: '联想', value: 40, color: '#409eff' },
        { name: 'H3C', value: 30, color: '#67c234' },
        { name: '中国移动', value: 20, color: '#e6a23c' },
        { name: '中国联通', value: 15, color: '#909399' }
      ],
      unitTableData: [
        { name: '联通', count: 100, percent: '33%' },
        { name: '华为', count: 50, percent: '17%' },
        { name: '联想', count: 40, percent: '17%' },
        { name: 'H3C', count: 30, percent: '17%' },
        { name: '中国移动', count: 20, percent: '17%' },
        { name: '中国联通', count: 15, percent: '17%' }
      ],
      barData: [
        { name: '张三', value: 48, width: 70 },
        { name: '李四', value: 42, width: 60 },
        { name: '王五', value: 35, width: 50 },
        { name: '齐欢', value: 20, width: 29 },
        { name: '齐欢', value: 13, width: 19 },
        { name: '齐欢', value: 8, width: 11 }
      ]
    }
  },
  computed: {
    piePercent() {
      const total = this.pieData.reduce((sum, item) => sum + item.value, 0)
      return (this.pieData[0].value / total) * 100
    }
  },
  methods: {
    queryData() {
      console.log('查询数据:', this.dateRange)
      // 这里可以调用 API 获取真实数据
    },
    reset() {
      this.timeRange = '本月'
      this.dateRange = ['2025-04-01', '2025-04-21']
    }
  }
}
</script>

<style scoped>
.summary-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  background: white;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.card {
  background: white;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  text-align: center;
}

.card .icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.card .title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.card .value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.card .trend {
  font-size: 12px;
  color: #409eff;
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-wrapper {
  background: white;
  padding: 15px;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.chart-wrapper h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.chart-content {
  display: flex;
  gap: 20px;
}

.pie-chart {
  flex: 1;
  position: relative;
  width: 200px;
  height: 200px;
}

.pie {
  width: 100%;
  height: 100%;
  position: relative;
  clip-path: polygon(50% 50%, 50% 50%, 50% 50%);
  background: conic-gradient(
    #8d72e6 0%,
    #f56c6c 33%,
    #409eff 50%,
    #67c234 67%,
    #e6a23c 83%,
    #909399 100%
  );
}

.legend {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.legend .item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
}

.legend .color {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  margin-right: 5px;
}

.table {
  flex: 1;
  min-width: 300px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.bar-item .label {
  width: 60px;
  text-align: right;
  color: #666;
}

.bar-item .bar {
  flex: 1;
  height: 20px;
  background: linear-gradient(to right, #8d72e6, #f56c6c);
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.bar-item .bar .value {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-size: 12px;
  background: rgba(0,0,0,0.6);
  padding: 0 5px;
  border-radius: 3px;
}
</style>
