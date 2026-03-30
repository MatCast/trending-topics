import { computed } from 'vue'
import { useSettings } from './useSettings'

export function useScheduleToggle() {
  const { schedule, saveSettings, isSaving } = useSettings()

  async function toggle(val: boolean) {
    if (isSaving.value) return
    const prev = schedule.value.active
    schedule.value.active = val
    const ok = await saveSettings()
    if (!ok) {
      schedule.value.active = prev
    }
  }

  return {
    active: computed(() => schedule.value.active),
    isSaving,
    toggle
  }
}
