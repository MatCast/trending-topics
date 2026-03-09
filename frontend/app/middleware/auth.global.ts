/**
 * Global auth middleware — redirects unauthenticated users to /login.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  // Skip auth check for login page
  if (to.path === '/login') return

  const { isAuthenticated, waitForAuth } = useAuth()

  // Wait for auth to initialize on the client
  await waitForAuth()

  if (!isAuthenticated.value) {
    return navigateTo('/login')
  }
})
