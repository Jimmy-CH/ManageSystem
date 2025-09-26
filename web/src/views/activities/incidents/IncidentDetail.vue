<template>
  <el-card>
    <h2>{{ incident.title }}</h2>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="分类">{{ incident.category?.name || '无' }}</el-descriptions-item>
      <el-descriptions-item label="优先级">P{{ incident.priority }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ statusMap[incident.status] }}</el-descriptions-item>
      <el-descriptions-item label="发生时间">{{ formatDate(incident.occurred_at) }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ formatDate(incident.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="SLA">{{ incident.sla?.level_name || '无' }}</el-descriptions-item>
    </el-descriptions>

    <h3 style="margin-top: 20px">事件描述</h3>
    <p>{{ incident.description }}</p>

    <h3>关联故障</h3>
    <el-table v-if="faults.length" :data="faults" style="margin-top:10px">
      <el-table-column prop="detail" label="故障详情" />
      <el-table-column prop="downtime_minutes" label="停机(分钟)" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">{{ statusMap[scope.row.status] }}</template>
      </el-table-column>
    </el-table>
    <el-alert v-else title="暂无故障记录" type="info" style="margin-top: 10px" />

    <div style="margin-top:20px">
      <el-button @click="$router.back()">返回</el-button>
      <el-button type="primary" @click="$router.push(`/incidents/${incident.id}/edit`)">编辑</el-button>
    </div>
  </el-card>
</template>

<script>
import { incidentApi } from '@/api/incident'

export default {
  props: ['id'],
  data() {
    return {
      incident: {},
      faults: [],
      statusMap: { 0: '待处理', 1: '处理中', 2: '已解决', 3: '已关闭' }
    }
  },
  async created() {
    const [incidentRes, faultRes] = await Promise.all([
      incidentApi.detail(this.id),
      incidentApi.getFaults(this.id)
    ])
    this.incident = incidentRes.data
    this.faults = faultRes.data
  },
  methods: {
    formatDate(date) {
      return date ? new Date(date).toLocaleString() : ''
    }
  }
}
</script>
