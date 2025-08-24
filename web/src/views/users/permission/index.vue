<template>
  <div class="app-container">
    <el-button @click="handleAdd()" type="primary" size="small">新增</el-button>
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      highlight-current-row
    >
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="编码">
        <template slot-scope="scope">
          {{ scope.row.codename }}
        </template>
      </el-table-column>
      <el-table-column label="名称" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="描述" width="210" align="center">
        <template slot-scope="scope">
          {{ scope.row.description }}
        </template>
      </el-table-column>
      <el-table-column
        class-name="status-col"
        label="Status"
        width="110"
        align="center"
      >
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{
            scope.row.status
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        align="center"
        prop="created_at"
        label="创建时间"
        width="200"
      >
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column
        align="center"
        prop="updated_at"
        label="更新时间"
        width="200"
      >
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="200">
        <template slot-scope="scope">
          <el-button
            @click="handleDelete(scope.row)"
            type="text"
            size="small"
            style="color: #f56c6c"
          >
            删除
          </el-button>
          <el-button @click="handleEdit(scope.row)" type="text" size="small"
            >修改</el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <!-- 引入权限对话框组件 -->
    <PermissionDialog
      v-model="showDialog"
      :permission="currentPermission"
      @submit="onPermissionSubmit"
    />
  </div>
</template>

<script>
import { getPermissionList, deletePermission } from "@/api/permission";
import PermissionDialog from "./PermissionDialog.vue";

export default {
  components: {
    PermissionDialog,
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: "success",
        draft: "gray",
        deleted: "danger",
      };
      return statusMap[status];
    },
  },
  data() {
    return {
      list: null,
      listLoading: true,
      showDialog: false,
      currentPermission: {},
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.listLoading = true;
      getPermissionList().then((response) => {
        console.log(response);
        this.list = response.data;
        this.listLoading = false;
      });
    },
    handleAdd() {
      this.currentPermission = null; // 新增时设置为 null
      this.showDialog = true;
    },
    handleEdit(permission) {
      this.currentPermission = { ...permission }; // 修改时传入权限对象的副本
      this.showDialog = true;
    },
    // 处理子组件提交的数据
    onPermissionSubmit({ data, isEdit }) {
      console.log("提交的数据:", data, "操作类型:", isEdit ? "修改" : "新增");
      // 然后刷新列表等操作
      this.fetchData();
    },
    async handleDelete(row) {
      try {
        // 1. 请求用户确认
        await this.$confirm(
          `确定要删除权限 "${row.name}" 吗？此操作不可撤销！`,
          "危险操作",
          {
            confirmButtonText: "确定删除",
            cancelButtonText: "再想想",
            type: "warning",
            confirmButtonClass: "el-button--danger", // 可选：给确认按钮加红色
          }
        );

        // 2. 开始删除，设置加载状态
        this.loading = true;

        // 3. 调用封装好的 API 函数 (使用 await)
        // deletePermission(id) 返回一个 Promise
        const response = await deletePermission(row.id);

        // 4. API 调用成功 (Promise resolve)
        console.log("删除API响应:", response); // 可以查看后端返回的具体数据

        // 6. 显示成功提示
        this.$message({
          type: "success",
          message: "权限删除成功!",
        });

        // 7. (可选) 如果删除后需要刷新整个列表（例如权限树结构复杂），可以调用
        await this.fetchData();
      } catch (error) {
        // 8. 捕获错误 (用户取消 或 API 调用失败)

        if (error && error === "cancel") {
          // 用户点击了取消
          this.$message({
            type: "info",
            message: "已取消删除",
          });
        } else {
          // API 调用失败 (Promise reject)
          // 尝试从错误对象中提取更有意义的信息
          let errorMessage = "删除失败";
          if (error && error.response) {
            // 服务器返回了错误响应 (如 404, 500, 或后端自定义错误)
            const status = error.response.status;
            const data = error.response.data;
            // 可以根据状态码或后端返回的 message 字段定制错误信息
            errorMessage += `: ${data.message || `HTTP ${status}`}`;
          } else if (error && error.message) {
            // 网络错误等
            errorMessage += `: ${error.message}`;
          }
          this.$message.error(errorMessage);
          console.error("删除权限出错:", error);
        }
      } finally {
        // 9. 无论成功或失败，最终都要关闭加载状态
        this.loading = false;
      }
    },
  },
};
</script>
