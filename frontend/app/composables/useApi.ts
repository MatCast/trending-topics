/**
 * API composable — $fetch wrapper that attaches Firebase ID token.
 */
export function useApi() {
  const config = useRuntimeConfig();
  const { getIdToken } = useAuth();

  async function apiFetch<T>(path: string, options: any = {}): Promise<T> {
    console.log("[apiFetch] getting token...");
    const token = await getIdToken();
    console.log("[apiFetch] got token:", !!token);
    if (!token) {
      throw new Error("Not authenticated");
    }
    const baseUrl = config.public.apiBaseUrl
  const url = `${baseUrl}${path}`
  console.log('[apiFetch] fetching:', options.method || 'GET', url)

    try {
      const result = await $fetch<T>(url, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: `Bearer ${token}`,
        },
      });
      console.log("[apiFetch] completed:", options.method || "GET", url);
      return result;
    } catch (e) {
      console.error("[apiFetch] threw:", options.method || "GET", url, e);
      throw e;
    }
  }

  return { apiFetch };
}
