<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-6">
      <!-- Top Header -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl font-black tracking-tight uppercase">Extraction History</h1>
          <p class="text-muted-foreground font-bold">Review your past extractions and trending topics.</p>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto">
          <div v-if="profile" class="hidden lg:block mr-2">
            <Badge variant="outline" class="border-2 border-black bg-white px-3 py-1 text-xs font-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              {{ extractionUsage.monthly }} / {{ extractionLimits.monthly }} Monthly
            </Badge>
          </div>

          <div class="flex items-center gap-2">
            <Button
              variant="outline"
              size="lg"
              class="group h-12 px-6 border-2 border-black bg-primary flex items-center justify-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all"
              :disabled="isExtracting || isAnyLimitReached"
              @click="runExtraction"
            >
              <Loader2 v-if="isExtracting" class="size-4 animate-spin" />
              <Plus v-else class="size-4" />
              <span v-if="isAnyLimitReached && !isExtracting">Limit Reached</span>
              <span v-else>{{ isExtracting ? 'Searching...' : 'New Extraction' }}</span>
            </Button>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger as-child>
                  <Button
                    variant="outline"
                    class="size-11 p-0 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none transition-all"
                    @click="openScheduleModal"
                  >
                    <Clock class="size-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent class="border-2 border-black rounded-none font-bold bg-white text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  Schedule Automation
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      </div>

      <!-- Settings Toolbar -->
      <ExtractionSettings
        v-model="userSettings"
        :saving="isSavingSettings"
        @change="saveSettings"
      />
    </div>

    <!-- Loading state -->
    <div v-if="isLoadingResults" class="space-y-4 py-8">
      <Skeleton v-for="i in 5" :key="i" class="h-24 w-full border-2 border-black" />
    </div>

    <!-- Empty state -->
    <div v-else-if="!extractions.length" class="text-center py-20 border-4 border-dashed border-muted flex flex-col items-center">
      <div class="flex aspect-square size-20 items-center justify-center border-4 border-black bg-muted mb-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
        <FileSearch class="size-10 text-muted-foreground" />
      </div>
      <h3 class="text-2xl font-black mb-2 uppercase">No extractions yet</h3>
      <p class="text-muted-foreground font-bold mb-8">Run an extraction to find trending topics.</p>
      <Button size="lg" @click="runExtraction" class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        Run First Extraction
      </Button>
    </div>

    <!-- Extractions Table / Mobile Cards -->
    <div v-else class="pb-8">
      <!-- Desktop Table -->
      <div class="hidden md:block">
        <Table class="border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
          <TableHeader class="bg-black text-white">
            <TableRow class="hover:bg-black border-b-2 border-black">
              <TableHead class="text-white font-black uppercase py-4 pl-6">Run Date</TableHead>
              <TableHead class="text-white font-black uppercase py-4">Target Platforms</TableHead>
              <TableHead class="text-white font-black uppercase py-4 text-right">Topics</TableHead>
              <TableHead class="text-white font-black uppercase py-4 text-right pr-6">Expires</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-for="extraction in extractions" :key="`desktop-${extraction.id}`"
              class="group cursor-pointer border-b-2 border-black hover:bg-primary transition-colors"
              @click="extraction.status !== 'pending' && navigateTo(`/extractions/${extraction.id}`)">
              <TableCell class="py-6 pl-6">
                <div class="flex flex-col">
                  <div class="flex items-center gap-2">
                    <span class="text-lg font-black">{{ formatDate(extraction.created_at).split(',')[0] }}</span>
                    <Loader2 v-if="extraction.status === 'pending'" class="size-4 animate-spin text-primary" />
                  </div>
                  <span class="text-xs font-bold text-muted-foreground uppercase">{{ formatDate(extraction.created_at).split(',')[1] }}</span>
                </div>
              </TableCell>
              <TableCell class="py-6">
                <div class="flex items-center gap-4">
                  <div v-for="type in getUniqueSources(extraction.sources)" :key="type" class="flex items-center gap-1">
                    <div class="size-8 flex items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                      <component :is="getLucideIcon(type)" class="size-5" />
                    </div>
                  </div>
                  <span v-if="!getUniqueSources(extraction.sources).length" class="text-muted-foreground italic text-sm font-bold">No sources</span>
                </div>
              </TableCell>
              <TableCell class="text-right py-6">
                <div class="inline-flex flex-col items-end">
                  <span class="text-2xl font-black font-mono">{{ extraction.results_count }}</span>
                </div>
              </TableCell>
              <TableCell class="text-right py-6 pr-6">
                <div class="flex flex-col items-end">
                  <span class="text-sm font-black">{{ formatDate(extraction.expires_at).split(',')[0] }}</span>
                  <span class="text-[10px] font-black uppercase text-destructive">{{ formatDate(extraction.expires_at).split(',')[1] }}</span>
                </div>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>

      <!-- Mobile Cards -->
      <div class="md:hidden space-y-4">
        <Card v-for="extraction in extractions" :key="`mobile-${extraction.id}`"
          class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-none relative overflow-hidden"
          :class="extraction.status === 'pending' ? 'opacity-80 active:scale-100' : 'active:scale-[0.98] cursor-pointer'"
          @click="extraction.status !== 'pending' && navigateTo(`/extractions/${extraction.id}`)">
          <CardHeader class="pb-2">
            <div class="flex justify-between items-start">
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-lg font-black">{{ formatDate(extraction.created_at).split(',')[0] }}</span>
                  <Loader2 v-if="extraction.status === 'pending'" class="size-4 animate-spin text-primary" />
                </div>
                <p class="text-[10px] font-black text-muted-foreground uppercase tracking-wider">{{ formatDate(extraction.created_at).split(',')[1] }}</p>
              </div>

              <div class="text-right">
                <span class="text-[11px] font-black truncate block">{{ formatDate(extraction.expires_at).split(',')[0] }}</span>
                <p class="text-[9px] font-black uppercase text-destructive">{{ formatDate(extraction.expires_at).split(',')[1] }}</p>
              </div>
            </div>
          </CardHeader>
          <CardFooter class="pt-2 border-t-2 border-black flex justify-between items-end bg-muted/30">
            <div class="flex items-center gap-2">
              <div v-for="type in getUniqueSources(extraction.sources)" :key="type" class="size-6 flex items-center justify-center border-2 border-black bg-white shadow-[1px_1px_0px_0px_rgba(0,0,0,1)]">
                <component :is="getLucideIcon(type)" class="size-3.5" />
              </div>
              <span v-if="!getUniqueSources(extraction.sources).length" class="text-muted-foreground italic text-xs font-bold">No sources</span>
            </div>

            <div class="flex items-center gap-2">
              <span class="text-[10px] font-black uppercase text-muted-foreground">Topics</span>
              <span class="text-2xl font-black text-primary font-mono leading-none">{{ extraction.results_count }}</span>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalResults > pageSize" class="flex justify-center mt-6">
      <div class="flex border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] bg-white overflow-hidden uppercase font-black text-xs">
        <button
          class="px-4 py-2 border-r-2 border-black hover:bg-primary disabled:opacity-30 transition-colors"
          :disabled="page <= 1"
          @click="page--"
        >
          Prev
        </button>
        <div class="px-6 py-2 bg-muted/50">Page {{ page }}</div>
        <button
          class="px-4 py-2 border-l-2 border-black hover:bg-primary disabled:opacity-30 transition-colors"
          :disabled="page * pageSize >= totalResults"
          @click="page++"
        >
          Next
        </button>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useFormatDate } from '~/composables/useFormatDate'
