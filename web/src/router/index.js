import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/* Router Modules */
// import nestedRouter from './modules/nested'
// import tableRouter from './modules/table'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: 'Dashboard', icon: 'dashboard' }
    }]
  },

  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/user',
    name: 'Profile',
    meta: { title: '用户中心', icon: 'user' },
    children: [
      {
        path: 'user',
        component: () => import('@/views/profile/user/index'),
        name: 'UserProfile',
        meta: { title: '用户信息', icon: 'user' }
      },
      {
        path: 'role',
        component: () => import('@/views/profile/role/index'),
        name: 'RoleProfile',
        meta: { title: '角色信息', icon: 'user' }
      },
      {
        path: 'permission',
        component: () => import('@/views/profile/permission/index'),
        name: 'PermissionProfile',
        meta: { title: '权限信息', icon: 'user' }
      }
    ]
  },
  {
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
        meta: { title: '分类信息', icon: 'tree' }
      },
      {
        path: 'incident',
        component: () => import('@/views/activities/incidents/IncidentList.vue'),
        name: 'Incident',
        meta: { title: '事件信息', icon: 'tree' }
      },
      {
        path: 'standard',
        component: () => import('@/views/activities/standard/SLAList.vue'),
        name: 'Standard',
        meta: { title: '时效信息', icon: 'tree' }
      },
      { path: '/incidents/create', component: () => import('@/views/activities/incidents/IncidentForm.vue'),
        name: 'IncidentCreate',
        meta: { title: '创建事件', icon: 'tree' },
        hidden: true
      },
      { path: '/incidents/:id', component: () => import('@/views/activities/incidents/IncidentDetail.vue'),
        name: 'IncidentDetail',
        meta: { title: '事件详情', icon: 'tree' },
        props: true,
        hidden: true
      },
      { path: '/incidents/:id/edit', component: () => import('@/views/activities/incidents/IncidentForm.vue'),
        name: 'IncidentEdit',
        meta: { title: '修改事件', icon: 'tree' },
        props: true,
        hidden: true
      }
    ]
  },

  /** when your routing map is too long, you can split it into small modules **/
  // tableRouter,
  // nestedRouter,
  {
    path: '/form',
    component: Layout,
    children: [
      {
        path: 'index',
        name: 'Form',
        component: () => import('@/views/form/index'),
        meta: { title: 'Form', icon: 'form' }
      }
    ]
  },
  {
    path: 'external-link',
    component: Layout,
    children: [
      {
        path: 'https://panjiachen.github.io/vue-element-admin-site/#/',
        meta: { title: 'External Link', icon: 'link' }
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
