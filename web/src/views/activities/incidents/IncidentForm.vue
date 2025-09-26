<template>
  <el-card>
    <h2>{{ isEdit ? '编辑事件' : '新建事件' }}</h2>
    <el-form ref="form" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="分类">
        <el-cascader
          v-model="form.category"
          :options="categoryOptions"
          :props="{ value: 'id', label: 'name', children: 'children', checkStrictly: true }"
          clearable
          placeholder="请选择分类"
        />
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-select v-model="form.priority">
          <el-option
            v-for="opt in priorityOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="发生时间" prop="occurred_at">
        <el-date-picker
          v-model="form.occurred_at"
          type="datetime"
          value-format="yyyy-MM-dd HH:mm:ss"
          placeholder="选择时间"
        />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submit">保存</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
import { incidentApi } from '@/api/incident'
import { categoryApi } from '@/api/category' // ✅ 新增导入
import moment from 'moment'

export default {
  props: {
    id: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      isEdit: !!this.id,
      form: {
        title: '',
        category: null,
        priority: 2,
        occurred_at: moment().format('YYYY-MM-DD HH:mm:ss'),
        description: ''
      },
      rules: {
        title: [{ required: true, message: '请输入标题' }],
        description: [{ required: true, message: '请输入描述' }]
      },
      categoryOptions: [],
      // data 中添加
      priorityOptions: [
        { value: 1, label: '低' },
        { value: 2, label: '中' },
        { value: 3, label: '高' },
        { value: 4, label: '紧急' }
      ]
    }
  },
  async created() {
    try {
      // ✅ 使用 categoryApi 而不是 incidentApi.getCategories
      const res = await categoryApi.list()
      this.categoryOptions = this.buildTree(res.data.results || [])

      if (this.isEdit) {
        const detail = await incidentApi.detail(this.id)
        const data = detail.data
        this.form = {
          title: data.title,
          // 注意：cascader 的 v-model 是数组，但你传的是单个 ID？
          category: data.category ? [data.category] : null, // 👈 修正点
          priority: data.priority,
          occurred_at: moment(data.occurred_at).format('YYYY-MM-DD HH:mm:ss'),
          description: data.description
        }
      }
    } catch (err) {
      console.error('加载数据失败:', err)
      this.$message.error('初始化表单失败')
    }
  },
  // async created() {
  //   try {
  //     const res = await categoryApi.list()
  //     this.categoryOptions = this.buildTree(res.data.results || [])

  //     if (this.isEdit) {
  //       const detail = await incidentApi.detail(this.id)
  //       const data = detail.data

  //       // 确保 category 是 ID（兼容对象或 ID）
  //       const categoryId = data.category
  //         ? (typeof data.category === 'object' ? data.category.id : data.category)
  //         : null

  //       this.form = {
  //         title: data.title,
  //         category: categoryId ? [categoryId] : null,
  //         priority: data.priority,
  //         occurred_at: moment(data.occurred_at).format('YYYY-MM-DD HH:mm:ss'),
  //         description: data.description
  //       }
  //     }
  //   } catch (err) {
  //     console.error('加载数据失败:', err)
  //     this.$message.error('初始化表单失败')
  //   }
  // },
  methods: {
    buildTree(list, parentId = null) {
      return list
        .filter(item => item.parent === parentId)
        .map(item => ({
          ...item,
          children: this.buildTree(list, item.id)
        }))
    },
    async submit() {
      this.$refs.form.validate(async valid => {
        if (!valid) return

        // 注意：el-cascader 的值是数组，如 [1, 2]，但后端只需要最终叶子节点 ID
        const categoryId = Array.isArray(this.form.category)
          ? this.form.category[this.form.category.length - 1]
          : null

        const payload = {
          ...this.form,
          category: categoryId // 传单个 ID 给后端
        }

        try {
          if (this.isEdit) {
            await incidentApi.update(this.id, payload)
          } else {
            await incidentApi.create(payload)
          }
          this.$message.success('操作成功')
          this.$router.push('/activity/incident')
        } catch (err) {
          this.$message.error('操作失败')
        }
      })
    }
  }
}
</script>

