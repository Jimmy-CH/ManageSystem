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
        <div class="value">
          {{ totalPeople }}
          <span class="trend">{{ getTrendText(ringRatio.people) }}</span>
        </div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-user-solid" /></div>
        <div class="title">实际进出总次数</div>
        <div class="value">
          {{ totalTimes }}
          <span class="trend">{{ getTrendText(ringRatio.entries) }}</span>
        </div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-s-custom" /></div>
        <div class="title">进出单位数量</div>
        <div class="value">
          {{ unitCount }}
          <span class="trend">{{ getTrendText(ringRatio.unit) }}</span>
        </div>
      </div>
      <div class="card">
        <div class="icon"><i class="el-icon-warning" /></div>
        <div class="title">进出正常占比</div>
        <div class="value">
          {{ normalRate }}%
          <span class="trend">{{ getTrendText(ringRatio.ratio) }}</span>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 左侧：进入单位分布（饼图） -->
      <div class="chart-wrapper">
        <h3>进入单位分布</h3>
        <div class="chart-content">
          <div ref="pieChart" class="echart" style="width: 100%; height: 300px;" />
          <div class="table">
            <el-table :data="unitTableData" border style="width: 100%">
              <el-table-column prop="name" label="单位" width="120" />
              <el-table-column prop="count" label="人员数量" width="100" />
              <el-table-column prop="percent" label="占比" width="80" />
            </el-table>
          </div>
        </div>
      </div>

      <!-- 右侧：申请人次数（柱状图） -->
      <div class="chart-wrapper">
        <h3>申请人次数</h3>
        <div ref="barChart" class="echart" style="width: 100%; height: 300px;" />
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { summaryApi } from '@/api/record'

const TIME_RANGE_MAP = {
  '本周': 'this_week',
  '本月': 'this_month',
  '本年': 'this_year',
  '上一周': 'last_week',
  '上个月': 'last_month'
}

