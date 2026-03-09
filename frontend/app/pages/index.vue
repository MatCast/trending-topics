<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <p class="text-base-content/60 text-sm">Your trending topics from configured sources.</p>
      </div>

      <div class="flex gap-2">
        <button
          class="btn btn-primary gap-2"
          :class="{ 'btn-disabled': isExtracting }"
          @click="runExtraction"
        >
          <span v-if="isExtracting" class="loading loading-spinner loading-sm"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {{ isExtracting ? 'Searching...' : 'Run Extraction' }}
        </button>

        <button class="btn btn-outline btn-sm gap-2" @click="exportCSV" :disabled="!results.length">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>
    </div>

    <!-- Extraction result toast -->
    <div v-if="lastRunMessage" class="alert alert-info mb-4 shadow-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{{ lastRunMessage }}</span>
      <button class="btn btn-ghost btn-xs" @click="lastRunMessage = ''">✕</button>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        class="btn btn-sm"
        :class="activeFilter === null ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = null"
      >
        All
      </button>
      <button
        class="btn btn-sm gap-1"
        :class="activeFilter === 'reddit' ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = 'reddit'"
      >
        <svg class="w-4 h-4 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701z"/>
        </svg>
        Reddit
      </button>
      <button
        class="btn btn-sm gap-1"
        :class="activeFilter === 'hackernews' ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = 'hackernews'"
      >
        <span class="text-orange-400 font-bold text-sm">Y</span>
        Hacker News
      </button>
      <button
        class="btn btn-sm gap-1"
        :class="activeFilter === 'bluesky' ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = 'bluesky'"
      >
        🦋 Bluesky
      </button>

      <!-- Sort -->
      <div class="ml-auto">
        <select class="select select-bordered select-sm" v-model="sortBy">
          <option value="created_at">Newest</option>
          <option value="trend_score">Highest Score</option>
          <option value="ups">Most Upvotes</option>
          <option value="comments">Most Comments</option>
          <option value="title">Title</option>
          <option value="source">Source</option>
        </select>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="isLoadingResults" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Empty state -->
    <div v-else-if="!results.length" class="text-center py-16">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-base-300 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12A2 2 0 007 21h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-1">No results yet</h3>
      <p class="text-base-content/60 text-sm mb-4">Run an extraction to find trending topics.</p>
      <button class="btn btn-primary btn-sm" @click="runExtraction">Run Extraction</button>
    </div>

    <!-- Results Table -->
    <div v-else class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th class="w-12 cursor-pointer hover:text-primary select-none" @click="toggleSort('source')">
              Source
              <span v-if="sortBy === 'source'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="cursor-pointer hover:text-primary select-none" @click="toggleSort('title')">
              Title
              <span v-if="sortBy === 'title'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="w-20 text-right cursor-pointer hover:text-primary select-none" @click="toggleSort('trend_score')">
              Score
              <span v-if="sortBy === 'trend_score'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="w-16 text-right cursor-pointer hover:text-primary select-none" @click="toggleSort('ups')">
              👍
              <span v-if="sortBy === 'ups'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="w-16 text-right cursor-pointer hover:text-primary select-none" @click="toggleSort('comments')">
              💬
              <span v-if="sortBy === 'comments'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="w-32 cursor-pointer hover:text-primary select-none" @click="toggleSort('created_at')">
              Date
              <span v-if="sortBy === 'created_at'" class="ml-1">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="result in filteredResults"
            :key="result.id"
            class="hover"
          >
            <td>
              <div class="tooltip" :data-tip="result.source">
                <!-- Reddit icon -->
                <svg v-if="result.source_type === 'reddit'" class="w-5 h-5 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701z"/>
                </svg>
                <!-- HN icon -->
                <span v-else-if="result.source_type === 'hackernews'" class="text-lg font-bold text-orange-400">Y</span>
                <!-- Bluesky icon -->
                <span v-else-if="result.source_type === 'bluesky'" class="text-lg">🦋</span>
                <!-- Unknown -->
                <span v-else class="text-lg">📰</span>
              </div>
            </td>
            <td>
              <div>
                <a
                  :href="result.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="link link-hover font-medium text-sm"
                >
                  {{ result.title }}
                </a>
                <p class="text-xs text-base-content/50 mt-1 line-clamp-1">
                  {{ result.source }} · {{ result.description?.slice(0, 120) }}
                </p>
              </div>
            </td>
            <td class="text-right">
              <span class="badge badge-ghost font-mono">{{ Math.round(result.trend_score) }}</span>
            </td>
            <td class="text-right text-sm">{{ result.ups }}</td>
            <td class="text-right text-sm">{{ result.comments }}</td>
            <td class="text-xs text-base-content/60">{{ formatDate(result.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalResults > pageSize" class="flex justify-center mt-6">
      <div class="join">
        <button class="join-item btn btn-sm" :disabled="page <= 1" @click="page--">«</button>
        <button class="join-item btn btn-sm">Page {{ page }}</button>
        <button class="join-item btn btn-sm" :disabled="page * pageSize >= totalResults" @click="page++">»</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()

const results = ref<any[]>([])
const totalResults = ref(0)
const page = ref(1)
const pageSize = ref(50)
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')
const activeFilter = ref<string | null>(null)
const isLoadingResults = ref(true)
const isExtracting = ref(false)
const lastRunMessage = ref('')

// Filtered results (client-side for source type since we also do server-side)
const filteredResults = computed(() => {
  if (!activeFilter.value) return results.value
  return results.value.filter(r => r.source_type === activeFilter.value)
})

// Fetch results
async function fetchResults() {
  isLoadingResults.value = true
  try {
    const params = new URLSearchParams({
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: String(page.value),
      page_size: String(pageSize.value),
    })
    if (activeFilter.value) {
      params.set('source_type', activeFilter.value)
    }

    const data = await apiFetch<any>(`/api/results?${params}`)
    results.value = data.results || []
    totalResults.value = data.total || 0
  } catch (error) {
    console.error('Failed to fetch results:', error)
  } finally {
    isLoadingResults.value = false
  }
}

// Toggle sorting
function toggleSort(field: string) {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = 'desc'
  }
}

// Run extraction
async function runExtraction() {
  isExtracting.value = true
  lastRunMessage.value = ''
  try {
    const data = await apiFetch<any>('/api/extract', { method: 'POST', body: {} })
    lastRunMessage.value = `Found ${data.results_count} trending topics!`
    await fetchResults()
  } catch (error: any) {
    lastRunMessage.value = `Extraction failed: ${error.data?.detail || error.message}`
  } finally {
    isExtracting.value = false
  }
}

// Export CSV
async function exportCSV() {
  try {
    const { getIdToken } = useAuth()
    const token = await getIdToken()
    const config = useRuntimeConfig()
    const url = `${config.public.apiBaseUrl}/api/results/export/csv`

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'trends_export.csv'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('CSV export failed:', error)
  }
}

// Format date
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Watch for filter/sort/page changes
watch([sortBy, sortOrder, activeFilter, page], () => fetchResults())

// Initial load
onMounted(() => fetchResults())
</script>
