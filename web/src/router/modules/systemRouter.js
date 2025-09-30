/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const systemRouter = {
  path: '/system',
  component: Layout,
  redirect: '/system/system-config',
  name: 'System',
  meta: { title: '系统管理', icon: 'guide' },
  children: [
    {
      path: 'system-config',
      component: () => import('@/views/system/SystemConfig.vue'),
      name: 'SystemConfig',
      meta: { title: '系统配置', icon: 'lock', breadcrumb: false }
    },
    {
      path: 'menu',
      component: () => import('@/views/system/MenuManage.vue'),
      name: 'Menu',
      meta: { title: '菜单信息', icon: 'lock', breadcrumb: false }
    },
    {
      path: 'storage',
      component: () => import('@/views/system/StorageConfig.vue'),
      name: 'Storage',
      meta: { title: '存储信息', icon: 'lock', breadcrumb: false }
    }
  ]
}
export default systemRouter
