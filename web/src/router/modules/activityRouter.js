/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const activityRouter = {
  path: '/activity',
  component: Layout,
  redirect: '/activity/incident',
  name: 'Activity',
  meta: { title: '事件管理', icon: 'el-icon-s-help' },
  children: [
    {
      path: 'category',
      component: () => import('@/views/activities/category/CategoryList.vue'),
      name: 'Category',
      meta: { title: '分类信息', icon: 'tree', breadcrumb: false }
    },
    {
      path: 'incident',
      component: () => import('@/views/activities/incidents/IncidentList.vue'),
      name: 'Incident',
      meta: { title: '事件信息', icon: 'tree', breadcrumb: false }
    },
    {
      path: 'standard',
      component: () => import('@/views/activities/standard/SLAList.vue'),
      name: 'Standard',
      meta: { title: '时效信息', icon: 'tree', breadcrumb: false }
    },
    { path: '/incidents/create', component: () => import('@/views/activities/incidents/IncidentForm.vue'),
      name: 'IncidentCreate',
      meta: { title: '创建事件', icon: 'tree', breadcrumb: false },
      hidden: true
    },
    { path: '/incidents/:id', component: () => import('@/views/activities/incidents/IncidentDetail.vue'),
      name: 'IncidentDetail',
      meta: { title: '事件详情', icon: 'tree', breadcrumb: false },
      props: true,
      hidden: true
    },
    { path: '/incidents/:id/edit', component: () => import('@/views/activities/incidents/IncidentForm.vue'),
      name: 'IncidentEdit',
      meta: { title: '修改事件', icon: 'tree', breadcrumb: false },
      props: true,
      hidden: true
    }
  ]
}
export default activityRouter
