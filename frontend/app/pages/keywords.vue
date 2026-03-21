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
          <div class="flex items-start justify-between mb-2">
            <div>
              <h2 class="card-title text-base mb-1">Add Keywords</h2>
              <p class="text-base-content/60 text-xs m-0">Separate multiple keywords with commas.</p>
            </div>
            <UsageLimitBadge :current="activeKeywordCount" :limit="keywordLimit" type="active" />
          </div>
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
          <div v-if="addError || isLimitReached" class="mt-1">
            <p v-if="addError" class="text-error text-xs">{{ addError }}</p>
            <div v-else-if="isLimitReached" class="text-warning text-xs flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>At active limit. New keywords will be disabled.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Bulk Actions Bar -->
      <div v-if="selectedIds.size > 0" class="flex flex-wrap items-center gap-2 p-3 bg-base-300 rounded-xl sticky top-16 z-10 shadow-sm">
        <span class="text-sm font-medium w-full md:w-auto text-center md:text-left">{{ selectedIds.size }} selected</span>
        <div class="flex flex-1 justify-center md:justify-start gap-2">
          <button class="btn btn-success btn-xs" @click="bulkAction('enable')">Enable</button>
          <button class="btn btn-warning btn-xs" @click="bulkAction('disable')">Disable</button>
          <button class="btn btn-error btn-xs" @click="bulkAction('delete')">Delete</button>
        </div>
        <button class="btn btn-ghost btn-xs w-full md:w-auto md:ml-auto" @click="selectedIds.clear()">Clear selection</button>
      </div>

      <!-- Keywords List / Table -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body p-0" v-if="keywords.length">
          
          <!-- Desktop Table -->
          <div class="hidden md:block overflow-x-auto">
            <table class="table w-full">
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
                  :key="`desktop-${kw.id}`"
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
                      :checked="kw.enabled"
                      @change="toggleEnabled($event, kw)"
                    />
                  </td>
                  <td class="text-xs text-base-content/60">{{ formatDate(kw.created_at) }}</td>
                  <td>
                    <button class="btn btn-ghost btn-xs btn-square text-error" @click="deleteSingle(kw)">✕</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Cards -->
          <div class="md:hidden flex flex-col gap-0 divide-y divide-base-300">
            <!-- Mobile Select All Bar -->
            <div class="flex items-center justify-between p-4 bg-base-200/50">
              <label class="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  class="checkbox checkbox-sm"
                  :checked="isAllSelected"
                  :indeterminate="isPartiallySelected"
                  @change="toggleSelectAll"
                />
                <span class="text-xs font-semibold uppercase tracking-wider text-base-content/60">Select All</span>
              </label>
            </div>
            
            <div
              v-for="kw in keywords"
              :key="`mobile-${kw.id}`"
              class="flex flex-col p-4 gap-3 bg-base-100"
              :class="{ 'opacity-60': !kw.enabled, 'bg-base-200/40': selectedIds.has(kw.id) }"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                  <input
                    type="checkbox"
                    class="checkbox checkbox-sm mt-1 border-base-content/30"
                    :checked="selectedIds.has(kw.id)"
                    @change="toggleSelect(kw.id)"
                  />
                  <div>
                    <span class="font-bold text-base-content block">{{ kw.text }}</span>
                    <span class="text-[10px] text-base-content/50 uppercase tracking-wider font-semibold">{{ formatDate(kw.created_at) }}</span>
                  </div>
                </div>
                <button class="btn btn-ghost btn-xs btn-circle text-error" @click="deleteSingle(kw)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
              <div class="flex items-center justify-between pl-8">
                <span class="text-xs font-medium text-base-content/70">Status</span>
                <input
                  type="checkbox"
                  class="toggle toggle-sm toggle-success"
                  :checked="kw.enabled"
                  @change="toggleEnabled($event, kw)"
                />
              </div>
            </div>
          </div>
        </div>

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
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { keywordLimit, isKeywordUnlimited, fetchProfile } = useUser()

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

const activeKeywordCount = computed(() => keywords.value.filter(k => k.enabled).length)

const isLimitReached = computed(() => {
  if (isKeywordUnlimited.value) return false
  return activeKeywordCount.value >= keywordLimit.value
})

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

async function toggleEnabled(event: Event, kw: any) {
  const target = event.target as HTMLInputElement
  const newValue = target.checked;

  if (newValue && isLimitReached.value) {
    target.checked = false;
    addError.value = 'Active limit reached. Disable another keyword first.';
    return;
  }

  kw.enabled = newValue;
  try {
    await apiFetch(`/api/keywords/${kw.id}`, {
      method: 'PUT',
      body: { enabled: kw.enabled },
    })
    addError.value = ''
  } catch (error: any) {
    console.error('Failed to toggle keyword:', error)
    kw.enabled = !kw.enabled // revert
    target.checked = kw.enabled
    addError.value = error.data?.detail || 'Failed to toggle keyword.'
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

onMounted(() => {
  fetchKeywords()
  fetchProfile()
})
</script>
