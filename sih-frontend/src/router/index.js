import { createRouter, createWebHistory } from 'vue-router'
import { getUser, getPatientSession, isPatientRoute, isStaffUser, clearPatientSession } from '../services/api.js'
import {
  buildAppRoutes,
  defaultPathForUser,
  canAccessPath,
  redirectPathForUser,
  homeForRole,
} from '../config/navigation.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  ...buildAppRoutes(),
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: (to) => {
      const patient = getPatientSession()
      if (patient?.patient_id) return '/mon-espace'
      const user = getUser()
      if (!user?.role) return { path: '/login', query: { redirect: to.fullPath } }
      return defaultPathForUser(user)
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const patient = getPatientSession()
  const user = getUser()
  const staff = isStaffUser()
  const staffHome = user?.role ? defaultPathForUser(user) : null

  if (to.path === '/login') {
    if (patient?.patient_id && !staff) return next('/mon-espace')
    if (user?.role && staffHome && staffHome !== '/login') return next(staffHome)
    return next()
  }

  // Personnel hospitalier : accès complet selon le rôle (ignore session patient locale)
  if (staff) {
    if (patient?.patient_id) clearPatientSession()
    if (canAccessPath(to.path, user)) return next()
    const fallback = redirectPathForUser(user, to.path)
    if (fallback && fallback !== to.path && fallback !== '/login') {
      return next(fallback)
    }
    if (staffHome && staffHome !== to.path) return next(staffHome)
    return next()
  }

  if (patient?.patient_id) {
    if (isPatientRoute(to.path)) return next()
    return next('/mon-espace')
  }

  if (!user?.role) {
    if (to.path === '/') return next('/login')
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (canAccessPath(to.path, user)) return next()

  const fallback = redirectPathForUser(user, to.path)
  if (fallback && fallback !== to.path && fallback !== '/login') {
    return next(fallback)
  }

  if (staffHome && staffHome !== to.path) return next(staffHome)
  next()
})

export { homeForRole, defaultPathForUser }
export default router
