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
          <el-option v-for="p in [1,2,3,4]" :key="p" :label="`P${p}`" :value="p" />
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
import moment from 'moment'

export default {
  props: ['id'],
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
      categoryOptions: []
    }
  },
  async created() {
    const res = await incidentApi.getCategories()
    this.categoryOptions = this.buildTree(res.data)

    if (this.isEdit) {
      const detail = await incidentApi.detail(this.id)
      const data = detail.data
      this.form = {
        title: data.title,
        category: data.category?.id || null,
        priority: data.priority,
        occurred_at: moment(data.occurred_at).format('YYYY-MM-DD HH:mm:ss'),
        description: data.description
      }
    }
  },
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

        const payload = {
          ...this.form,
          category: this.form.category || null
        }

        try {
          if (this.isEdit) {
            await incidentApi.update(this.id, payload)
          } else {
            await incidentApi.create(payload)
          }
          this.$message.success('操作成功')
          this.$router.push('/incidents')
        } catch (err) {
          this.$message.error('操作失败')
        }
      })
    }
  }
}
</script>
