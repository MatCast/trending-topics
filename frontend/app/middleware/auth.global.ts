/**
 * Global auth middleware — redirects unauthenticated users to /login.
 */
export default defineNuxtRouteMiddleware((to) => {
  // Skip auth check for login page
  if (to.path === '/login') return

  const { isAuthenticated, isLoading } = useAuth()

  // Wait for auth to initialize
  if (isLoading.value) return

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
