<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold">Extraction History</h1>
        <p class="text-base-content/60 text-sm">Review your past extractions and trending topics.</p>
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
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12A2 2 0 007 21h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-1">No extractions yet</h3>
      <p class="text-base-content/60 text-sm mb-4">Run an extraction to find trending topics.</p>
      <button class="btn btn-primary btn-sm" @click="runExtraction">Run Extraction</button>
    </div>

    <!-- Extractions Table -->
    <div v-else class="overflow-x-auto">
      <table class="table table-zebra w-full">
        <thead>
          <tr>
            <th>Date</th>
            <th>Sources</th>
            <th class="text-right">Results Count</th>
            <th class="text-right">Expires On</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="extraction in extractions" :key="extraction.id" class="hover group">
            <td class="whitespace-nowrap font-medium">
              {{ formatDate(extraction.created_at) }}
            </td>
            <td>
               <div class="flex flex-wrap gap-1">
                 <span v-for="source in extraction.sources" :key="source" class="badge badge-sm badge-ghost">
                   {{ source }}
                 </span>
                 <span v-if="!extraction.sources || !extraction.sources.length" class="text-base-content/40 italic text-xs">Unknown</span>
               </div>
            </td>
            <td class="text-right font-mono">
              {{ extraction.results_count }}
            </td>
            <td class="text-right text-xs text-base-content/60">
              {{ formatDate(extraction.expires_at) }}
            </td>
            <td class="text-right w-12">
               <button 
                 class="btn btn-sm btn-ghost opacity-0 group-hover:opacity-100 transition-opacity" 
                 title="View Results"
                 @click="navigateTo(`/extractions/${extraction.id}`)"
               >
                 View
               </button>
            </td>
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

const extractions = ref<any[]>([])
const totalResults = ref(0)
const page = ref(1)
const pageSize = ref(50)
const isLoadingResults = ref(true)
const isExtracting = ref(false)
const lastRunMessage = ref('')

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
    lastRunMessage.value = `Found ${data.results_count} trending topics!`
    
    if (data.extraction_id && data.results_count > 0) {
        navigateTo(`/extractions/${data.extraction_id}`)
    } else {
        await fetchExtractions()
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
</script>
