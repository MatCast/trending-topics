<template>
  <div class="max-w-4xl mx-auto space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-black tracking-tight uppercase">Keywords</h1>
        <p class="text-muted-foreground font-bold">Manage keywords used to filter trending content.</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-4 py-8">
      <Skeleton v-for="i in 3" :key="i" class="h-32 w-full border-2 border-black" />
    </div>

    <div v-else class="space-y-8">
      <!-- Add Keywords -->
      <Card class="border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none">
        <CardHeader class="pb-4">
          <div class="flex items-start justify-between">
            <div>
              <CardTitle class="text-xl font-black uppercase">Add Keywords</CardTitle>
              <CardDescription class="text-black font-bold">Separate multiple keywords with commas.</CardDescription>
            </div>
            <UsageLimitBadge :current="activeKeywordCount" :limit="keywordLimit" type="active" />
          </div>
        </CardHeader>
        <CardContent>
          <div class="flex">
            <Input
              v-model="newKeywordInput"
              type="text"
              placeholder="e.g., AI, startup, GPT, machine learning"
              class="flex-1 border-2 border-black rounded-none shadow-none focus-visible:ring-0 focus-visible:border-black"
              :class="{ 'border-destructive': addError }"
              @keyup.enter="addKeywords"
            />
            <Button
              class="border-2 border-black border-l-0 rounded-none shadow-none hover:bg-primary transition-colors px-8"
              :disabled="isAdding"
              @click="addKeywords"
            >
              <Loader2 v-if="isAdding" class="size-4 animate-spin mr-2" />
              {{ isAdding ? 'Adding' : 'Add' }}
            </Button>
          </div>
          <div v-if="addError || isLimitReached" class="mt-3">
            <p v-if="addError" class="text-xs font-black text-destructive uppercase">{{ addError }}</p>
            <div v-else-if="isLimitReached" class="p-3 border-2 border-black bg-primary/20 flex items-center gap-2 text-xs font-bold uppercase">
              <AlertTriangle class="size-4" />
              <span>At active limit. New keywords will be disabled.</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Bulk Actions Bar -->
      <transition 
        enter-active-class="transition duration-200 ease-out" 
        enter-from-class="translate-y-4 opacity-0" 
        enter-to-class="translate-y-0 opacity-100" 
        leave-active-class="transition duration-150 ease-in" 
        leave-from-class="translate-y-0 opacity-100" 
        leave-to-class="translate-y-4 opacity-0"
      >
        <div v-if="selectedIds.size > 0" class="flex flex-wrap items-center gap-4 p-4 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] sticky top-4 z-20">
          <span class="text-xs font-black uppercase tracking-widest bg-black text-white px-3 py-1">{{ selectedIds.size }} Selected</span>
          <div class="flex flex-wrap gap-2 flex-1">
            <Button size="sm" variant="neutral" class="border-2 border-black hover:bg-primary h-8 uppercase font-black text-[10px]" @click="bulkAction('enable')">Enable</Button>
            <Button size="sm" variant="neutral" class="border-2 border-black hover:bg-muted h-8 uppercase font-black text-[10px]" @click="bulkAction('disable')">Disable</Button>
            <Button size="sm" variant="destructive" class="border-2 border-black hover:bg-destructive h-8 uppercase font-black text-[10px]" @click="bulkAction('delete')">Delete</Button>
          </div>
          <Button variant="ghost" size="sm" class="h-8 uppercase font-black text-[10px] hover:bg-transparent hover:underline" @click="selectedIds.clear()">Clear</Button>
        </div>
      </transition>

      <!-- Keywords List / Table -->
      <Card class="border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <CardContent class="p-0">
          <div v-if="keywords.length">
            <!-- Desktop Table -->
            <div class="hidden md:block">
              <Table>
                <TableHeader class="bg-black text-white">
                  <TableRow class="hover:bg-black border-b-2 border-black">
                    <TableHead class="w-12 py-4 pl-6">
                      <div class="flex items-center gap-1">
                        <Checkbox
                          class="border-2 border-white data-[state=checked]:bg-white data-[state=checked]:text-black"
                          :checked="isAllSelected"
                          @update:checked="toggleSelectAll"
                        />
                        <DropdownMenu>
                          <DropdownMenuTrigger as-child>
                            <Button variant="ghost" size="icon" class="h-6 w-6 p-0 hover:bg-white/20 text-white rounded-none">
                              <ChevronDown class="size-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="start" class="border-2 border-black rounded-none shadow-[4px_4px_0px_0px_black]">
                            <DropdownMenuItem class="font-black uppercase text-xs cursor-pointer" @click="bulkAction('enable')" :disabled="selectedIds.size === 0">
                              <CheckCircle class="size-4 mr-2" />
                              Enable Selected
                            </DropdownMenuItem>
                            <DropdownMenuItem class="font-black uppercase text-xs cursor-pointer" @click="bulkAction('disable')" :disabled="selectedIds.size === 0">
                              <Circle class="size-4 mr-2" />
                              Disable Selected
                            </DropdownMenuItem>
                            <DropdownMenuItem class="font-black uppercase text-xs cursor-pointer text-destructive focus:text-destructive" @click="bulkAction('delete')" :disabled="selectedIds.size === 0">
                              <Trash2 class="size-4 mr-2" />
                              Delete Selected
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableHead>
                    <TableHead class="text-white font-black uppercase py-4">Keyword</TableHead>
                    <TableHead class="text-white font-black uppercase py-4 text-center">Status</TableHead>
                    <TableHead class="text-white font-black uppercase py-4">Added</TableHead>
                    <TableHead class="w-12 py-4 pr-6"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow
                    v-for="kw in keywords"
                    :key="`desktop-${kw.id}`"
                    class="border-b-2 border-black hover:bg-muted/30 transition-colors"
                    :class="{ 'opacity-60 grayscale': !kw.enabled }"
                  >
                    <TableCell class="py-4 pl-6">
                      <Checkbox
                        class="border-2 border-black"
                        :checked="selectedIds.has(kw.id)"
                        @update:checked="toggleSelect(kw.id)"
                      />
                    </TableCell>
                    <TableCell class="font-black text-lg py-4">{{ kw.text }}</TableCell>
                    <TableCell class="text-center py-4">
                      <Switch
                        size="sm"
                        :checked="kw.enabled"
                        :disabled="isToggling"
                        @update:checked="(val: boolean) => toggleKeyword(kw, val, isLimitReached)"
                      />
                    </TableCell>
                    <TableCell class="text-xs font-bold uppercase py-4 text-muted-foreground">{{ formatDate(kw.created_at) }}</TableCell>
                    <TableCell class="py-4 pr-6 text-right">
                      <DeleteButton 
                        @click="deleteSingle(kw)" 
                      />
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>

            <!-- Mobile List -->
            <div class="md:hidden divide-y-2 divide-black">
              <div
                v-for="kw in keywords"
                :key="`mobile-${kw.id}`"
                class="p-4 space-y-4"
                :class="{ 'opacity-60 grayscale bg-muted/20': !kw.enabled, 'bg-primary/10': selectedIds.has(kw.id) }"
              >
                <div class="flex items-start justify-between gap-4">
                  <div class="flex items-start gap-4">
                    <Checkbox
                      class="border-2 border-black mt-1"
                      :checked="selectedIds.has(kw.id)"
                      @update:checked="toggleSelect(kw.id)"
                    />
                    <div>
                      <span class="font-black text-xl block leading-tight">{{ kw.text }}</span>
                      <span class="text-[10px] font-black uppercase text-muted-foreground">{{ formatDate(kw.created_at) }}</span>
                    </div>
                  </div>
                  <DeleteButton 
                    @click="deleteSingle(kw)" 
                  />
                </div>
                <div class="flex items-center justify-between border-t border-black/10 pt-4">
                  <span class="text-[10px] font-black uppercase text-muted-foreground tracking-widest">Active Status</span>
                  <Switch
                    :checked="kw.enabled"
                    :disabled="isToggling"
                    @update:checked="(val: boolean) => toggleKeyword(kw, val, isLimitReached)"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else class="text-center py-20 border-4 border-dashed border-muted flex flex-col items-center">
            <div class="flex aspect-square size-16 items-center justify-center border-4 border-black bg-muted mb-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
              <Tag class="size-8 text-muted-foreground" />
            </div>
            <h3 class="text-2xl font-black mb-1 uppercase">No keywords yet</h3>
            <p class="text-muted-foreground font-bold mb-8">Add keywords above to start filtering trends.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

