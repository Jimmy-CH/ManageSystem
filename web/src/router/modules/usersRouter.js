/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const usersRouter = {
  path: '/users',
  component: Layout,
  redirect: '/users/info',
  name: 'Users',
  meta: { title: '用户中心', icon: 'user' },
  children: [
    {
      path: 'info',
      component: () => import('@/views/users/UserLIst.vue'),
      name: 'UserInfo',
      meta: { title: '用户信息', icon: 'user', breadcrumb: false }
    },
    {
      path: 'role',
      component: () => import('@/views/users/RoleList.vue'),
      name: 'RoleInfo',
      meta: { title: '角色信息', icon: 'user', breadcrumb: false }
    },
    {
      path: 'permission',
      component: () => import('@/views/users/PermissionList.vue'),
      name: 'PermissionInfo',
      meta: { title: '权限信息', icon: 'user', breadcrumb: false }
    }
  ]
}
export default usersRouter
