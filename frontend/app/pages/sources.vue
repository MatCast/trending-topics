<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Sources</h1>
        <p class="text-base-content/60 text-sm">Manage your trending topic sources.</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <div v-else class="space-y-6">
      <!-- Dynamic source cards from catalog -->
      <div
        v-for="catalogSource in catalog"
        :key="catalogSource.id"
        class="card bg-base-100 shadow-xl border border-base-300"
      >
        <div class="card-body">
          <!-- Source header -->
          <div class="flex items-center justify-between">
            <h2 class="card-title gap-2">
              <!-- Dynamic icon from composable -->
              <svg v-if="isSvgIcon(catalogSource.icon)" class="w-6 h-6" :class="getIconConfig(catalogSource.icon).svgClass" viewBox="0 0 24 24" fill="currentColor">
                <path :d="getIconConfig(catalogSource.icon).svgPath" />
              </svg>
              <span v-else :class="getIconConfig(catalogSource.icon).textClass">
                {{ getIconConfig(catalogSource.icon).text }}
              </span>
              {{ catalogSource.name }}
            </h2>

            <!-- Singleton: show toggle or enable button -->
            <template v-if="!catalogSource.is_multi_instance">
              <div v-if="getSingletonSource(catalogSource.id)">
                <input
                  type="checkbox"
                  class="toggle toggle-success"
                  v-model="getSingletonSource(catalogSource.id)!.enabled"
                  @change="toggleSource(getSingletonSource(catalogSource.id)!)"
                />
              </div>
              <button v-else class="btn btn-primary btn-sm" @click="addSingletonSource(catalogSource)">Enable</button>
            </template>
          </div>

          <p class="text-base-content/60 text-sm">{{ catalogSource.description }}</p>
          <a
            v-if="catalogSource.website_url"
            :href="catalogSource.website_url"
            target="_blank"
            rel="noopener"
            class="link link-hover text-xs text-base-content/40"
          >{{ catalogSource.website_url }}</a>

          <!-- Multi-instance sources: add form + list -->
          <template v-if="catalogSource.is_multi_instance">
            <!-- Dynamic config form from config_schema -->
            <div class="form-control mt-4">
              <div v-if="catalogSource.id === 'reddit'" class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold uppercase tracking-wider text-base-content/40">Add Subreddit</span>
                <span 
                  class="badge badge-sm font-bold"
                  :class="isRedditLimitReached ? 'badge-warning' : 'badge-ghost'"
                >
                  {{ redditSourceCount }} / {{ redditLimit }} active
                </span>
              </div>
              
              <div class="join w-full" v-for="(fieldSchema, fieldKey) in catalogSource.config_schema" :key="fieldKey">
                <span v-if="catalogSource.id === 'reddit'" class="join-item btn btn-disabled">r/</span>
                <input
                  v-model="multiInstanceInput[catalogSource.id]"
                  type="text"
                  :placeholder="fieldSchema.placeholder || `Add ${fieldSchema.label}...`"
                  class="input input-bordered join-item flex-1"
                  :class="{ 'input-error': multiInstanceError[catalogSource.id] }"
                  @keyup.enter="addMultiInstanceSource(catalogSource)"
                  @input="multiInstanceError[catalogSource.id] = ''"
                />
                <button 
                  class="btn btn-primary join-item" 
                  @click="addMultiInstanceSource(catalogSource)"
                >
                  Add
                </button>
              </div>

              <!-- Limit Warning (Now shown below toggles if toggle fails, but we keep a generic info here) -->
              <div v-if="isRedditLimitReached && catalogSource.id === 'reddit'" class="text-xs text-warning mt-2 flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>At active limit. New subreddits will be added as disabled.</span>
              </div>

              <label v-if="multiInstanceError[catalogSource.id]" class="label">
                <span class="label-text-alt text-error font-medium">{{ multiInstanceError[catalogSource.id] }}</span>
              </label>
            </div>

            <!-- List of user's instances -->
            <div class="space-y-2 mt-4">
              <div
                v-for="src in getMultiInstanceSources(catalogSource.id)"
                :key="src.id"
                class="flex items-center justify-between p-3 rounded-lg"
                :class="src.enabled ? 'bg-base-200' : 'bg-base-200/50 opacity-60'"
              >
                <div class="flex items-center gap-3">
                  <input type="checkbox" class="toggle toggle-sm toggle-success" v-model="src.enabled" @change="toggleSource(src)" />
                  <span class="font-medium">{{ src.name }}</span>
                  <label class="label cursor-pointer gap-2">
                    <span class="label-text text-xs opacity-60">Keywords</span>
                    <input type="checkbox" class="toggle toggle-xs toggle-primary" v-model="src.use_global_keywords" @change="updateSource(src)" />
                  </label>
                </div>
                <button class="btn btn-ghost btn-sm btn-square text-error" @click="deleteSource(src)">✕</button>
              </div>
              <p v-if="!getMultiInstanceSources(catalogSource.id).length" class="text-base-content/40 text-sm p-3">
                No {{ catalogSource.name }} sources configured
              </p>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { getIconConfig, isSvgIcon } = useSourceIcons()

