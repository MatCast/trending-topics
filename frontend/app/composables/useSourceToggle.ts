import { ref } from 'vue'
import { useApi } from './useApi'
import { toast } from 'vue-sonner'

export function useSourceToggle() {
  const { apiFetch } = useApi()
  const isSaving = ref(false)

  async function toggleStatus(src: any, newValue: boolean, errorCallback?: (msg: string) => void) {
    const originalState = src.enabled
    src.enabled = newValue
    isSaving.value = true

    try {
      const updated = await apiFetch<any>(`/api/sources/${src.id}`, {
        method: 'PUT',
        body: { enabled: src.enabled },
      })
      src.enabled = updated.enabled
      toast.success(`${src.name} ${src.enabled ? 'enabled' : 'disabled'}`)
    } catch (error: any) {
      console.error('Failed to toggle source:', error)
      src.enabled = originalState
      const detail = error.data?.detail || 'Limit reached. Disable another to enable this one.'
      if (errorCallback) errorCallback(detail)
      toast.error('Action failed', { description: detail })
    } finally {
      isSaving.value = false
    }
  }

  async function toggleGlobalKeywords(src: any, newValue: boolean) {
    const originalState = src.use_global_keywords
    src.use_global_keywords = newValue
    isSaving.value = true

    try {
      await apiFetch(`/api/sources/${src.id}`, {
        method: 'PUT',
        body: { use_global_keywords: src.use_global_keywords },
      })
      toast.success(`Updated ${src.name} settings`)
    } catch (error) {
      console.error('Failed to update source:', error)
      src.use_global_keywords = originalState
      toast.error('Failed to update source settings')
    } finally {
      isSaving.value = false
    }
  }

  return { toggleStatus, toggleGlobalKeywords, isSaving }
}
