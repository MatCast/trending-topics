/**
 * API composable — $fetch wrapper that attaches Firebase ID token.
 */
export function useApi() {
  const config = useRuntimeConfig()
  const { getIdToken } = useAuth()

  async function apiFetch<T>(path: string, options: any = {}): Promise<T> {
    const token = await getIdToken()
    if (!token) {
      throw new Error('Not authenticated')
    }

    const baseUrl = config.public.apiBaseUrl
    return $fetch<T>(`${baseUrl}${path}`, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    })
  }

  return { apiFetch }
}
