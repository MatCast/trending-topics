import { ref } from 'vue'
import { useApi } from './useApi'
import { toast } from 'vue-sonner'

export function useKeywordToggle() {
  const { apiFetch } = useApi()
  const isSaving = ref(false)

  async function toggle(kw: any, newValue: boolean, isLimitReached: boolean) {
    if (newValue && isLimitReached) {
      toast.error('Limit reached', { description: 'Active limit reached. Disable another keyword first.' })
      return
    }

    const prev = kw.enabled
    kw.enabled = newValue
    isSaving.value = true

    try {
      await apiFetch(`/api/keywords/${kw.id}`, {
        method: 'PUT',
        body: { enabled: kw.enabled },
      })
      toast.success(`Keyword ${kw.enabled ? 'enabled' : 'disabled'}`)
    } catch (error: any) {
      kw.enabled = prev
      const detail = error.data?.detail || 'Failed to toggle keyword.'
      toast.error('Action failed', { description: detail })
    } finally {
      isSaving.value = false
    }
  }

  return { toggle, isSaving }
}
