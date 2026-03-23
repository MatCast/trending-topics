<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm text-base-content/60 mb-2">
            <NuxtLink to="/" class="hover:text-primary transition-colors flex items-center gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Dashboard
            </NuxtLink>
            <span>/</span>
            <span>Extraction Details</span>
        </div>
        <h1 class="text-2xl font-bold flex items-center gap-2">
            Extraction Results
            <span v-if="!isLoadingResults && results.length" class="badge badge-primary">{{ totalResults }}</span>
        </h1>
        <p class="text-base-content/60 text-sm">Results for the extraction run on {{ formattedDate }}</p>
      </div>

      <div class="flex gap-2">
        <button class="btn btn-outline btn-sm gap-2" @click="exportCSV" :disabled="!results.length">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>
    </div>

    <!-- Insights & Warnings Component -->
    <ExtractionInsights :insights="extraction?.insights" />

    <!-- Dynamic Filters from catalog -->
    <div class="flex flex-wrap gap-2 mb-4">
      <button
        class="btn btn-sm"
        :class="activeFilter === null ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = null"
      >
        All
      </button>
      <button
        v-for="catalogSource in catalog"
        :key="catalogSource.id"
        class="btn btn-sm gap-1"
        :class="activeFilter === catalogSource.id ? 'btn-primary' : 'btn-ghost'"
        @click="activeFilter = catalogSource.id"
      >
        <svg v-if="isSvgIcon(catalogSource.icon)" class="w-4 h-4" :class="getIconConfig(catalogSource.icon).svgClass" viewBox="0 0 24 24" fill="currentColor">
          <path :d="getIconConfig(catalogSource.icon).svgPath" />
        </svg>
        <span v-else :class="getIconConfig(catalogSource.icon).textClass" class="text-sm">
          {{ getIconConfig(catalogSource.icon).text }}
        </span>
        {{ catalogSource.name }}
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
    <div v-else-if="!results.length" class="text-center py-16 bg-base-200 rounded-box">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-base-300 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12A2 2 0 007 21h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-1">No results found</h3>
      <p class="text-base-content/60 text-sm mb-4">This extraction didn't return any trending topics.</p>
      <NuxtLink to="/" class="btn btn-primary btn-sm">Return to Dashboard</NuxtLink>
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
                <!-- Dynamic source icon -->
                <svg v-if="isSvgIcon(result.source_type)" class="w-5 h-5" :class="getIconConfig(result.source_type).svgClass" viewBox="0 0 24 24" fill="currentColor">
                  <path :d="getIconConfig(result.source_type).svgPath" />
                </svg>
                <span v-else :class="getIconConfig(result.source_type).textClass">
                  {{ getIconConfig(result.source_type).text }}
                </span>
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
import type { Extraction, PaginatedResults, ExtractionResult } from '~/types/extraction'

const route = useRoute()
const { apiFetch } = useApi()
const { getIconConfig, isSvgIcon } = useSourceIcons()

const extractionId = route.params.id as string

const extraction = ref<Extraction | null>(null)
// Catalog data for dynamic filter buttons
const catalog = ref<any[]>([])

const results = ref<ExtractionResult[]>([])
const totalResults = ref(0)
const page = ref(1)
const pageSize = ref(50)
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')
const activeFilter = ref<string | null>(null)
const isLoadingResults = ref(true)

const extractionDate = computed(() => {
    if (extraction.value?.created_at) {
        return extraction.value.created_at
    }
    return null
})

const formattedDate = computed(() => {
    return formatDate(extractionDate.value)
})

// Filtered results (client-side for source type since we also do server-side)
const filteredResults = computed(() => {
  if (!activeFilter.value) return results.value
  return results.value.filter(r => r.source_type === activeFilter.value)
})

// Fetch catalog, extraction details, and results
async function fetchCatalog() {
  try {
    catalog.value = await apiFetch<any[]>('/api/sources/catalog')
  } catch (error) {
    console.error('Failed to fetch catalog:', error)
  }
}

async function fetchExtraction() {
  try {
    extraction.value = await apiFetch<Extraction>(`/api/extractions/${extractionId}`)
  } catch (error) {
    console.error('Failed to fetch extraction details:', error)
  }
}

async function fetchResults() {
  isLoadingResults.value = true
  try {
    const params = new URLSearchParams({
      extraction_id: extractionId,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: String(page.value),
      page_size: String(pageSize.value),
    })
    
    if (activeFilter.value) {
      params.set('source_type', activeFilter.value)
    }

    const data = await apiFetch<PaginatedResults>(`/api/results?${params}`)
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

// Export CSV
async function exportCSV() {
  try {
    const { getIdToken } = useAuth()
    const token = await getIdToken()
    const config = useRuntimeConfig()
    
    // We pass extraction_id so it only exports this specific run
    const params = new URLSearchParams({ extraction_id: extractionId })
    const url = `${config.public.apiBaseUrl}/api/results/export/csv?${params}`

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await res.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `extraction_${extractionId}_export.csv`
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('CSV export failed:', error)
  }
}

// Format date
function formatDate(dateStr: string | null) {
  if (!dateStr) return 'Unknown'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Watch for filter/sort/page changes
watch([sortBy, sortOrder, activeFilter, page], () => fetchResults())

// Initial load
onMounted(async () => {
  await Promise.all([fetchCatalog(), fetchResults(), fetchExtraction()])
})
</script>
