<template>
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold mb-2">Welcome! Let's set up your sources 🚀</h1>
      <p class="text-base-content/60">Configure where you want to find trending topics.</p>
    </div>

    <!-- Loading catalog -->
    <div v-if="isLoadingCatalog" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <template v-else>
      <!-- Progress Steps -->
      <ul class="steps steps-horizontal w-full mb-8">
        <li class="step" :class="{ 'step-primary': currentStep >= 1 }">Keywords</li>
        <li class="step" :class="{ 'step-primary': currentStep >= 2 }" v-if="multiInstanceSources.length">
          {{ multiInstanceSources.map(s => s.name).join(' & ') }}
        </li>
        <li class="step" :class="{ 'step-primary': currentStep >= 3 }" v-if="singletonSources.length">Other Sources</li>
        <li class="step" :class="{ 'step-primary': currentStep >= 4 }">Preferences</li>
      </ul>

      <!-- Step 1: Global Keywords -->
      <div v-if="currentStep === 1" class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Global Keywords</h2>
          <p class="text-base-content/60 text-sm mb-4">
            These keywords will be used to filter content from sources that support keyword search.
          </p>

          <div class="form-control">
            <label class="label"><span class="label-text">Add keywords</span></label>
            <div class="join w-full">
              <input
                v-model="newKeyword"
                type="text"
                placeholder="e.g., AI, Startup, GPT"
                class="input input-bordered join-item flex-1"
                @keyup.enter="addKeyword"
              />
              <button class="btn btn-primary join-item" @click="addKeyword">Add</button>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 mt-4">
            <div
              v-for="(kw, idx) in globalKeywords"
              :key="idx"
              class="badge badge-lg badge-primary gap-2"
            >
              {{ kw }}
              <button class="btn btn-ghost btn-xs" @click="globalKeywords.splice(idx, 1)">✕</button>
            </div>
            <span v-if="!globalKeywords.length" class="text-base-content/40 text-sm">No keywords added yet</span>
          </div>

          <div class="card-actions justify-end mt-6">
            <button class="btn btn-primary" @click="currentStep = multiInstanceSources.length ? 2 : (singletonSources.length ? 3 : 4)">
              Next →
            </button>
          </div>
        </div>
      </div>

      <!-- Step 2: Multi-instance sources (e.g., Reddit) -->
      <div v-if="currentStep === 2" class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <div v-for="catalogSource in multiInstanceSources" :key="catalogSource.id">
            <h2 class="card-title flex items-center gap-2">
              <svg v-if="isSvgIcon(catalogSource.icon)" class="w-6 h-6" :class="getIconConfig(catalogSource.icon).svgClass" viewBox="0 0 24 24" fill="currentColor">
                <path :d="getIconConfig(catalogSource.icon).svgPath" />
              </svg>
              <span v-else :class="getIconConfig(catalogSource.icon).textClass">{{ getIconConfig(catalogSource.icon).text }}</span>
              {{ catalogSource.name }}
            </h2>
            <p class="text-base-content/60 text-sm mb-4">{{ catalogSource.description }}</p>

            <!-- Dynamic config form -->
            <div class="form-control" v-for="(fieldSchema, fieldKey) in catalogSource.config_schema" :key="fieldKey">
              <label class="label"><span class="label-text">Add {{ fieldSchema.label }}</span></label>
              <div class="join w-full">
                <span v-if="catalogSource.id === 'reddit'" class="join-item btn btn-disabled">r/</span>
                <input
                  v-model="multiInstanceDrafts[catalogSource.id]"
                  type="text"
                  :placeholder="fieldSchema.placeholder || `e.g., ${fieldSchema.label}`"
                  class="input input-bordered join-item flex-1"
                  :class="{ 'input-error': multiDraftError[catalogSource.id] }"
                  @keyup.enter="addDraftInstance(catalogSource)"
                  @input="multiDraftError[catalogSource.id] = ''"
                />
                <button class="btn btn-primary join-item" @click="addDraftInstance(catalogSource)">Add</button>
              </div>
              <label v-if="multiDraftError[catalogSource.id]" class="label">
                <span class="label-text-alt text-error font-medium">{{ multiDraftError[catalogSource.id] }}</span>
              </label>
            </div>

            <!-- Pending instances list -->
            <div class="space-y-2 mt-4">
              <div
                v-for="(src, idx) in pendingMultiInstances[catalogSource.id] || []"
                :key="idx"
                class="flex items-center justify-between p-3 bg-base-200 rounded-lg"
              >
                <div class="flex items-center gap-3">
                  <span class="font-medium">{{ src.name }}</span>
                  <label class="label cursor-pointer gap-2">
                    <span class="label-text text-xs opacity-60">Keywords</span>
                    <input type="checkbox" class="toggle toggle-sm toggle-primary" v-model="src.use_global_keywords" />
                  </label>
                </div>
                <button class="btn btn-ghost btn-sm btn-square" @click="(pendingMultiInstances[catalogSource.id] || []).splice(idx, 1)">✕</button>
              </div>
              <p v-if="!(pendingMultiInstances[catalogSource.id] || []).length" class="text-base-content/40 text-sm p-3">
                None added yet
              </p>
            </div>
          </div>

          <div class="card-actions justify-between mt-6">
            <button class="btn btn-ghost" @click="currentStep = 1">← Back</button>
            <button class="btn btn-primary" @click="currentStep = singletonSources.length ? 3 : 4">Next →</button>
          </div>
        </div>
      </div>

      <!-- Step 3: Singleton sources (HN, Bluesky, Indie Hackers, etc.) -->
      <div v-if="currentStep === 3" class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Other Sources</h2>
          <p class="text-base-content/60 text-sm mb-4">
            Enable additional trend sources. These use your global keywords for searching.
          </p>

          <div
            v-for="catalogSource in singletonSources"
            :key="catalogSource.id"
            class="p-4 bg-base-200 rounded-xl mb-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-3">
                <svg v-if="isSvgIcon(catalogSource.icon)" class="w-6 h-6" :class="getIconConfig(catalogSource.icon).svgClass" viewBox="0 0 24 24" fill="currentColor">
                  <path :d="getIconConfig(catalogSource.icon).svgPath" />
                </svg>
                <span v-else :class="getIconConfig(catalogSource.icon).textClass">{{ getIconConfig(catalogSource.icon).text }}</span>
                <div>
                  <h3 class="font-semibold">{{ catalogSource.name }}</h3>
                  <p class="text-xs text-base-content/60">{{ catalogSource.description }}</p>
                </div>
              </div>
              <input type="checkbox" class="toggle toggle-primary" v-model="singletonToggles[catalogSource.id]" />
            </div>
          </div>

          <div class="card-actions justify-between mt-6">
            <button class="btn btn-ghost" @click="currentStep = multiInstanceSources.length ? 2 : 1">← Back</button>
            <button class="btn btn-primary" @click="currentStep = 4">Next: Preferences →</button>
          </div>
        </div>
      </div>

      <!-- Step 4: Preferences -->
      <div v-if="currentStep === 4" class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Preferences</h2>
          <p class="text-base-content/60 text-sm mb-4">Fine-tune your extraction settings.</p>

          <div class="grid gap-4">
            <div class="form-control">
              <label class="label"><span class="label-text">Time window (hours)</span></label>
              <input v-model.number="timeWindowHours" type="number" min="1" max="168" class="input input-bordered" />
              <label class="label"><span class="label-text-alt">How far back to look for trending content</span></label>
            </div>

            <div class="form-control">
              <label class="label"><span class="label-text">Max results per source</span></label>
              <input v-model.number="maxTrendsPerSource" type="number" min="1" max="50" class="input input-bordered" />
              <label class="label"><span class="label-text-alt">Maximum number of trending topics to keep per source</span></label>
            </div>
          </div>

          <div class="card-actions justify-between mt-6">
            <button class="btn btn-ghost" @click="currentStep = singletonSources.length ? 3 : (multiInstanceSources.length ? 2 : 1)">← Back</button>
            <button
              class="btn btn-primary"
              :class="{ 'btn-disabled loading': isSaving }"
              @click="saveAndContinue"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
              {{ isSaving ? 'Saving...' : 'Complete Setup ✓' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { getIconConfig, isSvgIcon } = useSourceIcons()

const currentStep = ref(1)
const isSaving = ref(false)
const isLoadingCatalog = ref(true)

// Catalog data
const catalog = ref<any[]>([])
const multiInstanceSources = computed(() => catalog.value.filter(s => s.is_multi_instance))
const singletonSources = computed(() => catalog.value.filter(s => !s.is_multi_instance))

// Step 1: Keywords
const globalKeywords = ref<string[]>([])
const newKeyword = ref('')

function addKeyword() {
  // Split by commas, trim each, filter empty and duplicates
  const parts = newKeyword.value.split(',').map(s => s.trim()).filter(Boolean)
  for (const kw of parts) {
    if (!globalKeywords.value.some(existing => existing.toLowerCase() === kw.toLowerCase())) {
      globalKeywords.value.push(kw)
    }
  }
  newKeyword.value = ''
}

// Step 2: Multi-instance source drafts (e.g., subreddits to be saved)
const multiInstanceDrafts = ref<Record<string, string>>({})
const multiDraftError = ref<Record<string, string>>({})
const pendingMultiInstances = ref<Record<string, any[]>>({})

function addDraftInstance(catalogSource: any) {
  const inputVal = (multiInstanceDrafts.value[catalogSource.id] || '').trim()
  multiDraftError.value[catalogSource.id] = ''
  if (!inputVal) return

  const fieldKey = Object.keys(catalogSource.config_schema)[0]

  // Reddit-specific validation
  if (catalogSource.id === 'reddit') {
    const redditRegex = /^[a-zA-Z0-9_]{3,21}$/
    if (!redditRegex.test(inputVal)) {
      multiDraftError.value[catalogSource.id] = 'Invalid subreddit name (3-21 chars, no spaces/special chars)'
      return
    }
    const existing = pendingMultiInstances.value[catalogSource.id] || []
    if (existing.some(s => s.params[fieldKey]?.toLowerCase() === inputVal.toLowerCase())) {
      multiDraftError.value[catalogSource.id] = `r/${inputVal} is already in your list`
      return
    }
  }

  if (!pendingMultiInstances.value[catalogSource.id]) {
    pendingMultiInstances.value[catalogSource.id] = []
  }

  const displayName = catalogSource.id === 'reddit' ? `r/${inputVal}` : inputVal
  pendingMultiInstances.value[catalogSource.id].push({
    source_id: catalogSource.id,
    name: displayName,
    enabled: true,
    use_global_keywords: false,
    params: { [fieldKey]: inputVal },
  })
  multiInstanceDrafts.value[catalogSource.id] = ''
}

// Step 3: Singleton toggles
const singletonToggles = ref<Record<string, boolean>>({})

// Step 4: Preferences
const timeWindowHours = ref(3)
const maxTrendsPerSource = ref(3)

// Check if user already completed onboarding
async function checkOnboardingStatus() {
  try {
    const existingSources = await apiFetch<any[]>('/api/sources')
    if (existingSources && existingSources.length > 0) {
      navigateTo('/')
      return
    }
  } catch (error) {
    console.error('Failed to check onboarding status:', error)
  }
}

// Fetch catalog on mount
async function fetchCatalog() {
  isLoadingCatalog.value = true
  try {
    catalog.value = await apiFetch<any[]>('/api/sources/catalog')
    // Initialize singleton toggles with defaults
    for (const source of singletonSources.value) {
      // Default: enable hackernews and indiehackers, disable bluesky
      singletonToggles.value[source.id] = source.id !== 'bluesky'
    }
  } catch (error) {
    console.error('Failed to fetch catalog:', error)
  } finally {
    isLoadingCatalog.value = false
  }
}

async function saveAndContinue() {
  isSaving.value = true
  try {
    // Save user settings (without keywords — they're separate now)
    await apiFetch('/api/settings', {
      method: 'PUT',
      body: {
        time_window_hours: timeWindowHours.value,
        max_trends_per_source: maxTrendsPerSource.value,
      },
    })

    // Save keywords via keywords API
    if (globalKeywords.value.length > 0) {
      await apiFetch('/api/keywords', {
        method: 'POST',
        body: { keywords: globalKeywords.value },
      })
    }

    // Save multi-instance sources
    for (const [_sourceId, instances] of Object.entries(pendingMultiInstances.value)) {
      for (const src of instances) {
        await apiFetch('/api/sources', { method: 'POST', body: src })
      }
    }

    // Save singleton sources (only enabled ones)
    for (const catalogSource of singletonSources.value) {
      if (singletonToggles.value[catalogSource.id]) {
        await apiFetch('/api/sources', {
          method: 'POST',
          body: {
            source_id: catalogSource.id,
            enabled: true,
            use_global_keywords: true,
          },
        })
      }
    }

    navigateTo('/')
  } catch (error) {
    console.error('Failed to save onboarding config:', error)
  } finally {
    isSaving.value = false
  }
}

onMounted(async () => {
  await checkOnboardingStatus()
  await fetchCatalog()
})
</script>
