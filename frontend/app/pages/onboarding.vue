<template>
  <div class="max-w-4xl mx-auto space-y-12 animate-in fade-in duration-500">
    <div class="text-center space-y-4">
      <div class="inline-flex items-center justify-center size-20 border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] -rotate-3 mb-4">
        <Rocket class="size-10 text-black animate-pulse" />
      </div>
      <h1 class="text-5xl font-black uppercase tracking-tight">Welcome Aboard</h1>
      <p class="text-xs font-black uppercase tracking-widest text-muted-foreground">Configure your trend intelligence engine in 4 steps</p>
    </div>

    <!-- Loading catalog -->
    <div v-if="isLoadingCatalog" class="flex flex-col items-center justify-center py-24 gap-4">
        <div class="size-16 flex items-center justify-center border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-bounce">
          <Loader2 class="size-8 text-black animate-spin" />
        </div>
        <p class="text-[10px] font-black uppercase tracking-widest">Initializing Catalog...</p>
    </div>

    <template v-else>
      <!-- Custom Neobrutalism Stepper -->
      <div class="flex items-center justify-between relative px-4">
        <div class="absolute inset-0 top-1/2 -translate-y-1/2 h-1 bg-black/10 z-0"></div>
        <div 
          v-for="step in [1, 2, 3, 4]" 
          :key="step"
          class="relative z-10 flex flex-col items-center gap-3"
        >
          <div 
            class="size-12 flex items-center justify-center border-4 border-black font-black text-xl transition-all"
            :class="currentStep >= step ? 'bg-primary translate-x-1 translate-y-1 shadow-none' : 'bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'"
          >
            {{ step }}
          </div>
          <span class="text-[8px] font-black uppercase tracking-widest bg-white px-2 border-2 border-black" v-if="step === 1">Keywords</span>
          <span class="text-[8px] font-black uppercase tracking-widest bg-white px-2 border-2 border-black" v-if="step === 2">Multi-Source</span>
          <span class="text-[8px] font-black uppercase tracking-widest bg-white px-2 border-2 border-black" v-if="step === 3">Others</span>
          <span class="text-[8px] font-black uppercase tracking-widest bg-white px-2 border-2 border-black" v-if="step === 4">Finish</span>
        </div>
      </div>

      <!-- Step 1: Global Keywords -->
      <Card v-if="currentStep === 1" class="border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <div class="bg-black p-4">
          <h2 class="text-xl font-black uppercase text-white tracking-widest flex items-center gap-3">
            <Search class="size-6" />
            Global Context
          </h2>
        </div>
        <div class="p-8 space-y-8">
          <p class="text-xs font-bold text-muted-foreground uppercase leading-relaxed max-w-xl">
            These keywords will be used to filter content from sources that support keyword search. Separate terms with commas.
          </p>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-[10px] font-black uppercase tracking-[0.2em] text-black">Target Keywords</span>
              <UsageLimitBadge :current="activeKeywordCountDraft" :limit="keywordLimit" type="active" />
            </div>
            
            <div class="flex gap-4">
              <Input
                v-model="newKeyword"
                placeholder="e.g. AI, STARTUP, GPT-4"
                class="flex-1 h-14 border-4 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] font-black uppercase placeholder:text-black/20 focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:translate-x-0.5 focus-visible:translate-y-0.5 focus-visible:shadow-none transition-all"
                @keyup.enter="addKeyword"
              />
              <Button 
                class="h-14 px-10 border-4 border-black bg-primary text-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="addKeyword"
              >
                Add Term
              </Button>
            </div>
            
            <div v-if="isKeywordLimitReached" class="bg-yellow-400 border-2 border-black p-3 flex items-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] animate-in slide-in-from-top-2">
              <AlertTriangle class="size-5 text-black shrink-0" />
              <p class="text-[10px] font-black uppercase text-black leading-tight">
                ACTIVE LIMIT REACHED. ADDITIONAL KEYWORDS WILL BE SAVED AS DISABLED.
              </p>
            </div>
          </div>

          <div class="flex flex-wrap gap-3 pt-4 border-t-2 border-black border-dashed">
            <Badge
              v-for="(kw, idx) in globalKeywords"
              :key="idx"
              class="border-2 border-black bg-white text-black font-black uppercase text-[10px] rounded-none px-4 py-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] flex items-center gap-3 transition-all hover:bg-red-400 hover:text-white group cursor-pointer"
              @click="globalKeywords.splice(idx, 1)"
            >
              {{ kw }}
              <X class="size-3 transition-transform group-hover:scale-125" />
            </Badge>
            <div v-if="!globalKeywords.length" class="py-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">
              No keywords defined yet — using default trends
            </div>
          </div>

          <div class="flex justify-end pt-8">
            <Button 
              class="h-14 px-12 border-4 border-black bg-black text-white rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all group"
              @click="currentStep = multiInstanceSources.length ? 2 : (singletonSources.length ? 3 : 4)"
            >
              Continue Execution
              <ChevronRight class="size-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </Card>

      <!-- Step 2: Multi-instance sources (e.g., Reddit) -->
      <Card v-if="currentStep === 2" class="border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <div class="bg-black p-4">
          <h2 class="text-xl font-black uppercase text-white tracking-widest flex items-center gap-3">
            <Globe class="size-6" />
            Regional Channels
          </h2>
        </div>
        <div class="p-8 space-y-10">
          <div v-for="catalogSource in multiInstanceSources" :key="catalogSource.id" class="space-y-8">
            <div class="space-y-2">
              <div class="flex items-center gap-3">
                <div class="size-10 flex items-center justify-center border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                  <svg v-if="isSvgIcon(catalogSource.icon)" class="size-6 fill-current" viewBox="0 0 24 24">
                    <path :d="getIconConfig(catalogSource.icon).svgPath" />
                  </svg>
                  <span v-else class="text-sm font-black">{{ getIconConfig(catalogSource.icon).text }}</span>
                </div>
                <h3 class="text-2xl font-black uppercase tracking-tight">{{ catalogSource.name }}</h3>
              </div>
              <p class="text-xs font-bold text-muted-foreground uppercase leading-relaxed">{{ catalogSource.description }}</p>
            </div>

            <!-- Dynamic config form -->
            <div class="space-y-4" v-for="(fieldSchema, fieldKey) in catalogSource.config_schema" :key="fieldKey">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black uppercase tracking-[0.2em] text-black">Target {{ fieldSchema.label }}</span>
                <UsageLimitBadge
                  v-if="catalogSource.id === 'reddit'"
                  :current="redditSourceCount"
                  :limit="redditLimit"
                  type="active"
                />
              </div>
              
              <div class="flex gap-4">
                <div class="flex-1 flex gap-0">
                   <div v-if="catalogSource.id === 'reddit'" class="h-14 px-4 bg-muted border-4 border-black border-r-0 flex items-center font-black text-black">r/</div>
                   <Input
                    v-model="multiInstanceDrafts[catalogSource.id]"
                    :placeholder="fieldSchema.placeholder || `e.g. ${fieldSchema.label}`"
                    class="h-14 border-4 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] font-black uppercase placeholder:text-black/20 focus-visible:ring-0 transition-all"
                    :class="{ 'border-red-500 shadow-red-500/20': multiDraftError[catalogSource.id] }"
                    @keyup.enter="addDraftInstance(catalogSource)"
                  />
                </div>
                <Button 
                  class="h-14 px-10 border-4 border-black bg-primary text-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                  @click="addDraftInstance(catalogSource)"
                >
                  Anchor
                </Button>
              </div>
              
              <p v-if="multiDraftError[catalogSource.id]" class="text-[10px] font-black uppercase text-red-500 animate-in fade-in slide-in-from-left-2">
                {{ multiDraftError[catalogSource.id] }}
              </p>

              <div v-if="catalogSource.id === 'reddit' && isRedditLimitReached" class="bg-yellow-400 border-2 border-black p-3 flex items-center gap-3 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                <AlertTriangle class="size-5 text-black shrink-0" />
                <p class="text-[10px] font-black uppercase text-black leading-tight">
                  ACTIVE REDDIT LIMIT REACHED. ADDITIONAL SUBS WILL BE ADDED AS DISABLED.
                </p>
              </div>
            </div>

            <!-- Pending instances list -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div
                v-for="(src, idx) in pendingMultiInstances[catalogSource.id] || []"
                :key="idx"
                class="group flex items-center justify-between p-4 border-2 border-black transition-all bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
                :class="{ 'opacity-50 grayscale': !src.enabled }"
              >
                <div class="flex items-center gap-4">
                  <Switch 
                    size="sm"
                    :checked="src.enabled" 
                    @update:checked="(val: boolean) => toggleDraftSourceManual(val, src, catalogSource.id)" 
                  />
                  <div class="space-y-0.5">
                    <span class="text-sm font-black uppercase leading-none">{{ src.name }}</span>
                    <div class="flex items-center gap-2">
                         <span class="text-[8px] font-black uppercase text-muted-foreground">Context Filtering</span>
                         <Switch 
                            size="sm"
                            v-model:checked="src.use_global_keywords" 
                          />
                    </div>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  class="size-8 p-0 rounded-none hover:bg-black hover:text-white transition-colors"
                  @click="(pendingMultiInstances[catalogSource.id] || []).splice(idx, 1)"
                >
                  <X class="size-4" />
                </Button>
              </div>
              <div v-if="!(pendingMultiInstances[catalogSource.id] || []).length" class="col-span-full py-8 text-center border-2 border-black border-dashed bg-muted/20">
                <p class="text-[10px] font-black uppercase text-muted-foreground tracking-widest">No active channels anchored</p>
              </div>
            </div>
          </div>

          <div class="flex justify-between border-t-4 border-black border-double pt-8">
            <Button 
                variant="outline"
                class="h-14 px-12 border-4 border-black bg-white text-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="currentStep = 1"
            >
                <ChevronLeft class="size-5 mr-2" />
                Backtrack
            </Button>
            <Button 
                class="h-14 px-12 border-4 border-black bg-black text-white rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="currentStep = singletonSources.length ? 3 : 4"
            >
                Proceed to Integration
                <ChevronRight class="size-5 ml-2" />
            </Button>
          </div>
        </div>
      </Card>

      <!-- Step 3: Singleton sources -->
      <Card v-if="currentStep === 3" class="border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <div class="bg-black p-4">
          <h2 class="text-xl font-black uppercase text-white tracking-widest flex items-center gap-3">
            <Zap class="size-6" />
            Direct Feeds
          </h2>
        </div>
        <div class="p-8 space-y-8">
          <p class="text-xs font-bold text-muted-foreground uppercase leading-relaxed max-w-xl">
            Enable additional trend sources. These use your global keywords for deep scanning.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div
              v-for="catalogSource in singletonSources"
              :key="catalogSource.id"
              class="group flex flex-col p-6 border-4 border-black bg-white transition-all shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-1 hover:translate-y-1"
              :class="{ 'bg-primary/5 border-primary': singletonToggles[catalogSource.id] }"
            >
              <div class="flex items-center justify-between mb-6">
                <div class="size-12 flex items-center justify-center border-4 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] group-hover:bg-primary transition-colors">
                  <svg v-if="isSvgIcon(catalogSource.icon)" class="size-6 fill-current" viewBox="0 0 24 24">
                    <path :d="getIconConfig(catalogSource.icon).svgPath" />
                  </svg>
                  <span v-else class="text-sm font-black">{{ getIconConfig(catalogSource.icon).text }}</span>
                </div>
                <Switch 
                  v-model:checked="singletonToggles[catalogSource.id]" 
                  class="data-[state=checked]:bg-primary border-4 border-black h-8 w-14 p-0 shadow-none scale-125"
                />
              </div>
              <div class="space-y-1">
                <h3 class="text-lg font-black uppercase tracking-tight">{{ catalogSource.name }}</h3>
                <p class="text-[10px] font-bold text-muted-foreground uppercase leading-tight">{{ catalogSource.description }}</p>
              </div>
            </div>
          </div>

          <div class="flex justify-between border-t-4 border-black border-double pt-8">
            <Button 
                variant="outline"
                class="h-14 px-12 border-4 border-black bg-white text-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="currentStep = multiInstanceSources.length ? 2 : 1"
            >
                <ChevronLeft class="size-5 mr-2" />
                Backtrack
            </Button>
            <Button 
                class="h-14 px-12 border-4 border-black bg-black text-white rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="currentStep = 4"
            >
                Final Calibration
                <ChevronRight class="size-5 ml-2" />
            </Button>
          </div>
        </div>
      </Card>

      <!-- Step 4: Preferences -->
      <Card v-if="currentStep === 4" class="border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <div class="bg-black p-4">
          <h2 class="text-xl font-black uppercase text-white tracking-widest flex items-center gap-3">
            <SlidersHorizontal class="size-6" />
            System Calibration
          </h2>
        </div>
        <div class="p-8 space-y-12">
          <p class="text-xs font-bold text-muted-foreground uppercase leading-relaxed max-w-xl">
            Configure extraction depth and sensitivity.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div class="space-y-4">
              <div class="flex items-center gap-3">
                 <div class="size-8 border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center">
                    <Clock class="size-4" />
                 </div>
                 <span class="text-[10px] font-black uppercase tracking-widest text-black">Time Horizon</span>
              </div>
              <div class="relative pt-6">
                 <input 
                    type="range" 
                    v-model.number="timeWindowHours" 
                    min="1" 
                    max="168" 
                    class="w-full h-8 bg-black/10 appearance-none border-4 border-black cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none 
                    [&::-webkit-slider-thumb]:size-8 
                    [&::-webkit-slider-thumb]:bg-primary 
                    [&::-webkit-slider-thumb]:border-4 
                    [&::-webkit-slider-thumb]:border-black
                    [&::-webkit-slider-thumb]:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" 
                />
                <div class="flex justify-between mt-4">
                   <div class="text-[10px] font-black uppercase px-2 py-1 border-2 border-black bg-white">1 HR</div>
                   <div class="text-[10px] font-black uppercase px-4 py-1 border-4 border-black bg-primary translate-y-2">{{ timeWindowHours }} HOURS</div>
                   <div class="text-[10px] font-black uppercase px-2 py-1 border-2 border-black bg-white">168 HRS</div>
                </div>
              </div>
            </div>

            <div class="space-y-4">
              <div class="flex items-center gap-3">
                 <div class="size-8 border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] flex items-center justify-center">
                    <Database class="size-4" />
                 </div>
                 <span class="text-[10px] font-black uppercase tracking-widest text-black">Payload Limit</span>
              </div>
              <div class="relative pt-6">
                 <input 
                    type="range" 
                    v-model.number="maxTrendsPerSource" 
                    min="1" 
                    max="50" 
                    class="w-full h-8 bg-black/10 appearance-none border-4 border-black cursor-pointer
                    [&::-webkit-slider-thumb]:appearance-none 
                    [&::-webkit-slider-thumb]:size-8 
                    [&::-webkit-slider-thumb]:bg-primary 
                    [&::-webkit-slider-thumb]:border-4 
                    [&::-webkit-slider-thumb]:border-black
                    [&::-webkit-slider-thumb]:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" 
                />
                <div class="flex justify-between mt-4">
                   <div class="text-[10px] font-black uppercase px-2 py-1 border-2 border-black bg-white">1 PT</div>
                   <div class="text-[10px] font-black uppercase px-4 py-1 border-4 border-black bg-primary translate-y-2">{{ maxTrendsPerSource }} TOPICS</div>
                   <div class="text-[10px] font-black uppercase px-2 py-1 border-2 border-black bg-white">50 PTS</div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-between pt-12 border-t-4 border-black border-double pt-8">
            <Button 
                variant="outline"
                class="h-14 px-12 border-4 border-black bg-white text-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                @click="currentStep = singletonSources.length ? 3 : (multiInstanceSources.length ? 2 : 1)"
            >
                <ChevronLeft class="size-5 mr-2" />
                Backtrack
            </Button>
            <Button 
                class="h-14 px-12 border-4 border-black bg-primary text-black rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] uppercase font-black hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                :disabled="isSaving"
                @click="saveAndContinue"
            >
                <Loader2 v-if="isSaving" class="size-5 mr-2 animate-spin" />
                {{ isSaving ? 'Executing Deploy...' : 'Finalize & Launch' }}
                <Rocket v-if="!isSaving" class="size-5 ml-2 group-hover:-translate-y-1 transition-transform" />
            </Button>
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { 
    Rocket, Search, Loader2, X, ChevronRight, ChevronLeft, 
    Globe, AlertTriangle, Zap, SlidersHorizontal, Clock, Database 
} from 'lucide-vue-next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'

definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { getIconConfig, isSvgIcon } = useSourceIcons()
const { redditLimit, isRedditUnlimited, keywordLimit, isKeywordUnlimited, fetchProfile } = useUser()

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

const activeKeywordCountDraft = computed(() => {
  if (isKeywordUnlimited.value) return globalKeywords.value.length
  return Math.min(globalKeywords.value.length, keywordLimit.value)
})

const isKeywordLimitReached = computed(() => {
  if (isKeywordUnlimited.value) return false
  return globalKeywords.value.length >= keywordLimit.value
})

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

const redditSourceCount = computed(() =>
  (pendingMultiInstances.value['reddit'] || []).filter(s => s.enabled).length
)
const isRedditLimitReached = computed(() => {
  if (isRedditUnlimited.value) return false
  return redditSourceCount.value >= redditLimit.value
})

function addDraftInstance(catalogSource: any) {
  const inputVal = (multiInstanceDrafts.value[catalogSource.id] || '').trim()
  multiDraftError.value[catalogSource.id] = ''
  if (!inputVal) return

  const fieldKey = Object.keys(catalogSource.config_schema || {})[0] as string

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

  let enabledByDefault = true
  if (catalogSource.id === 'reddit' && isRedditLimitReached.value) {
    enabledByDefault = false
  }

  pendingMultiInstances.value[catalogSource.id]!.push({
    source_id: catalogSource.id,
    name: displayName,
    enabled: enabledByDefault,
    use_global_keywords: false,
    params: { [fieldKey]: inputVal },
  })
  multiInstanceDrafts.value[catalogSource.id] = ''
}

function toggleDraftSourceManual(checked: boolean, src: any, sourceId: string) {
  if (checked && sourceId === 'reddit') {
    if (!isRedditUnlimited.value && redditSourceCount.value >= redditLimit.value) {
      multiDraftError.value[sourceId] = 'Limit reached. Disable another to enable this one.'
      return
    }
  }
  src.enabled = checked
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
  await fetchProfile()
  await checkOnboardingStatus()
  await fetchCatalog()
})
</script>
