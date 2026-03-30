<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-black tracking-tight uppercase">Sources</h1>
        <p class="text-muted-foreground font-bold">Manage your trending topic sources.</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-4 py-8">
      <Skeleton v-for="i in 3" :key="i" class="h-48 w-full border-2 border-black" />
    </div>

    <div v-else class="space-y-8">
      <!-- Dynamic source cards from catalog -->
      <Card
        v-for="catalogSource in catalog"
        :key="catalogSource.id"
        class="border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden"
      >
        <CardHeader class="border-b-2 border-black bg-muted/20">
          <div class="flex items-center justify-between gap-4">
            <CardTitle class="flex items-center gap-3 text-2xl font-black uppercase truncate">
              <!-- Dynamic icon from composable -->
              <div class="flex aspect-square size-10 items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <component :is="getLucideIcon(catalogSource.id)" class="size-6" />
              </div>
              <span class="truncate">{{ catalogSource.name }}</span>
            </CardTitle>

            <!-- Singleton: show toggle or enable button -->
            <template v-if="!catalogSource.is_multi_instance">
              <div v-if="getSingletonSource(catalogSource.id)" class="flex items-center gap-3">
                <span class="text-[10px] font-black uppercase text-muted-foreground">{{ getSingletonSource(catalogSource.id)!.enabled ? 'Enabled' : 'Disabled' }}</span>
                <Switch
                  :checked="getSingletonSource(catalogSource.id)!.enabled"
                  :disabled="isTogglingSource"
                  @update:checked="(val: boolean) => toggleStatus(getSingletonSource(catalogSource.id)!, val)"
                />
              </div>
              <Button v-else size="sm" class="border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] cursor-pointer" @click="addSingletonSource(catalogSource)">
                Enable
              </Button>
            </template>
          </div>
          <CardDescription class="text-black font-bold mt-2">
            {{ catalogSource.description }}
          </CardDescription>
        </CardHeader>

        <CardContent class="pt-6">
          <a
            v-if="catalogSource.website_url"
            :href="catalogSource.website_url"
            target="_blank"
            rel="noopener"
            class="inline-flex items-center gap-1 font-bold text-xs hover:underline mb-4"
          >
            <ExternalLink class="size-3" />
            {{ catalogSource.website_url }}
          </a>

          <!-- Multi-instance sources: add form + list -->
          <template v-if="catalogSource.is_multi_instance">
            <!-- Dynamic config form from config_schema -->
            <div class="space-y-4">
              <div v-if="catalogSource.id === 'reddit'" class="flex flex-wrap items-center justify-between gap-2">
                <span class="text-xs font-black uppercase tracking-widest text-muted-foreground">Add Subreddit</span>
                <UsageLimitBadge :current="redditSourceCount" :limit="redditLimit" type="active" />
              </div>
              
              <div class="flex" v-for="(fieldSchema, fieldKey) in catalogSource.config_schema" :key="fieldKey">
                <div v-if="catalogSource.id === 'reddit'" class="flex items-center justify-center px-4 border-2 border-black border-r-0 bg-muted font-black">r/</div>
                <Input
                  v-model="multiInstanceInput[catalogSource.id]"
                  type="text"
                  :placeholder="fieldSchema.placeholder || `Add ${fieldSchema.label}...`"
                  class="flex-1 border-2 border-black rounded-none shadow-none focus-visible:ring-0 focus-visible:border-black"
                  :class="{ 'border-destructive': multiInstanceError[catalogSource.id] }"
                  @keyup.enter="addMultiInstanceSource(catalogSource)"
                  @input="multiInstanceError[catalogSource.id] = ''"
                />
                <Button 
                  class="border-2 border-black border-l-0 rounded-none shadow-none hover:bg-primary transition-colors px-6 cursor-pointer" 
                  @click="addMultiInstanceSource(catalogSource)"
                >
                  Add
                </Button>
              </div>

              <!-- Limit Warning -->
              <div v-if="isRedditLimitReached && catalogSource.id === 'reddit'" class="p-3 border-2 border-black bg-primary/20 flex items-center gap-2 text-xs font-bold uppercase">
                <AlertTriangle class="size-4" />
                <span>At active limit. New subreddits added as disabled.</span>
              </div>

              <p v-if="multiInstanceError[catalogSource.id]" class="text-xs font-black text-destructive uppercase tracking-tight">
                {{ multiInstanceError[catalogSource.id] }}
              </p>
            </div>

            <!-- List of user's instances -->
            <div class="space-y-3 mt-6">
              <div
                v-for="src in getMultiInstanceSources(catalogSource.id)"
                :key="src.id"
                class="flex items-center justify-between p-4 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] transition-all"
                :class="src.enabled ? 'bg-white' : 'bg-muted/30 opacity-70'"
              >
                <div class="flex flex-wrap items-center gap-4 flex-1 min-w-0">
                  <Switch 
                    :checked="src.enabled" 
                    :disabled="isTogglingSource"
                    @update:checked="(val: boolean) => toggleStatus(src, val, (err) => {
                      if (src.source_id === 'reddit') multiInstanceError['reddit'] = err
                    })" 
                  />
                  <span class="font-black truncate max-w-full text-lg">{{ src.name }}</span>
                  
                  <div class="flex items-center gap-2 ml-auto sm:ml-4">
                    <span class="text-[10px] font-black uppercase text-muted-foreground whitespace-nowrap">Global Keywords</span>
                    <Switch 
                      size="sm" 
                      :checked="src.use_global_keywords" 
                      :disabled="isTogglingSource"
                      @update:checked="(val: boolean) => toggleGlobalKeywords(src, val)" 
                    />
                  </div>
                </div>
                <DeleteButton 
                  class="ml-4" 
                  @click="deleteSource(src)" 
                />
              </div>
              <div v-if="!getMultiInstanceSources(catalogSource.id).length" class="text-center py-6 border-2 border-dashed border-muted text-muted-foreground font-bold uppercase text-sm">
                No {{ catalogSource.name }} sources configured
              </div>
            </div>
          </template>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

