<template>
  <div class="incident-statistics">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <i class="el-icon-s-data" />
            <div>
              <div class="label">事件总数</div>
              <div class="value">{{ stats.total_incidents }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <i class="el-icon-warning" />
            <div>
              <div class="label">未解决</div>
              <div class="value">{{ stats.unresolved }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <i class="el-icon-alarm-clock" />
            <div>
              <div class="label">已超时</div>
              <div class="value">{{ stats.overdue }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <i class="el-icon-timer" />
            <div>
              <div class="label">平均解决时长（小时）</div>
              <div class="value">{{ stats.average_resolve_time_hours | number(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header"><span>按分类统计</span></div>
          <el-table :data="categoryStats" size="small" style="width: 100%">
            <el-table-column prop="category__name" label="分类" width="150" />
            <el-table-column prop="count" label="事件数" width="100" />
            <el-table-column label="占比">
              <template slot-scope="scope">
                {{ ((scope.row.count / stats.total_incidents) * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <div slot="header"><span>按优先级统计</span></div>
          <el-table :data="priorityStats" size="small" style="width: 100%">
            <el-table-column prop="priority_display" label="优先级" width="120" />
            <el-table-column prop="count" label="事件数" width="100" />
            <el-table-column label="占比">
              <template slot-scope="scope">
                {{ ((scope.row.count / stats.total_incidents) * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover">
      <div slot="header"><span>近30天事件趋势</span></div>
      <div ref="trendChart" style="height: 400px;" />
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { incidentApi } from '@/api/incident'

export default {
  name: 'Dashboard',
  filters: {
    number(value, digits = 2) {
      return Number(value).toFixed(digits)
    }
  },
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
      trendData: []
    }
  },
  async mounted() {
    await this.loadAllStats()
    this.renderTrendChart()
  },
  // mounted() {
  //   console.log('incidentApi:', incidentApi) // 👈 看控制台输出是不是 undefined
  //   this.loadAllStats()
  // },
  methods: {
    async loadAllStats() {
      try {
        const [
          generalRes,
          categoryRes,
          priorityRes,
          trendRes
        ] = await Promise.all([
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

    renderTrendChart() {
      const chartDom = this.$refs.trendChart
      if (!chartDom) return

      const myChart = echarts.init(chartDom)
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: this.trendData.map(item => item.date)
        },
        yAxis: {
          type: 'value',
          name: '事件数量'
        },
        series: [
          {
            name: '事件数',
            type: 'bar',
            data: this.trendData.map(item => item.count),
            itemStyle: {
              color: '#409EFF'
            }
          }
        ],
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        }
      }
      myChart.setOption(option)

      // 响应窗口大小变化
      window.addEventListener('resize', () => myChart.resize())
      this.$once('hook:beforeDestroy', () => {
        window.removeEventListener('resize', () => myChart.resize())
        myChart.dispose()
      })
    }
  }
}
</script>

<style scoped>
.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stat-item i {
  font-size: 24px;
  color: #409EFF;
}
.label {
  font-size: 14px;
  color: #909399;
}
.value {
  font-size: 24px;
  font-weight: bold;
}
</style>