import { Loader2, AlertTriangle, X, Tag, ChevronDown, CheckCircle, Circle, Trash2 } from 'lucide-vue-next'
import { Checkbox } from '@/components/ui/checkbox'
import { Switch } from '@/components/ui/switch'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import DeleteButton from '@/components/DeleteButton.vue'
import { toast } from 'vue-sonner'
import { useKeywordToggle } from '~/composables/useKeywordToggle'

const { apiFetch } = useApi()
const { keywordLimit, isKeywordUnlimited, fetchProfile } = useUser()
const { toggle: toggleKeyword, isSaving: isToggling } = useKeywordToggle()

const keywords = ref<any[]>([])
const isLoading = ref(true)
const isAdding = ref(false)
const newKeywordInput = ref('')
const addError = ref('')
const selectedIds = ref(new Set<string>())

const isAllSelected = computed(() =>
  keywords.value.length > 0 && selectedIds.value.size === keywords.value.length
)
const isPartiallySelected = computed(() =>
  selectedIds.value.size > 0 && selectedIds.value.size < keywords.value.length
)

const activeKeywordCount = computed(() => keywords.value.filter(k => k.enabled).length)

const isLimitReached = computed(() => {
  if (isKeywordUnlimited.value) return false
  return activeKeywordCount.value >= keywordLimit.value
})

