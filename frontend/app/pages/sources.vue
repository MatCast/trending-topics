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
      <!-- Reddit Section -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <h2 class="card-title gap-2">
              <svg class="w-6 h-6 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701z"/>
              </svg>
              Reddit
            </h2>
          </div>

          <!-- Add new subreddit -->
          <div class="form-control mt-4">
            <div class="join w-full">
              <span class="join-item btn btn-disabled">r/</span>
              <input
                v-model="newSubreddit"
                type="text"
                placeholder="Add subreddit..."
                class="input input-bordered join-item flex-1"
                :class="{ 'input-error': redditError }"
                @keyup.enter="addRedditSource"
                @input="redditError = ''"
              />
              <button class="btn btn-primary join-item" @click="addRedditSource">Add</button>
            </div>
            <label v-if="redditError" class="label">
              <span class="label-text-alt text-error font-medium">{{ redditError }}</span>
            </label>
          </div>

          <!-- Reddit sources list -->
          <div class="space-y-2 mt-4">
            <div
              v-for="src in redditSources"
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
            <p v-if="!redditSources.length" class="text-base-content/40 text-sm p-3">No Reddit sources configured</p>
          </div>
        </div>
      </div>

      <!-- Hacker News Section -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <h2 class="card-title gap-2">
              <span class="text-xl font-bold text-orange-400">Y</span>
              Hacker News
            </h2>
            <div v-if="hnSource">
              <input type="checkbox" class="toggle toggle-success" v-model="hnSource.enabled" @change="toggleSource(hnSource)" />
            </div>
            <button v-else class="btn btn-primary btn-sm" @click="addHNSource">Enable</button>
          </div>
          <p class="text-base-content/60 text-sm">Top stories filtered by your global keywords.</p>
        </div>
      </div>

      <!-- Bluesky Section -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <h2 class="card-title gap-2">
              🦋 Bluesky
            </h2>
            <div v-if="blueskySource">
              <input type="checkbox" class="toggle toggle-success" v-model="blueskySource.enabled" @change="toggleSource(blueskySource)" />
            </div>
            <button v-else class="btn btn-primary btn-sm" @click="addBlueskySource">Enable</button>
          </div>
          <p class="text-base-content/60 text-sm">Search posts using your global keywords.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()

const sources = ref<any[]>([])
const isLoading = ref(true)
const newSubreddit = ref('')

const redditSources = computed(() => sources.value.filter(s => s.type === 'reddit'))
const hnSource = computed(() => sources.value.find(s => s.type === 'hackernews') || null)
const blueskySource = computed(() => sources.value.find(s => s.type === 'bluesky') || null)

async function fetchSources() {
  isLoading.value = true
  try {
    sources.value = await apiFetch<any[]>('/api/sources')
  } catch (error) {
    console.error('Failed to fetch sources:', error)
  } finally {
    isLoading.value = false
  }
}

const redditError = ref('')

async function addRedditSource() {
  const sub = newSubreddit.value.trim()
  redditError.value = ''

  if (!sub) return

  // 1. Format validation (3-21 chars, alphanumeric/underscores)
  const redditRegex = /^[a-zA-Z0-9_]{3,21}$/
  if (!redditRegex.test(sub)) {
    redditError.value = 'Invalid subreddit name (3-21 chars, no spaces/special chars)'
    return
  }

  // 2. Case-insensitive uniqueness check
  const isDuplicate = redditSources.value.some(
    s => s.params?.subreddit?.toLowerCase() === sub.toLowerCase()
  )
  if (isDuplicate) {
    redditError.value = `r/${sub} is already in your list`
    return
  }

  try {
    const newSource = await apiFetch<any>('/api/sources', {
      method: 'POST',
      body: {
        type: 'reddit',
        name: `r/${sub}`,
        enabled: true,
        use_global_keywords: false,
        params: { subreddit: sub },
      },
    })

    // Check if the source already existed on the backend (safety check)
    if (newSource.existed) {
      redditError.value = `r/${sub} is already in your list`
      newSubreddit.value = ''
      return
    }

    sources.value.push(newSource)
    newSubreddit.value = ''
  } catch (error) {
    console.error('Failed to add source:', error)
    redditError.value = 'Failed to add subreddit. Please try again.'
  }
}

async function addHNSource() {
  try {
    const newSource = await apiFetch<any>('/api/sources', {
      method: 'POST',
      body: {
        type: 'hackernews',
        name: 'Hacker News',
        enabled: true,
        use_global_keywords: true,
        params: { url: 'https://hnrss.org/newest?points=10' },
      },
    })
    sources.value.push(newSource)
  } catch (error) {
    console.error('Failed to add HN source:', error)
  }
}

async function addBlueskySource() {
  try {
    const newSource = await apiFetch<any>('/api/sources', {
      method: 'POST',
      body: {
        type: 'bluesky',
        name: 'Bluesky',
        enabled: true,
        use_global_keywords: true,
        params: {},
      },
    })
    sources.value.push(newSource)
  } catch (error) {
    console.error('Failed to add Bluesky source:', error)
  }
}

async function toggleSource(src: any) {
  try {
    await apiFetch(`/api/sources/${src.id}`, {
      method: 'PUT',
      body: { enabled: src.enabled },
    })
  } catch (error) {
    console.error('Failed to toggle source:', error)
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

onMounted(() => fetchSources())
</script>