const catalog = ref<any[]>([])
const sources = ref<any[]>([])
const isLoading = ref(true)

// Input state for multi-instance sources (keyed by catalog source id)
const multiInstanceInput = ref<Record<string, string>>({})
const multiInstanceError = ref<Record<string, string>>({})

// Computed helpers
function getSingletonSource(sourceId: string) {
  return sources.value.find(s => s.source_id === sourceId) || null
}

function getMultiInstanceSources(sourceId: string) {
  return sources.value.filter(s => s.source_id === sourceId)
}

// Limits (TODO: should come from user profile API)
const redditLimit = computed(() => 3)
const redditSourceCount = computed(() => 
  sources.value.filter((s: any) => s.source_id === 'reddit' && s.enabled).length
)
const isRedditLimitReached = computed(() => {
  return redditSourceCount.value >= redditLimit.value
})

async function fetchData() {
  isLoading.value = true
  try {
    const [catalogData, sourcesData] = await Promise.all([
      apiFetch<any[]>('/api/sources/catalog'),
      apiFetch<any[]>('/api/sources'),
    ])
    catalog.value = catalogData
    sources.value = sourcesData
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    isLoading.value = false
  }
}

async function addSingletonSource(catalogSource: any) {
  try {
    const newSource = await apiFetch<any>('/api/sources', {
      method: 'POST',
      body: {
        source_id: catalogSource.id,
        enabled: true,
        use_global_keywords: true,
      },
    })
    sources.value.push(newSource)
  } catch (error) {
    console.error('Failed to add source:', error)
  }
}

async function addMultiInstanceSource(catalogSource: any) {
  const inputKey = catalogSource.id
  const inputVal = (multiInstanceInput.value[inputKey] || '').trim()
  multiInstanceError.value[inputKey] = ''

  if (!inputVal) return

  // Get first config field key (e.g., 'subreddit')
  const fieldKey = Object.keys(catalogSource.config_schema)[0]

  // Reddit-specific validation
  if (catalogSource.id === 'reddit') {
    const redditRegex = /^[a-zA-Z0-9_]{3,21}$/
    if (!redditRegex.test(inputVal)) {
      multiInstanceError.value[inputKey] = 'Invalid subreddit name (3-21 chars, no spaces/special chars)'
      return
    }
    // Case-insensitive uniqueness check
    const isDuplicate = getMultiInstanceSources(catalogSource.id).some(
      (s: any) => s.params?.[fieldKey]?.toLowerCase() === inputVal.toLowerCase()
    )
    if (isDuplicate) {
      multiInstanceError.value[inputKey] = `r/${inputVal} is already in your list`
      return
    }
  }

  try {
    const newSource = await apiFetch<any>('/api/sources', {
      method: 'POST',
      body: {
        source_id: catalogSource.id,
        enabled: true,
        use_global_keywords: false,
        params: { [fieldKey]: inputVal },
      },
    })

    if (newSource.existed) {
      if (newSource.enabled) {
        multiInstanceError.value[inputKey] = `${inputVal} is already in your list`
        multiInstanceInput.value[inputKey] = ''
        return
      } else {
        // It existed but was disabled. The backend might have enabled it if possible.
        // Let's just refresh our local list.
        const idx = sources.value.findIndex(s => s.id === newSource.id)
        if (idx !== -1) sources.value[idx] = newSource
      }
    } else {
      sources.value.push(newSource)
    }
    multiInstanceInput.value[inputKey] = ''
  } catch (error: any) {
    console.error('Failed to add source:', error)
    const detail = error.data?.detail || 'Failed to add. Please try again.'
    multiInstanceError.value[inputKey] = detail
  }
}

async function toggleSource(src: any) {
  const originalState = !src.enabled
  try {
    const updated = await apiFetch<any>(`/api/sources/${src.id}`, {
      method: 'PUT',
      body: { enabled: src.enabled },
    })
    // If backend forced it to stay disabled (legacy check, though we handle it via 400 now)
    src.enabled = updated.enabled
  } catch (error: any) {
    console.error('Failed to toggle source:', error)
    // Revert local state on failure
    src.enabled = originalState
    
    // Show error if it was a reddit limit error
    if (src.source_id === 'reddit') {
      const detail = error.data?.detail || 'Limit reached. Disable another to enable this one.'
      multiInstanceError.value['reddit'] = detail
    }
  }
}

async function updateSource(src: any) {
  try {
    await apiFetch(`/api/sources/${src.id}`, {
      method: 'PUT',
      body: { use_global_keywords: src.use_global_keywords },
    })
  } catch (error) {
    console.error('Failed to update source:', error)
  }
}

async function deleteSource(src: any) {
  try {
    await apiFetch(`/api/sources/${src.id}`, { method: 'DELETE' })
    sources.value = sources.value.filter(s => s.id !== src.id)
  } catch (error) {
    console.error('Failed to delete source:', error)
  }
}

onMounted(() => fetchData())
</script>
