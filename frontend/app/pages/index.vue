<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold">Extraction History</h1>
        <p class="text-base-content/60 text-sm">Review your past extractions and trending topics.</p>
      </div>

      <div class="flex gap-2">
        <button class="btn btn-primary gap-2" :class="{ 'btn-disabled': isExtracting }" @click="runExtraction">
          <span v-if="isExtracting" class="loading loading-spinner loading-sm"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {{ isExtracting ? 'Searching...' : 'New Extraction' }}
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

    <!-- Loading state -->
    <div v-if="isLoadingResults" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <!-- Empty state -->
    <div v-else-if="!extractions.length" class="text-center py-16">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-base-300 mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12A2 2 0 007 21h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-1">No extractions yet</h3>
      <p class="text-base-content/60 text-sm mb-4">Run an extraction to find trending topics.</p>
      <button class="btn btn-primary btn-sm" @click="runExtraction">Run Extraction</button>
    </div>

    <!-- Extractions Table / Mobile Cards -->
    <div v-else class="pb-8">
      
      <!-- Desktop Table -->
      <div class="hidden md:block overflow-x-auto">
        <table class="table w-full border-separate border-spacing-y-4">
          <thead>
            <tr class="text-base-content/40 border-none uppercase text-xs tracking-widest">
              <th class="bg-transparent pl-8">Run Date</th>
              <th class="bg-transparent">Target Platforms</th>
              <th class="bg-transparent text-right">Topics Found</th>
              <th class="bg-transparent text-right pr-8">Expires</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="extraction in extractions" :key="`desktop-${extraction.id}`"
              class="group bg-base-100 hover:bg-base-100/90 transition-all duration-300 shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.25)] hover:-translate-y-2 rounded-2xl border border-base-300 hover:border-primary/30 active:scale-[0.97]"
              :class="extraction.status === 'pending' ? 'cursor-wait opacity-80' : 'cursor-pointer'"
              @click="extraction.status !== 'pending' && navigateTo(`/extractions/${extraction.id}`)">
              <td class="whitespace-nowrap font-medium py-8 pl-10 rounded-l-2xl border-l border-t border-b border-transparent group-hover:border-base-300/50">
                <div class="flex flex-col gap-1">
                  <div class="flex items-center gap-2">
                    <span class="text-lg font-bold text-base-content tracking-tight group-hover:text-primary transition-colors">{{
                      formatDate(extraction.created_at).split(',')[0] }}</span>
                    <span v-if="extraction.status === 'pending'" class="loading loading-spinner loading-xs text-primary"></span>
                  </div>
                  <span class="text-xs font-semibold text-base-content/40 tracking-wider uppercase">{{ formatDate(extraction.created_at).split(',')[1] }}</span>
                </div>
              </td>
              <td class="py-8 border-t border-b border-transparent group-hover:border-base-300/50">
                <div class="flex items-center gap-4">
                  <div v-for="type in getUniqueSources(extraction.sources)" :key="type" class="tooltip tooltip-bottom font-bold" :data-tip="type.toUpperCase()">
                    <svg v-if="isSvgIcon(type)" class="w-7 h-7 transition-all duration-500 group-hover:scale-125" :class="getIconConfig(type).svgClass"
                      viewBox="0 0 24 24" fill="currentColor">
                      <path :d="getIconConfig(type).svgPath" />
                    </svg>
                    <span v-else :class="getIconConfig(type).textClass" class="text-2xl transition-all duration-500 group-hover:scale-125">
                      {{ getIconConfig(type).text }}
                    </span>
                  </div>
                  <span v-if="!getUniqueSources(extraction.sources).length" class="text-base-content/20 italic text-sm">No sources tracked</span>
                </div>
              </td>
              <td class="text-right py-8 border-t border-b border-transparent group-hover:border-base-300/50">
                <div class="inline-flex flex-col items-end gap-1">
                  <span class="text-2xl font-black text-primary/80 group-hover:text-primary transition-colors font-mono">{{ extraction.results_count }}</span>
                  <span class="text-[10px] uppercase tracking-tighter text-base-content/40 font-bold">Total Trends</span>
                </div>
              </td>
              <td class="text-right py-8 pr-10 rounded-r-2xl border-r border-t border-b border-transparent group-hover:border-base-300/50">
                <div class="flex flex-col items-end gap-0.5">
                  <span class="text-sm font-semibold text-base-content/60">{{ formatDate(extraction.expires_at).split(',')[0] }}</span>
                  <span class="text-[10px] uppercase font-bold text-error/40 group-hover:text-error/60 transition-colors">{{
                    formatDate(extraction.expires_at).split(',')[1] }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards -->
      <div class="md:hidden flex flex-col gap-4 mt-2">
        <div v-for="extraction in extractions" :key="`mobile-${extraction.id}`"
          class="bg-base-100 rounded-xl shadow-md border border-base-300 p-4 relative"
          :class="extraction.status === 'pending' ? 'opacity-80' : 'active:scale-[0.98] cursor-pointer'"
          @click="extraction.status !== 'pending' && navigateTo(`/extractions/${extraction.id}`)">
          
          <div class="flex justify-between items-start mb-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-base font-bold text-base-content">{{ formatDate(extraction.created_at).split(',')[0] }}</span>
                <span v-if="extraction.status === 'pending'" class="loading loading-spinner loading-xs text-primary"></span>
              </div>
              <p class="text-[10px] font-semibold text-base-content/50 uppercase tracking-widest">{{ formatDate(extraction.created_at).split(',')[1] }}</p>
            </div>
            
            <div class="text-right">
              <span class="text-[11px] font-semibold text-base-content/60">{{ formatDate(extraction.expires_at).split(',')[0] }}</span>
              <p class="text-[9px] uppercase font-bold text-error/60">{{ formatDate(extraction.expires_at).split(',')[1] }}</p>
            </div>
          </div>

          <div class="flex justify-between items-end mt-4 pt-3 border-t border-base-200">
            <div class="flex items-center gap-2">
              <div v-for="type in getUniqueSources(extraction.sources)" :key="type">
                <svg v-if="isSvgIcon(type)" class="w-5 h-5 text-base-content/70" :class="getIconConfig(type).svgClass" viewBox="0 0 24 24" fill="currentColor">
                  <path :d="getIconConfig(type).svgPath" />
                </svg>
                <span v-else :class="getIconConfig(type).textClass" class="text-lg">
                  {{ getIconConfig(type).text }}
                </span>
              </div>
              <span v-if="!getUniqueSources(extraction.sources).length" class="text-base-content/20 italic text-xs">No sources</span>
            </div>
            
            <div class="flex items-baseline gap-1.5">
              <span class="text-[10px] uppercase font-bold text-base-content/50">Topics</span>
              <span class="text-xl font-black text-primary font-mono leading-none">{{ extraction.results_count }}</span>
            </div>
          </div>
        </div>
      </div>
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
import { useSourceIcons } from '~/composables/useSourceIcons'
import { doc, onSnapshot } from 'firebase/firestore'

definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { $firebaseFirestore } = useNuxtApp()
const { user } = useAuth()
const { getIconConfig, isSvgIcon } = useSourceIcons()

const extractions = ref<any[]>([])
const totalResults = ref(0)
const page = ref(1)
const pageSize = ref(50)
const isLoadingResults = ref(true)
const isExtracting = ref(false)
const lastRunMessage = ref('')
const pendingListeners = new Map<string, () => void>()

function getUniqueSources(sources: string[]) {
  if (!sources || !Array.isArray(sources)) return []
  const types = new Set<string>()

  sources.forEach(s => {
    if (!s) return
    const raw = s.toLowerCase()
    if (raw.includes('reddit')) types.add('reddit')
    else if (raw.includes('hacker news') || raw.includes('hackernews')) types.add('hackernews')
    else if (raw.includes('bluesky')) types.add('bluesky')
    else if (raw.includes('indie hackers') || raw.includes('indiehackers')) types.add('indiehackers')
    // Filter out everything else to ensure only clean icons are shown
  })

  return Array.from(types)
}

function setupExtractionListener(extractionId: string) {
  if (!user.value?.uid || !extractionId || pendingListeners.has(extractionId)) return

  const unsubscribe = onSnapshot(
    doc($firebaseFirestore, 'users', user.value.uid, 'extractions', extractionId),
    (snapshot) => {
      const data = snapshot.data()
      if (!data) return

      const index = extractions.value.findIndex(e => e.id === extractionId)
      if (index !== -1) {
        // Update local object
        extractions.value[index] = {
          ...extractions.value[index],
          ...data,
          id: extractionId, // ensure ID stays
        }

        // If no longer pending, cleanup
        if (data.status === 'completed' || data.status === 'failed') {
          cleanupListener(extractionId)
          if (data.status === 'completed') {
            lastRunMessage.value = `Extraction completed! Found ${data.results_count || 0} topics.`
          } else {
            lastRunMessage.value = `Extraction failed: ${data.error || 'Unknown error'}`
          }
        }
      }
    }
  )

  pendingListeners.set(extractionId, unsubscribe)
}

function cleanupListener(extractionId: string) {
  const unsubscribe = pendingListeners.get(extractionId)
  if (unsubscribe) {
    unsubscribe()
    pendingListeners.delete(extractionId)
  }
}

async function fetchExtractions() {
  isLoadingResults.value = true
  try {
    const params = new URLSearchParams({
      page: String(page.value),
      page_size: String(pageSize.value),
    })

    const data = await apiFetch<any>(`/api/extractions?${params}`)
    extractions.value = data.extractions || []
    totalResults.value = data.total || 0

    // Restart listeners for any still-pending extractions
    extractions.value.forEach(ext => {
      if (ext.status === 'pending') {
        setupExtractionListener(ext.id)
      }
    })
  } catch (error) {
    console.error('Failed to fetch extractions:', error)
  } finally {
    isLoadingResults.value = false
  }
}


// Run extraction
async function runExtraction() {
  isExtracting.value = true
  lastRunMessage.value = ''
  try {
    const data = await apiFetch<any>('/api/extract', { method: 'POST', body: {} })

    if (data.status === 'pending' || data.id) {
      const extractionId = data.id || data.extraction_id
      // Add to list immediately
      extractions.value.unshift({
        id: extractionId,
        status: 'pending',
        created_at: new Date().toISOString(),
        sources: [],
        results_count: 0,
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
      })

      lastRunMessage.value = 'Extraction started in background...'
      setupExtractionListener(extractionId)
    } else {
      lastRunMessage.value = `Found ${data.results_count} trending topics!`
      if (data.extraction_id && data.results_count > 0) {
        navigateTo(`/extractions/${data.extraction_id}`)
      } else {
        await fetchExtractions()
      }
    }
  } catch (error: any) {
    lastRunMessage.value = `Extraction failed: ${error.data?.detail || error.message}`
  } finally {
    isExtracting.value = false
  }
}

// Format date
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Watch for page changes
watch([page], () => fetchExtractions())

// Initial load
onMounted(async () => {
  await fetchExtractions()
})

onUnmounted(() => {
  pendingListeners.forEach(unsubscribe => unsubscribe())
  pendingListeners.clear()
})
</script>