import { ExternalLink, AlertTriangle, MessageSquare, Hash, Globe, TrendingUp, X } from 'lucide-vue-next'
import { Switch } from '@/components/ui/switch'
import DeleteButton from '@/components/DeleteButton.vue'
import { toast } from 'vue-sonner'
import { useSourceToggle } from '~/composables/useSourceToggle'

const { apiFetch } = useApi()
const { getIconConfig, isSvgIcon } = useSourceIcons()
const { redditLimit, isRedditUnlimited, fetchProfile } = useUser()
const { toggleStatus, toggleGlobalKeywords, isSaving: isTogglingSource } = useSourceToggle()

function getLucideIcon(id: string) {
  const sourceId = id.toLowerCase()
  if (sourceId.includes('reddit')) return MessageSquare
  if (sourceId.includes('hackernews') || sourceId.includes('hacker news')) return Hash
  if (sourceId.includes('bluesky')) return Globe
  return TrendingUp
}

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

// Limits
const redditSourceCount = computed(() => 
  sources.value.filter((s: any) => s.source_id === 'reddit' && s.enabled).length
)
const isRedditLimitReached = computed(() => {
  if (isRedditUnlimited.value) return false
  return redditSourceCount.value >= redditLimit.value
})

async function fetchData() {
  isLoading.value = true
  try {
    const [catalogData, sourcesData] = await Promise.all([
      apiFetch<any[]>('/api/sources/catalog'),
      apiFetch<any[]>('/api/sources'),
      fetchProfile()
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
    toast.success(`${catalogSource.name} enabled`)
  } catch (error) {
    console.error('Failed to add source:', error)
    toast.error('Failed to enable source')
  }
}

async function addMultiInstanceSource(catalogSource: any) {
  const inputKey = catalogSource.id
  const inputVal = (multiInstanceInput.value[inputKey] || '').trim()
  multiInstanceError.value[inputKey] = ''

  if (!inputVal) return

  // Get first config field key (e.g., 'subreddit')
  const fieldKey = Object.keys(catalogSource.config_schema || {})[0] as string
  if (!fieldKey) return

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
        const idx = sources.value.findIndex(s => s.id === newSource.id)
        if (idx !== -1) sources.value[idx] = newSource
        toast.info(`${inputVal} re-enabled from history`)
      }
    } else {
      sources.value.push(newSource)
      toast.success(`${inputVal} added to sources`)
    }
    multiInstanceInput.value[inputKey] = ''
  } catch (error: any) {
    console.error('Failed to add source:', error)
    const detail = error.data?.detail || 'Failed to add. Please try again.'
    multiInstanceError.value[inputKey] = detail
    toast.error('Failed to add source', { description: detail })
  }
}



async function deleteSource(src: any) {
  try {
    await apiFetch(`/api/sources/${src.id}`, { method: 'DELETE' })
    sources.value = sources.value.filter(s => s.id !== src.id)
    toast.success(`${src.name} removed`)
  } catch (error) {
    console.error('Failed to delete source:', error)
    toast.error('Failed to remove source')
  }
}

onMounted(() => fetchData())
</script>