function toggleSelect(id: string) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  // Force reactivity
  selectedIds.value = new Set(selectedIds.value)
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIds.value.clear()
  } else {
    selectedIds.value = new Set(keywords.value.map(k => k.id))
  }
}

async function fetchKeywords() {
  isLoading.value = true
  try {
    keywords.value = await apiFetch<any[]>('/api/keywords')
  } catch (error) {
    console.error('Failed to fetch keywords:', error)
  } finally {
    isLoading.value = false
  }
}

async function addKeywords() {
  const rawInput = newKeywordInput.value.trim()
  addError.value = ''
  if (!rawInput) return

  // Split by commas, trim each, filter empty
  const kwList = rawInput.split(',').map(s => s.trim()).filter(Boolean)
  if (!kwList.length) return

  isAdding.value = true
  try {
    // Check for duplicates
    const existingTexts = new Set(keywords.value.map(k => k.text.toLowerCase()))
    const duplicates = kwList.filter(k => existingTexts.has(k.toLowerCase()))
    const uniqueToAdd = kwList.filter(k => !existingTexts.has(k.toLowerCase()))

    if (duplicates.length > 0) {
      toast.error('Keyword already exists', { 
        description: `${duplicates.join(', ')} is already in your list.` 
      })
      if (uniqueToAdd.length === 0) {
        isAdding.value = false
        return
      }
    }

    const created = await apiFetch<any[]>('/api/keywords', {
      method: 'POST',
      body: { keywords: uniqueToAdd },
    })
    keywords.value.push(...created)
    newKeywordInput.value = ''
    toast.success(`${uniqueToAdd.length} keyword(s) added`)
  } catch (error: any) {
    addError.value = error.data?.detail || 'Failed to add keywords'
    toast.error('Failed to add keywords', { description: addError.value })
  } finally {
    isAdding.value = false
  }
}



async function deleteSingle(kw: any) {
  try {
    await apiFetch(`/api/keywords/${kw.id}`, { method: 'DELETE' })
    keywords.value = keywords.value.filter(k => k.id !== kw.id)
    selectedIds.value.delete(kw.id)
    selectedIds.value = new Set(selectedIds.value)
    toast.success(`Keyword deleted`)
  } catch (error) {
    console.error('Failed to delete keyword:', error)
    toast.error('Failed to delete keyword')
  }
}

async function bulkAction(action: string) {
  const ids = Array.from(selectedIds.value)
  if (!ids.length) return

  if (action === 'delete') {
    const confirmed = window.confirm(`Are you sure you want to delete ${ids.length} keywords?`)
    if (!confirmed) return
  }

  try {
    await apiFetch('/api/keywords/bulk', {
      method: 'POST',
      body: { keyword_ids: ids, action },
    })

    if (action === 'delete') {
      keywords.value = keywords.value.filter(k => !selectedIds.value.has(k.id))
      toast.success(`${ids.length} keywords deleted`)
    } else if (action === 'enable') {
      keywords.value.forEach(k => {
        if (selectedIds.value.has(k.id)) k.enabled = true
      })
      toast.success(`${ids.length} keywords enabled`)
    } else if (action === 'disable') {
      keywords.value.forEach(k => {
        if (selectedIds.value.has(k.id)) k.enabled = false
      })
      toast.success(`${ids.length} keywords disabled`)
    }

    selectedIds.value.clear()
    selectedIds.value = new Set()
  } catch (error) {
    console.error('Bulk action failed:', error)
    toast.error('Bulk action failed')
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  fetchKeywords()
  fetchProfile()
})
</script>
