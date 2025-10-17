<template>
  <div class="incident-statistics">
    <!-- 指标卡片区域 -->
    <el-row :gutter="24" style="margin-bottom: 24px;">
      <el-col v-for="(item, index) in statCards" :key="index" :xs="12" :sm="6">
        <el-card
          class="stat-card"
          shadow="never"
          :style="{ backgroundColor: item.cardBgColor }"
        >
          <div class="stat-content">
            <div class="icon-wrapper" :style="{ color: item.iconColor }">
              <i :class="item.icon" />
            </div>
            <div class="text-wrapper">
              <div class="label">{{ item.label }}</div>
              <div class="value">{{ item.value }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类 & 优先级统计 -->
    <el-row :gutter="24" style="margin-bottom: 24px;">
      <el-col :xs="24" :md="12">
        <el-card class="stat-table-card" shadow="never">
          <div slot="header" class="card-header">
            <span>按分类统计</span>
          </div>
          <el-table
            :data="categoryStats"
            size="small"
            style="width: 100%"
            :show-header="false"
          >
            <el-table-column prop="category__name" width="140">
              <template #default="{ row }">
                <span class="category-name">{{ row.category__name }}</span>
              </template>
            </el-table-column>
            <el-table-column>
              <template #default="{ row }">
                <div class="progress-bar">
                  <el-progress
                    :percentage="getPercentage(row.count, stats.total_incidents)"
                    :show-text="false"
                    :stroke-width="8"
                    :color="progressColor"
                  />
                  <span class="count">{{ row.count }} ({{ getPercentage(row.count, stats.total_incidents) }}%)</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="stat-table-card" shadow="never">
          <div slot="header" class="card-header">
            <span>按优先级统计</span>
          </div>
          <el-table
            :data="priorityStats"
            size="small"
            style="width: 100%"
            :show-header="false"
          >
            <el-table-column prop="priority_display" width="120">
              <template #default="{ row }">
                <el-tag
                  :type="getPriorityTagType(row.priority)"
                  size="mini"
                  effect="plain"
                >
                  {{ row.priority_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column>
              <template #default="{ row }">
                <div class="progress-bar">
                  <el-progress
                    :percentage="getPercentage(row.count, stats.total_incidents)"
                    :show-text="false"
                    :stroke-width="8"
                    :color="progressColor"
                  />
                  <span class="count">{{ row.count }} ({{ getPercentage(row.count, stats.total_incidents) }}%)</span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图 -->
    <el-card class="trend-card" shadow="never">
      <div slot="header" class="card-header">
        <span>近30天事件趋势</span>
      </div>
      <div ref="trendChart" style="height: 360px; width: 100%;" />
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { incidentApi } from '@/api/incident'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        total_incidents: 0,
        unresolved: 0,
        overdue: 0,
        average_resolve_time_hours: 0
      },
      categoryStats: [],
      priorityStats: [],
      trendData: [],
      progressColor: '#409EFF'
    }
  },
  computed: {
    statCards() {
      return [
        {
          label: '事件总数',
          value: this.stats.total_incidents,
          icon: 'el-icon-s-data',
          cardBgColor: '#ecf5ff', // 浅蓝色背景
          iconColor: '#409EFF' // 图标颜色
        },
        {
          label: '未解决',
          value: this.stats.unresolved,
          icon: 'el-icon-warning',
          cardBgColor: '#fdf6ec', // 浅橙色背景
          iconColor: '#E6A23C'
        },
        {
          label: '已超时',
          value: this.stats.overdue,
          icon: 'el-icon-alarm-clock',
          cardBgColor: '#fef0f0', // 浅红色背景
          iconColor: '#F56C6C'
        },
        {
          label: '平均解决时长（小时）',
          value: this.stats.average_resolve_time_hours.toFixed(2),
          icon: 'el-icon-timer',
          cardBgColor: '#f0f9eb', // 浅绿色背景
          iconColor: '#67C23A'
        }
      ]
    }
  },
  async mounted() {
    await this.loadAllStats()
    this.renderTrendChart()
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose()
    }
  },
  methods: {
    async loadAllStats() {
      try {
        const [generalRes, categoryRes, priorityRes, trendRes] = await Promise.all([
          incidentApi.generalStatistics(),
          incidentApi.statsByCategory(),
          incidentApi.statsByPriority(),
          incidentApi.incidentTrend()
        ])
        this.stats = generalRes.data
        this.categoryStats = categoryRes.data
        this.priorityStats = priorityRes.data
        this.trendData = trendRes.data
      } catch (err) {
        console.error('加载统计失败:', err)
        this.$message.error('加载统计数据失败')
      }
    },

    getPercentage(count, total) {
      if (!total || total === 0) return 0
      return Math.round((count / total) * 100)
    },

    getPriorityTagType(priority) {
      // 假设 priority: 1=紧急, 2=高, 3=中, 4=低
      const map = { 1: 'danger', 2: 'warning', 3: 'info', 4: '' }
      return map[priority] || ''
    },

    renderTrendChart() {
      const chartDom = this.$refs.trendChart
      if (!chartDom) return

      const myChart = echarts.init(chartDom)
      this.chartInstance = myChart

      const data = this.trendData.map(item => item.count)
      const dates = this.trendData.map(item => item.date)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          backgroundColor: 'rgba(0,0,0,0.75)',
          borderColor: '#409EFF',
          borderWidth: 1,
          textStyle: { color: '#fff' }
        },
        grid: {
          left: '2%',
          right: '2%',
          bottom: '10%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisTick: { show: false },
          axisLine: { lineStyle: { color: '#dcdfe6' }},
          axisLabel: { color: '#606266', fontSize: 12 }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { lineStyle: { color: '#eee' }},
          axisLabel: { color: '#606266' }
        },
        series: [
          {
            name: '事件数',
            type: 'bar',
            data: data,
            barWidth: '60%',
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#5470c6' },
                { offset: 1, color: '#91cc75' }
              ]),
              borderRadius: [8, 8, 0, 0]
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.3)'
              }
            }
          }
        ]
      }

      myChart.setOption(option)

      window.addEventListener('resize', () => myChart.resize())
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', () => myChart.resize())
      })
    }
  }
}
</script>

<style scoped>
.incident-statistics {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  height: 100%;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  /* 如果希望文字靠左、图标靠左，已满足 */
}

.icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border-radius: 50%; /* 让图标区域成为圆形 */
  background-color: rgba(0, 0, 0, 0.05); /* 增加一个非常淡的灰色背景 */
}

.text-wrapper .label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
  font-weight: 500;
}
.text-wrapper .value {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
}

.card-header {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.stat-table-card ::v-deep .el-card__body {
  padding: 12px 0;
}

.category-name {
  color: #5a5e66;
  font-weight: 500;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.progress-bar .count {
  font-size: 13px;
  color: #606266;
  min-width: 80px;
  text-align: right;
}

.trend-card ::v-deep .el-card__body {
  padding-top: 12px;
}
</style>
