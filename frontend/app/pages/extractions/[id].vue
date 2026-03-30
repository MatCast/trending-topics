<template>
  <div class="space-y-8 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-8 border-b-4 border-black">
      <div class="space-y-4">
        <div class="flex items-center gap-3">
            <NuxtLink to="/" class="group flex items-center gap-2 border-2 border-black bg-white px-3 py-1.5 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
                <ArrowLeft class="size-4 text-black" />
                <span class="text-[10px] font-black uppercase tracking-widest text-black">Dashboard</span>
            </NuxtLink>
            <ChevronRight class="size-4 text-black/20" />
            <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Extraction Analysis</span>
        </div>
        <div class="space-y-1">
          <h1 class="text-4xl font-black uppercase tracking-tight flex items-center gap-4">
              Results
              <Badge v-if="!isLoadingResults && results.length" class="border-2 border-black bg-primary text-black font-black text-xl px-4 py-1 rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                {{ totalResults }}
              </Badge>
          </h1>
          <p class="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">
            Processed on <span class="text-black">{{ formattedDate }}</span>
          </p>
        </div>
      </div>

      <div class="flex gap-4 w-full sm:w-auto">
        <Button 
          variant="neutral" 
          class="flex-1 sm:flex-none border-2 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-xs h-12 hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer" 
          @click="exportCSV" 
          :disabled="!results.length"
        >
          <Download class="size-4 mr-2" />
          Export CSV
        </Button>
      </div>
    </div>

    <!-- Insights & Warnings Component -->
    <ExtractionInsights :insights="extraction?.insights" />

    <!-- Filters Section -->
    <div class="space-y-6">
      <div class="flex items-center gap-3">
        <span class="text-[10px] font-black uppercase tracking-[0.2em] text-black">Source Filters</span>
        <div class="h-0.5 bg-black grow"></div>
      </div>

      <div class="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
        <div class="flex flex-wrap gap-3">
          <Button
            variant="neutral"
            class="border-2 border-black rounded-none uppercase font-black text-[10px] h-10 px-6 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] cursor-pointer"
            :class="activeFilter === null ? 'bg-primary text-black translate-x-0.5 translate-y-0.5 shadow-none' : 'bg-white hover:bg-muted'"
            @click="activeFilter = null"
          >
            All Sources
          </Button>
          <Button
            v-for="catalogSource in catalog"
            :key="catalogSource.id"
            variant="neutral"
            class="border-2 border-black rounded-none uppercase font-black text-[10px] h-10 px-6 transition-all shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] flex items-center gap-2 cursor-pointer"
            :class="activeFilter === catalogSource.id ? 'bg-primary text-black translate-x-0.5 translate-y-0.5 shadow-none' : 'bg-white hover:bg-muted'"
            @click="activeFilter = catalogSource.id"
          >
            <div class="size-4 flex items-center justify-center">
              <svg v-if="isSvgIcon(catalogSource.icon)" class="size-3.5 fill-current" viewBox="0 0 24 24">
                <path :d="getIconConfig(catalogSource.icon).svgPath" />
              </svg>
              <span v-else class="text-[10px]">{{ getIconConfig(catalogSource.icon).text }}</span>
            </div>
            {{ catalogSource.name }}
          </Button>
        </div>

        <!-- Sort Select -->
        <div class="w-full md:w-auto relative">
          <select 
            class="w-full md:w-64 h-10 border-2 border-black bg-white px-4 font-black uppercase text-[10px] appearance-none focus:outline-none focus:ring-0 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" 
            v-model="sortBy"
          >
            <option value="created_at">Sort by Newest</option>
            <option value="trend_score">Sort by Score</option>
            <option value="ups">Sort by Upvotes</option>
            <option value="comments">Sort by Comments</option>
            <option value="title">Sort by Title</option>
            <option value="source">Sort by Source</option>
          </select>
          <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
            <ChevronDown class="size-4 text-black" />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content State -->
    <div class="space-y-8">
      <!-- Loading state -->
      <div v-if="isLoadingResults" class="flex flex-col items-center justify-center py-24 gap-4">
        <div class="size-16 flex items-center justify-center border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-bounce">
          <Loader2 class="size-8 text-black animate-spin" />
        </div>
        <p class="text-[10px] font-black uppercase tracking-widest">Aggregating Results...</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="!results.length" class="text-center py-24 border-4 border-black border-dashed bg-muted/20 flex flex-col items-center gap-6">
        <div class="size-20 flex items-center justify-center border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
          <SearchX class="size-10 text-black/20" />
        </div>
        <div>
          <h3 class="text-2xl font-black uppercase tracking-tight">Zero Matches Found</h3>
          <p class="text-xs font-bold text-muted-foreground mt-2 uppercase tracking-tight">Adjust your extraction parameters and try again</p>
        </div>
        <NuxtLink to="/">
          <Button class="border-2 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-xs px-8 h-12 hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all">
            Return to Dashboard
          </Button>
        </NuxtLink>
      </div>

      <!-- Results Table -->
      <div v-else class="border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-white overflow-hidden">
        <div class="overflow-x-auto">
          <Table>
            <TableHeader class="bg-black">
              <TableRow class="hover:bg-transparent border-black">
                <TableHead class="w-24 text-white font-black uppercase text-[10px] h-12 cursor-pointer hover:bg-white/10 transition-colors" @click="toggleSort('source')">
                  Source
                </TableHead>
                <TableHead class="text-white font-black uppercase text-[10px] h-12 cursor-pointer hover:bg-white/10 transition-colors" @click="toggleSort('title')">
                  Insights & Trends
                </TableHead>
                <TableHead class="w-24 text-right text-white font-black uppercase text-[10px] h-12 cursor-pointer hover:bg-white/10 transition-colors" @click="toggleSort('trend_score')">
                  Impact
                </TableHead>
                <TableHead class="w-24 text-right text-white font-black uppercase text-[10px] h-12 cursor-pointer hover:bg-white/10 transition-colors" @click="toggleSort('ups')">
                  Engmnt
                </TableHead>
                <TableHead class="w-32 text-right text-white font-black uppercase text-[10px] h-12 cursor-pointer hover:bg-white/10 transition-colors" @click="toggleSort('created_at')">
                  Timestamp
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow
                v-for="result in filteredResults"
                :key="result.id"
                class="border-black hover:bg-muted/30 group"
              >
                 <TableCell>
                  <div class="size-10 flex items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] group-hover:bg-primary transition-colors">
                    <svg v-if="isSvgIcon(result.source_type)" class="size-5 fill-current" viewBox="0 0 24 24">
                      <path :d="getIconConfig(result.source_type).svgPath" />
                    </svg>
                    <span v-else class="text-xs font-black">{{ getIconConfig(result.source_type).text }}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div class="space-y-1">
                    <a
                      :href="result.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-black text-sm uppercase leading-tight hover:text-primary transition-colors decoration-2 underline-offset-4"
                    >
                      {{ result.title }}
                    </a>
                    <div class="flex items-center gap-3">
                      <span class="text-[10px] font-black uppercase text-muted-foreground">{{ result.source }}</span>
                      <div class="size-1 bg-black/10"></div>
                      <p class="text-[10px] font-bold text-muted-foreground uppercase line-clamp-1">
                        {{ result.description?.slice(0, 100) }}
                      </p>
                    </div>
                  </div>
                </TableCell>
                <TableCell class="text-right">
                  <Badge class="border-2 border-black bg-white text-black font-black uppercase text-[10px] rounded-none px-3 py-1 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                    {{ Math.round(result.trend_score) }} pts
                  </Badge>
                </TableCell>
                <TableCell class="text-right">
                  <div class="flex flex-col items-end gap-0.5">
                    <span class="text-[10px] font-black uppercase flex items-center gap-1">
                      <ThumbsUp class="size-3" /> {{ result.ups }}
                    </span>
                    <span class="text-[10px] font-black uppercase text-muted-foreground flex items-center gap-1">
                      <MessageSquare class="size-3" /> {{ result.comments }}
                    </span>
                  </div>
                </TableCell>
                <TableCell class="text-right">
                  <span class="text-[10px] font-black uppercase text-muted-foreground">
                    {{ formatDate(result.created_at) }}
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalResults > pageSize" class="flex justify-center pt-8">
      <div class="flex gap-2">
        <Button 
          variant="neutral" 
          class="size-10 border-2 border-black rounded-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] font-black text-lg p-0 hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer" 
          :disabled="page <= 1" 
          @click="page--"
        >
          <ChevronLeft class="size-5" />
        </Button>
        <div class="h-10 px-6 flex items-center border-2 border-black bg-primary font-black uppercase text-xs">
          Page {{ page }}
        </div>
        <Button 
          variant="neutral" 
          class="size-10 border-2 border-black rounded-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] font-black text-lg p-0 hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer" 
          :disabled="page * pageSize >= totalResults" 
          @click="page++"
        >
          <ChevronRight class="size-5" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, ChevronRight, Download, ChevronDown, Loader2, SearchX, ThumbsUp, MessageSquare, ChevronLeft } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table'
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
