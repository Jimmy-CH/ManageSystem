<template>
  <el-dialog
    :title="dialogTitle"
    :visible.sync="dialogVisible"
    width="500px"
    @close="handleClose"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
  >
    <el-form
      ref="permissionForm"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      status-icon
    >
      <el-form-item label="权限名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入权限名称"
          clearable
        ></el-input>
      </el-form-item>

      <el-form-item label="权限标识" prop="codename">
        <el-input
          v-model="formData.codename"
          placeholder="请输入权限标识 (如: view_users)"
          clearable
        ></el-input>
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入权限描述"
        ></el-input>
      </el-form-item>

      <el-form-item label="应用标签">
        <el-input
          v-model="formData.app_label"
          placeholder="请输入应用标签 (可选)"
          clearable
        ></el-input>
      </el-form-item>
    </el-form>

    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">取 消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
        {{ isEditMode ? "修 改" : "增 加" }}
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
import { createPermission, updatePermission } from "@/api/permission";
export default {
  name: "PermissionDialog",
  props: {
    // 控制对话框显示/隐藏的 v-model
    value: {
      type: Boolean,
      required: true,
    },
    // 权限数据对象，用于编辑。新增时为 null 或 undefined
    permission: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      dialogVisible: this.value, // 同步 v-model 的值
      submitLoading: false,
      // 表单数据
      formData: {
        codename: "",
        name: "",
        description: "",
        app_label: "",
      },
      // 表单验证规则
      formRules: {
        name: [
          { required: true, message: "请输入权限名称", trigger: "blur" },
          {
            min: 2,
            max: 50,
            message: "长度在 2 到 50 个字符",
            trigger: "blur",
          },
        ],
        codename: [
          { required: true, message: "请输入权限标识", trigger: "blur" },
          {
            pattern: /^[a-z_][a-z0-9_]*$/,
            message: "只能包含小写字母、数字和下划线，且必须以字母或下划线开头",
            trigger: "blur",
          },
          {
            min: 3,
            max: 100,
            message: "长度在 3 到 100 个字符",
            trigger: "blur",
          },
        ],
        description: [
          { required: true, message: "请输入权限描述", trigger: "blur" },
          {
            min: 5,
            max: 200,
            message: "长度在 5 到 200 个字符",
            trigger: "blur",
          },
        ],
      },
    };
  },
  computed: {
    // 计算对话框标题
    dialogTitle() {
      return this.isEditMode ? "修改权限" : "新增权限";
    },
    // 判断是否为编辑模式
    isEditMode() {
      return !!this.permission;
    },
  },
  watch: {
    // 监听 v-model 的变化，同步 dialogVisible
    value(val) {
      this.dialogVisible = val;
    },
    // 监听 dialogVisible 的变化，同步 v-model
    dialogVisible(val) {
      this.$emit("input", val);
    },
    // 监听传入的 permission 对象，用于初始化表单数据
    permission: {
      handler(val) {
        if (val && this.dialogVisible) {
          // 将传入的权限数据填充到表单
          this.formData = { ...val };
        } else if (!val && this.dialogVisible) {
          // 新增模式，清空表单
          this.$refs.permissionForm.resetForm();
        }
      },
      immediate: true, // 立即执行一次，确保初始化
    },
  },
  methods: {
    // 重置表单
    resetForm() {
      this.$refs.permissionForm.resetFields();
      // 注意：resetFields 不会重置没有在 rules 里的字段 (如 app_label)，需要手动重置
      this.formData.app_label = "";
    },
    // 处理取消/关闭
    handleClose() {
      this.$emit("input", false); // 关闭对话框
      this.$nextTick(() => {
        this.resetForm(); // 延迟重置表单，避免关闭动画时重置
      });
    },
    // 处理提交
    // **关键修改：使用实际的 API 调用**
    handleSubmit() {
      this.$refs.permissionForm.validate((valid) => {
        if (valid) {
          this.submitLoading = true;
          const requestData = { ...this.formData }; // 创建数据副本

          // **调用实际的 API**
          let apiCall;
          if (this.isEditMode) {
            // **重要：修改时，通常需要包含 ID 或主键**
            // 您的 updatePermission API 使用 PUT 到 /accounts/permissions/
            // 这通常意味着需要在 URL 中包含 ID，或者在数据中包含 ID
            // **请确认您的后端 API 是如何处理更新的！**
            // **常见情况1：PUT /accounts/permissions/:id**
            // **常见情况2：PUT /accounts/permissions/ 并在 data 中包含 id 字段**

            // **假设您的后端期望在 data 中包含一个 'id' 字段来标识更新哪个对象**
            // **您需要确保传入的 permission 对象包含 'id'**
            if (!requestData.id) {
              this.$message.error("无法确定要修改的权限ID！");
              this.submitLoading = false;
              return;
            }
            apiCall = updatePermission(requestData);

            // **假设您的后端期望 URL 包含 ID (更常见)**
            // 这需要修改 updatePermission 函数或在这里处理
            // 例如，如果您的函数是 updatePermission(id, data)
            // apiCall = updatePermission(this.permission.id, requestData);

            // **由于您提供的 updatePermission 函数签名是 updatePermission(data)，**
            // **我们暂时按 data 包含 id 的方式调用，但请务必根据后端实际要求调整！**
          } else {
            apiCall = createPermission(requestData);
          }

          // 执行 API 调用
          apiCall
            .then((response) => {
              // **成功处理**
              this.$message.success(
                this.isEditMode ? "权限修改成功！" : "权限新增成功！"
              );
              // 通过 submit 事件通知父组件操作成功，并传递可能更新后的数据 (response.data)
              this.$emit("submit", {
                data: response.data || requestData, // 优先使用返回的数据，否则用提交的数据
                isEdit: this.isEditMode,
              });
              // 关闭对话框
              this.handleClose();
            })
            .catch((error) => {
              // **错误处理**
              const errorMsg = this.isEditMode
                ? "权限修改失败"
                : "权限新增失败";
              // 尝试从错误响应中获取更具体的错误信息
              const detail =
                error.response?.data?.detail ||
                error.response?.data?.error ||
                "未知错误";
              this.$message.error(`${errorMsg}：${detail}`);
              console.error(`${errorMsg}:`, error);
            })
            .finally(() => {
              // **无论成功或失败，都停止加载状态**
              this.submitLoading = false;
            });
        } else {
          this.$message.error("请检查表单填写是否正确！");
        }
      });
    },
  },
};
</script>

<style scoped>
/* 可以根据需要添加自定义样式 */
.dialog-footer {
  text-align: right;
}
</style>
