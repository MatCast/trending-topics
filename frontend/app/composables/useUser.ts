/**
 * User composable — manages user profile and tier limits.
 */
export interface UserProfile {
  uid: string;
  email: string;
  active_tier: string;
  tier_limits: {
    keywords: number;
    reddit_sources: number;
    extractions: {
      daily: number;
      weekly: number;
      monthly: number;
    };
  };
  usage: {
    extractions: {
      daily: number;
      weekly: number;
      monthly: number;
    };
  };
  settings: {
    time_window_hours: number;
    max_trends_per_source: number;
    result_retention_days: number;
    schedule: {
      type: string;
    };
  };
}

export function useUser() {
  const { apiFetch } = useApi();
  const profile = useState<UserProfile | null>("user-profile", () => null);
  const isLoading = ref(false);

  async function fetchProfile() {
    isLoading.value = true;
    try {
      const data = await apiFetch<UserProfile>("/api/users/me");
      profile.value = data;
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
    } finally {
      isLoading.value = false;
    }
  }

  const redditLimit = computed(
    () => profile.value?.tier_limits?.reddit_sources ?? 3,
  );
  const isRedditUnlimited = computed(() => redditLimit.value === -1);

  const keywordLimit = computed(
    () => profile.value?.tier_limits?.keywords ?? 20,
  );
  const isKeywordUnlimited = computed(() => keywordLimit.value === -1);

  const extractionLimits = computed(
    () =>
      profile.value?.tier_limits?.extractions ?? {
        daily: 1,
        weekly: 2,
        monthly: 3,
      },
  );
  const extractionUsage = computed(
    () =>
      profile.value?.usage?.extractions ?? { daily: 0, weekly: 0, monthly: 0 },
  );
  const isFreeTier = computed(() => profile.value?.active_tier === "free");

  const isDailyLimitReached = computed(() => {
    const limit = extractionLimits.value.daily;
    return limit !== -1 && extractionUsage.value.daily >= limit;
  });

  const isWeeklyLimitReached = computed(() => {
    const limit = extractionLimits.value.weekly;
    return limit !== -1 && extractionUsage.value.weekly >= limit;
  });

  const isMonthlyLimitReached = computed(() => {
    const limit = extractionLimits.value.monthly;
    return limit !== -1 && extractionUsage.value.monthly >= limit;
  });

  const isAnyLimitReached = computed(
    () =>
      isDailyLimitReached.value ||
      isWeeklyLimitReached.value ||
      isMonthlyLimitReached.value,
  );

  return {
    profile,
    isLoading,
    fetchProfile,
    redditLimit,
    isRedditUnlimited,
    keywordLimit,
    isKeywordUnlimited,
    extractionLimits,
    extractionUsage,
    isFreeTier,
    isDailyLimitReached,
    isWeeklyLimitReached,
    isMonthlyLimitReached,
    isAnyLimitReached,
  };
}
