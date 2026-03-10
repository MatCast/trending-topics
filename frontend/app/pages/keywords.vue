<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Keywords</h1>
        <p class="text-base-content/60 text-sm">Manage keywords used to filter trending content.</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <div v-else class="space-y-6">
      <!-- Add Keywords -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title text-base">Add Keywords</h2>
          <p class="text-base-content/60 text-xs mb-2">Separate multiple keywords with commas.</p>
          <div class="join w-full">
            <input
              v-model="newKeywordInput"
              type="text"
              placeholder="e.g., AI, startup, GPT, machine learning"
              class="input input-bordered join-item flex-1"
              @keyup.enter="addKeywords"
            />
            <button
              class="btn btn-primary join-item"
              :class="{ 'btn-disabled': isAdding }"
              @click="addKeywords"
            >
              <span v-if="isAdding" class="loading loading-spinner loading-xs"></span>
              {{ isAdding ? '' : 'Add' }}
            </button>
          </div>
          <p v-if="addError" class="text-error text-xs mt-1">{{ addError }}</p>
        </div>
      </div>

      <!-- Bulk Actions Bar -->
      <div v-if="selectedIds.size > 0" class="flex items-center gap-3 p-3 bg-base-300 rounded-xl sticky top-16 z-10">
        <span class="text-sm font-medium">{{ selectedIds.size }} selected</span>
        <button class="btn btn-success btn-xs" @click="bulkAction('enable')">Enable</button>
        <button class="btn btn-warning btn-xs" @click="bulkAction('disable')">Disable</button>
        <button class="btn btn-error btn-xs" @click="bulkAction('delete')">Delete</button>
        <button class="btn btn-ghost btn-xs ml-auto" @click="selectedIds.clear()">Clear selection</button>
      </div>

      <!-- Keywords Table -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body p-0">
          <table class="table w-full" v-if="keywords.length">
            <thead>
              <tr>
                <th class="w-10">
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm"
                    :checked="isAllSelected"
                    :indeterminate="isPartiallySelected"
                    @change="toggleSelectAll"
                  />
                </th>
                <th>Keyword</th>
                <th class="w-24 text-center">Status</th>
                <th class="w-32">Added</th>
                <th class="w-16"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="kw in keywords"
                :key="kw.id"
                class="hover"
                :class="{ 'opacity-50': !kw.enabled }"
              >
                <td>
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm"
                    :checked="selectedIds.has(kw.id)"
                    @change="toggleSelect(kw.id)"
                  />
                </td>
                <td class="font-medium">{{ kw.text }}</td>
                <td class="text-center">
                  <input
                    type="checkbox"
                    class="toggle toggle-sm toggle-success"
                    v-model="kw.enabled"
                    @change="toggleEnabled(kw)"
                  />
                </td>
                <td class="text-xs text-base-content/60">{{ formatDate(kw.created_at) }}</td>
                <td>
                  <button class="btn btn-ghost btn-xs btn-square text-error" @click="deleteSingle(kw)">✕</button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty state -->
          <div v-else class="text-center py-12">
            <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-base-300 mb-3">
              <span class="text-2xl">🏷️</span>
            </div>
            <h3 class="text-lg font-semibold mb-1">No keywords yet</h3>
            <p class="text-base-content/60 text-sm">Add keywords above to start filtering trends.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()

const keywords = ref<any[]>([])
const isLoading = ref(true)
const isAdding = ref(false)
const newKeywordInput = ref('')
const addError = ref('')
const selectedIds = ref(new Set<string>())

const isAllSelected = computed(() =>
  keywords.value.length > 0 && selectedIds.value.size === keywords.value.length
)
const isPartiallySelected = computed(() =>
  selectedIds.value.size > 0 && selectedIds.value.size < keywords.value.length
)

function toggleSelect(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  // Force reactivity
  selectedIds.value = new Set(selectedIds.value)
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIds.value.clear()
  } else {
    selectedIds.value = new Set(keywords.value.map(k => k.id))
  }
}

async function fetchKeywords() {
  isLoading.value = true
  try {
    keywords.value = await apiFetch<any[]>('/api/keywords')
  } catch (error) {
    console.error('Failed to fetch keywords:', error)
  } finally {
    isLoading.value = false
  }
}

async function addKeywords() {
  const rawInput = newKeywordInput.value.trim()
  addError.value = ''
  if (!rawInput) return

  // Split by commas, trim each, filter empty
  const kwList = rawInput.split(',').map(s => s.trim()).filter(Boolean)
  if (!kwList.length) return

  isAdding.value = true
  try {
    const created = await apiFetch<any[]>('/api/keywords', {
      method: 'POST',
      body: { keywords: kwList },
    })
    keywords.value.push(...created)
    newKeywordInput.value = ''
  } catch (error: any) {
    addError.value = error.data?.detail || 'Failed to add keywords'
  } finally {
    isAdding.value = false
  }
}

async function toggleEnabled(kw: any) {
  try {
    await apiFetch(`/api/keywords/${kw.id}`, {
      method: 'PUT',
      body: { enabled: kw.enabled },
    })
  } catch (error) {
    console.error('Failed to toggle keyword:', error)
    kw.enabled = !kw.enabled // revert
  }
}

async function deleteSingle(kw: any) {
  try {
    await apiFetch(`/api/keywords/${kw.id}`, { method: 'DELETE' })
    keywords.value = keywords.value.filter(k => k.id !== kw.id)
    selectedIds.value.delete(kw.id)
    selectedIds.value = new Set(selectedIds.value)
  } catch (error) {
    console.error('Failed to delete keyword:', error)
  }
}

async function bulkAction(action: string) {
  const ids = Array.from(selectedIds.value)
  if (!ids.length) return

  try {
    await apiFetch('/api/keywords/bulk', {
      method: 'POST',
      body: { keyword_ids: ids, action },
    })

    if (action === 'delete') {
      keywords.value = keywords.value.filter(k => !selectedIds.value.has(k.id))
    } else if (action === 'enable') {
      keywords.value.forEach(k => {
        if (selectedIds.value.has(k.id)) k.enabled = true
      })
    } else if (action === 'disable') {
      keywords.value.forEach(k => {
        if (selectedIds.value.has(k.id)) k.enabled = false
      })
    }

    selectedIds.value.clear()
    selectedIds.value = new Set()
  } catch (error) {
    console.error('Bulk action failed:', error)
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(() => fetchKeywords())
</script>
