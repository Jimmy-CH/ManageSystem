<!-- src/views/PersonnelManagement.vue -->
<template>
  <div class="personnel-management">
    <!-- Tab 导航 -->
    <el-tabs v-model="activeTab" class="tabs-container" @tab-click="handleTabClick">
      <el-tab-pane label="人员进出管理" name="management" />
      <el-tab-pane label="人员进出汇总" name="summary" />
    </el-tabs>

    <!-- Tab 内容区 -->
    <div class="tab-content">
      <!-- 人员进出管理 -->
      <PersonnelList
        v-if="activeTab === 'management'"
        ref="personnelList"
        @search="handleSearch"
      />

      <!-- 人员进出汇总 -->
      <PersonnelSummary
        v-if="activeTab === 'summary'"
        ref="personnelSummary"
      />
    </div>
  </div>
</template>

<script>
import PersonnelList from '@/views/record/components/PersonnelList.vue'
import PersonnelSummary from '@/views/record/components/PersonnelSummary.vue'

export default {
  name: 'PersonnelManagement',
  components: {
    PersonnelList,
    PersonnelSummary
  },
  data() {
    return {
      activeTab: 'management' // 默认显示管理页
    }
  },
  methods: {
    handleTabClick(tab) {
      console.log('切换到 Tab:', tab.name)
      // 可选：在切换时触发子组件的刷新方法
      if (tab.name === 'summary' && this.$refs.personnelSummary) {
        // 例如：this.$refs.personnelSummary.loadData()
      }
    },
    handleSearch(params) {
      console.log('搜索参数:', params)
    }
  }
}
</script>

<style scoped>
.personnel-management {
  width: 100%;
  background: #f5f7fa;
  min-height: 100vh;
}

.tabs-container {
  margin-bottom: 20px;
  margin-left: 20px;
}

.tab-content {
  padding: 0 20px;
}
</style>