import { useSourceIcons } from '~/composables/useSourceIcons'
import { doc, onSnapshot } from 'firebase/firestore'
import { Search, Clock, Loader2, FileSearch, Globe, Hash, TrendingUp, MessageSquare, Plus } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { $firebaseFirestore } = useNuxtApp()
const { user } = useAuth()
const { profile, fetchProfile, extractionUsage, extractionLimits, isAnyLimitReached, isFreeTier } = useUser()
const { getIconConfig, isSvgIcon } = useSourceIcons()

const extractions = ref<any[]>([])
const totalResults = ref(0)
const page = ref(1)
const pageSize = ref(50)
const isLoadingResults = ref(true)
const isExtracting = ref(false)
const pendingListeners = new Map<string, () => void>()

function getLucideIcon(type: string) {
  const type_lower = type.toLowerCase()
  if (type_lower.includes('reddit')) return MessageSquare
  if (type_lower.includes('hacker news') || type_lower.includes('hackernews')) return Hash
  if (type_lower.includes('bluesky')) return Globe
  return TrendingUp
}

// Settings & Schedule
const isSavingSettings = ref(false)
const userSettings = ref({
  time_window_hours: 3,
  max_trends_per_source: 3
})
const userSchedule = ref({
  active: false,
  type: 'manual',
  interval_hours: 3,
  hour_of_day: 9,
  day_of_week: 0
})


