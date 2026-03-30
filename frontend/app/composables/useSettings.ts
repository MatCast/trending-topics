import { ref } from "vue";
import { useApi } from "./useApi";
import { useUser } from "./useUser";

// Global state so modal and settings page share the same data
const settings = ref<any>({
  time_window_hours: 3,
  max_trends_per_source: 3,
  reddit_fetch_method: "rapidapi",
});

const schedule = ref<any>({
  active: false,
  type: "manual",
  interval_hours: 3,
  hour_of_day: 9,
  day_of_week: 0,
});

const isLoading = ref(true);
const isSaving = ref(false);

export function useSettings() {
  const { apiFetch } = useApi();
  const { fetchProfile } = useUser();

  async function fetchSettings() {
    isLoading.value = true;
    try {
      const data = await apiFetch<any>("/api/settings");
      settings.value = {
        time_window_hours: data.time_window_hours || 3,
        max_trends_per_source: data.max_trends_per_source || 3,
        reddit_fetch_method: data.reddit_fetch_method || "rapidapi",
      };
      schedule.value = {
        ...data.schedule,
        active: data.schedule?.active === true,
        type: data.schedule?.type || "manual",
        interval_hours: data.schedule?.interval_hours || 3,
        hour_of_day: data.schedule?.hour_of_day || 9,
        day_of_week: data.schedule?.day_of_week || 0,
      };
    } catch (error) {
      console.error("Failed to fetch settings:", error);
    } finally {
      isLoading.value = false;
    }
  }

  async function saveSettings(): Promise<boolean> {
    console.log("[saveSettings] called | isSaving:", isSaving.value);
    if (isSaving.value) return false;
    isSaving.value = true;
    try {
      console.log("[saveSettings] firing apiFetch with", {
        ...settings.value,
        schedule: schedule.value,
      });
      await apiFetch("/api/settings", {
        method: "PUT",
        body: { ...settings.value, schedule: schedule.value },
      });
      console.log("[saveSettings] apiFetch succeeded");
      return true;
    } catch (error) {
      console.error("[saveSettings] apiFetch FAILED", error);
      return false;
    } finally {
      isSaving.value = false;
    }
  }

  return {
    settings,
    schedule,
    isLoading,
    isSaving,
    fetchSettings,
    saveSettings,
  };
}
