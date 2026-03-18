/**
 * User composable — manages user profile and tier limits.
 */
export interface UserProfile {
  uid: string
  email: string
  active_tier: string
  tier_limits: {
    keywords: number
    reddit_sources: number
  }
  settings: {
    time_window_hours: number
    max_trends_per_source: number
    result_retention_days: number
    schedule: {
      type: string
    }
  }
}

export function useUser() {
  const { apiFetch } = useApi()
  const profile = useState<UserProfile | null>('user-profile', () => null)
  const isLoading = ref(false)

  async function fetchProfile() {
    isLoading.value = true
    try {
      const data = await apiFetch<UserProfile>('/api/users/me')
      profile.value = data
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
    } finally {
      isLoading.value = false
    }
  }

  const redditLimit = computed(() => profile.value?.tier_limits?.reddit_sources ?? 3)
  const isRedditUnlimited = computed(() => redditLimit.value === -1)
  
  const keywordLimit = computed(() => profile.value?.tier_limits?.keywords ?? 20)
  const isKeywordUnlimited = computed(() => keywordLimit.value === -1)

  return {
    profile,
    isLoading,
    fetchProfile,
    redditLimit,
    isRedditUnlimited,
    keywordLimit,
    isKeywordUnlimited,
  }
}
