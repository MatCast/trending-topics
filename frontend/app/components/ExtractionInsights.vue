<template>
  <div v-if="hasInsights" class="space-y-8 mb-10 animate-in fade-in slide-in-from-top-4 duration-500">
    <!-- Zero Result Summary (Top Alerts) -->
    <div v-if="zeroResultInsights.length" class="space-y-4">
      <div class="flex items-center gap-2">
        <span class="text-[10px] font-black uppercase tracking-[0.2em] text-black">Extraction Warnings</span>
        <div class="h-0.5 bg-black grow"></div>
      </div>
      
      <div class="grid grid-cols-1 gap-4">
        <div
          v-for="(insight, index) in zeroResultInsights"
          :key="index"
          class="flex items-start gap-4 p-5 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
          :class="{
             'bg-primary/5': insight.type !== 'error',
             'bg-red-50': insight.type === 'error',
          }"
        >
          <div class="size-10 shrink-0 flex items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            <AlertTriangle v-if="insight.type === 'error'" class="size-5 text-red-600" />
            <AlertCircle v-else class="size-5 text-black" />
          </div>
          <div class="flex flex-col gap-1 grow">
            <div class="flex justify-between items-start">
              <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{{ insight.source_id }}</span>
              <span class="text-[10px] font-black uppercase text-black/40">{{ formatDate(insight.timestamp) }}</span>
            </div>
            <p class="font-bold text-sm leading-tight text-black">{{ insight.message }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Partial Filtering Summary (Bottom Accordion) -->
    <div v-if="partialResultInsights.length" class="space-y-4">
      <Card class="border-2 border-black rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] overflow-hidden bg-white">
        <button 
          @click="isExpanded = !isExpanded"
          class="w-full text-left px-6 py-5 flex items-center justify-between hover:bg-muted/30 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="size-10 flex items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <Info class="size-5 text-black" />
            </div>
            <div>
              <h3 class="font-black text-sm uppercase tracking-tight">Detailed Extraction Analysis</h3>
              <p class="text-[10px] font-bold text-muted-foreground uppercase">{{ partialResultInsights.length }} entries recorded</p>
            </div>
          </div>
          <ChevronDown class="size-5 transition-transform duration-300" :class="{ 'rotate-180': isExpanded }" />
        </button>

        <div v-show="isExpanded" class="px-6 pb-6 animate-in slide-in-from-top-2 duration-300">
          <div class="border-2 border-black overflow-hidden">
            <Table>
              <TableHeader class="bg-black">
                <TableRow class="hover:bg-transparent border-black">
                  <TableHead class="text-white font-black uppercase text-[10px] h-10">Source</TableHead>
                  <TableHead class="text-white font-black uppercase text-[10px] h-10">Analysis Message</TableHead>
                  <TableHead class="text-white font-black uppercase text-[10px] h-10 text-right">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="(insight, index) in partialResultInsights" :key="index" class="border-black hover:bg-muted/50">
                  <TableCell class="font-black text-[10px] uppercase text-muted-foreground py-3">{{ insight.source_id }}</TableCell>
                  <TableCell class="font-bold text-xs py-3">{{ insight.message }}</TableCell>
                  <TableCell class="text-right text-[10px] font-black uppercase text-black/40 py-3">{{ formatDate(insight.timestamp) }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertTriangle, AlertCircle, Info, ChevronDown } from 'lucide-vue-next'
import { Card } from '@/components/ui/card'
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table'
import type { Insight } from '~/types/extraction'
import { computed, ref } from 'vue'

const props = defineProps<{
  insights?: Insight[]
}>()

const isExpanded = ref(false)
const hasInsights = computed(() => !!props.insights?.length)

// Determine if an insight represents a zero-result using heuristics
function isZeroResultInsight(insight: Insight): boolean {
  if (insight.type === 'error') return true

  const msg = (insight.message || '').toLowerCase()
  if (msg.includes('0 trends found')) return true
  if (msg.includes('no trends found')) return true
  if (msg.includes('no items')) return true
  if (msg.includes('none were suitable')) return true

  if (msg.includes('out of') && msg.includes('items from source')) return false
  if (msg.includes('posts filtered out')) return false
  if (msg.includes('posts were too old')) return false
  if (msg.includes('rapidapi_key not set')) return false

  return insight.type === 'warning'
}

const zeroResultInsights = computed(() => {
  return props.insights?.filter(isZeroResultInsight) || []
})

const partialResultInsights = computed(() => {
  return props.insights?.filter(i => !isZeroResultInsight(i)) || []
})

function formatDate(dateStr: string | null) {
  if (!dateStr) return 'Unknown'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false
  })
}
</script>