const scheduleModalRef = ref<any>(null)

async function fetchSettings() {
  try {
    const data = await apiFetch<any>('/api/settings')
    userSettings.value = {
      time_window_hours: data.time_window_hours || 3,
      max_trends_per_source: data.max_trends_per_source || 3,
    }
    userSchedule.value = {
      active: data.schedule?.active ?? false,
      type: data.schedule?.type || 'manual',
      interval_hours: data.schedule?.interval_hours || 3,
      hour_of_day: data.schedule?.hour_of_day || 9,
      day_of_week: data.schedule?.day_of_week || 0,
      ...data.schedule
    }
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  }
}

async function saveSettings() {
  if (isSavingSettings.value) return
  isSavingSettings.value = true
  try {
    await apiFetch('/api/settings', {
      method: 'PUT',
      body: {
        ...userSettings.value,
        schedule: userSchedule.value,
      },
    })
    // Also update profile to keep it in sync
    fetchProfile()
    if (scheduleModalRef.value) scheduleModalRef.value.showSuccess()
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSavingSettings.value = false
  }
}

function openScheduleModal() {
  if (scheduleModalRef.value) {
    scheduleModalRef.value.show()
  }
}

async function handleScheduleSave(payload: any) {
  if (payload.settings) userSettings.value = payload.settings
  if (payload.schedule) userSchedule.value = payload.schedule
  await saveSettings()
}

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
            toast.success('Extraction completed!', {
              description: `Found ${data.results_count || 0} topics.`,
            })
            setTimeout(() => {
              navigateTo(`/extractions/${extractionId}`)
            }, 1000)
          } else {
            toast.error('Extraction failed', {
              description: data.error || 'Unknown error',
            })
          }
        }
      }
    },
    (error) => {
      console.error("Firestore snapshot error:", error)
      toast.error('Listener Error', { description: error.message })
      cleanupListener(extractionId)
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
  try {
    const data = await apiFetch<any>('/api/extract', { method: 'POST', body: {} })

    // Refresh profile to update usage counters (add small delay for Firestore consistency)
    setTimeout(() => fetchProfile(), 1000)

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

      toast.info('Extraction started', { description: 'Running in background...' })
      setupExtractionListener(extractionId)
    } else {
      toast.success('Extraction completed!', { description: `Found ${data.results_count} trending topics.` })
      if (data.extraction_id && data.results_count > 0) {
        navigateTo(`/extractions/${data.extraction_id}`)
      } else {
        await fetchExtractions()
      }
    }
  } catch (error: any) {
    toast.error('Extraction failed', { description: error.data?.detail || error.message })
  } finally {
    isExtracting.value = false
  }
}

// Format date
const { formatDate } = useFormatDate()

// Watch for page changes
watch([page], () => fetchExtractions())

// Initial load
onMounted(async () => {
  fetchProfile()
  await fetchSettings()
  await fetchExtractions()
})

onUnmounted(() => {
  pendingListeners.forEach(unsubscribe => unsubscribe())
  pendingListeners.clear()
})
</script>