export default {
  name: 'PersonnelSummary',
  data() {
    return {
      timeRange: '本月',
      dateRange: [],
      totalPeople: 0,
      totalTimes: 0,
      unitCount: 0,
      normalRate: 0,
      ringRatio: { people: 0, entries: 0, unit: 0, ratio: 0 },
      pieData: [],
      unitTableData: [],
      barData: []
    }
  },
  async created() {
    await this.queryData()
  },
  mounted() {
    this.initCharts()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    this.disposeCharts()
  },
  methods: {
    initCharts() {
      this.pieChart = echarts.init(this.$refs.pieChart)
      this.barChart = echarts.init(this.$refs.barChart)
      this.updateCharts()
    },
    disposeCharts() {
      this.pieChart?.dispose()
      this.barChart?.dispose()
    },
    handleResize() {
      this.pieChart?.resize()
      this.barChart?.resize()
    },
    updateCharts() {
      // 饼图
      const pieOption = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c}人 ({d}%)'
        },
        legend: {
          show: true,
          orient: 'horizontal',
          left: 'left',
          top: '20px',
          data: this.pieData.map(item => ({
            name: item.name,
            icon: 'circle',
            textStyle: { color: '#333' }
          }))
        },
        series: [
          {
            name: '单位分布',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}: {c}',
              color: '#333',
              fontSize: 12,
              lineHeight: 18
            },
            labelLine: {
              show: true,
              length: 10,
              length2: 20,
              smooth: true
            },
            itemStyle: {
              borderRadius: 4,
              borderColor: '#fff',
              borderWidth: 2
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '14',
                fontWeight: 'bold',
                color: '#333'
              }
            },
            data: this.pieData.map(item => ({
              name: item.name,
              value: item.value,
              itemStyle: { color: item.color }
            }))
          }
        ]
      }
      this.pieChart.setOption(pieOption, true)

      // 柱状图
      // 柱状图（堆叠）
      const barOption = {
        title: {
          text: '申请人次数',
          left: 'left',
          top: '10px',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            const completed = params[0]?.value || 0
            const pending = params[1]?.value || 0
            const total = completed + pending
            return `
        <div style="padding: 8px; font-size: 12px;">
          <p><strong>${params[0]?.name}</strong></p>
          <p style="color: #8d72e6;">● 已入场+已离场：${completed}次</p>
          <p style="color: #f56c6c;">● 未入场：${pending}次</p>
          <p><strong>总计：${total}次</strong></p>
        </div>
      `
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '次数',
          nameLocation: 'middle',
          nameGap: 20,
          axisLabel: {
            formatter: '{value}次'
          }
        },
        yAxis: {
          type: 'category',
          data: this.barData.map(item => item.name),
          axisTick: { show: false }
        },
        legend: {
          show: true,
          data: ['已入场+已离场', '未入场'],
          top: '10px',
          right: '10px'
        },
        series: [
          {
            name: '已入场+已离场',
            type: 'bar',
            stack: 'total',
            barWidth: '60%',
            itemStyle: { color: '#8d72e6' },
            label: {
              show: true,
              position: 'insideRight',
              color: '#fff',
              fontSize: 12,
              formatter: '{c}次'
            },
            data: this.barData.map(item => item.completed)
          },
          {
            name: '未入场',
            type: 'bar',
            stack: 'total',
            barWidth: '60%',
            itemStyle: { color: '#f56c6c' },
            label: {
              show: true,
              position: 'insideRight',
              color: '#fff',
              fontSize: 12,
              formatter: '{c}次'
            },
            data: this.barData.map(item => item.pending)
          }
        ]
      }
      this.barChart.setOption(barOption, true)
    },

    async queryData() {
      const params = {}
      if (this.dateRange && this.dateRange.length === 2) {
        params.start_date = this.dateRange[0]
        params.end_date = this.dateRange[1]
      } else {
        params.period = TIME_RANGE_MAP[this.timeRange]
      }

      try {
        const [cardRes, unitRes, applicantRes] = await Promise.all([
          summaryApi.getCards(params),
          summaryApi.getUnitDistribution(params),
          summaryApi.getApplicantCount(params)
        ])

        // === 卡片数据 ===
        const cardData = cardRes.data
        this.totalPeople = cardData.total_people || 0
        this.totalTimes = cardData.total_entries || 0
        this.unitCount = cardData.total_unit || 0
        this.normalRate = parseFloat(cardData.normal_ratio_percent)?.toFixed(1) || '0.0'
        this.ringRatio = cardData.ring_ratio || {}

        // === 单位分布 ===
        const unitList = unitRes.data.data || []
        const COLORS = ['#8d72e6', '#f56c6c', '#409eff', '#67c234', '#e6a23c', '#909399']
        this.pieData = unitList.map((item, index) => ({
          name: item.unit,
          value: item.count,
          percent: item.percentage,
          color: COLORS[index % COLORS.length]
        }))

        this.unitTableData = unitList.map(item => ({
          name: item.unit,
          count: item.count,
          percent: `${item.percentage}%`
        }))

        // === 申请人次数 ===
        const applicantList = applicantRes.data.data || []
        this.barData = applicantList.map(item => ({
          name: item.name,
          completed: item.completed || 0, // 已完成（已入场+已离场）
          pending: item.pending || 0 // 未入场
        }))

        // 更新图表
        if (this.pieChart && this.barChart) {
          this.updateCharts()
        }
      } catch (error) {
        this.$message.error('加载汇总数据失败')
        console.error(error)
      }
    },

    reset() {
      this.timeRange = '本月'
      this.dateRange = []
      this.queryData()
    },

    getTrendText(value) {
      if (value == null || value === undefined) return '环比 —'
      const num = parseFloat(value)
      if (isNaN(num)) return '环比 —'
      if (num > 0) return `环比 ↑${num}%`
      if (num < 0) return `环比 ↓${Math.abs(num)}%`
      return '环比 —'
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

.table {
  flex: 1;
  min-width: 300px;
}

.echart {
  width: 100%;
  height: 300px;
}
</style>
