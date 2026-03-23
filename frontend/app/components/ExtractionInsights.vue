<template>
  <div v-if="hasInsights" class="extraction-insights">
    <!-- Zero Result Summary (Top Alerts) -->
    <div v-if="zeroResultInsights.length" class="mb-6">
      <h2 class="text-xl font-semibold mb-3">Extraction Warnings</h2>
      <div class="space-y-3">
        <div
          v-for="(insight, index) in zeroResultInsights"
          :key="index"
          class="alert shadow-lg"
          :class="{
             'alert-error': insight.type === 'error',
             'alert-warning': insight.type !== 'error', // all zero results use yellow/orange warning scheme
          }"
        >
          <svg v-if="insight.type === 'error'" xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <div class="flex flex-col gap-0.5">
            <span class="text-xs font-bold uppercase opacity-60">{{ insight.source_id }}</span>
            <span>{{ insight.message }}</span>
          </div>
          <span class="text-xs text-base-content/60 ml-auto">{{ formatDate(insight.timestamp) }}</span>
        </div>
      </div>
    </div>

    <!-- Partial Filtering Summary (Bottom Accordion) -->
    <div v-if="partialResultInsights.length" class="mb-6">
      <div class="collapse collapse-arrow bg-base-200 shadow-sm border border-base-300">
        <input type="checkbox" /> 
        <div class="collapse-title text-lg font-medium flex items-center justify-between gap-2 pr-12">
          <div class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current h-6 w-6 opacity-60"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span class="truncate">Detailed Extraction Analysis</span>
          </div>
          <div class="badge badge-info badge-sm shrink-0">
            {{ partialResultInsights.length }}<span class="hidden sm:inline ml-1">entries</span>
          </div>
        </div>
        <div class="collapse-content overflow-x-auto">
          <table class="table table-sm w-full">
            <thead>
              <tr>
                <th>Source</th>
                <th>Message</th>
                <th class="text-right">Time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(insight, index) in partialResultInsights" :key="index" class="hover border-base-300/50">
                <td class="font-bold opacity-70 whitespace-nowrap">{{ insight.source_id }}</td>
                <td>{{ insight.message }}</td>
                <td class="text-right whitespace-nowrap opacity-60 text-xs">{{ formatDate(insight.timestamp) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Insight } from '~/types/extraction'
import { computed } from 'vue'

const props = defineProps<{
  insights?: Insight[]
}>()

const hasInsights = computed(() => !!props.insights?.length)

// Determine if an insight represents a zero-result using heuristics (backward compatibility)
function isZeroResultInsight(insight: Insight): boolean {
  if (insight.type === 'error') return true

  const msg = (insight.message || '').toLowerCase()
  if (msg.includes('0 trends found')) return true
  if (msg.includes('no trends found')) return true
  if (msg.includes('no items')) return true
  if (msg.includes('none were suitable')) return true

  // Conversely, if the message signifies partial extraction success...
  if (msg.includes('out of') && msg.includes('items from source')) return false
  if (msg.includes('posts filtered out')) return false
  if (msg.includes('posts were too old')) return false
  if (msg.includes('rapidapi_key not set')) return false

  // Fallback map: Assume warnings are for 0-results, infos are for partial results based on latest backend logic.
  return insight.type === 'warning'
}

/**
 * Filter for insights linked to sources that returned ZERO results.
 */
const zeroResultInsights = computed(() => {
  return props.insights?.filter(isZeroResultInsight) || []
})

/**
 * Filter for insights linked to sources that successfully returned results,
 * but had some items filtered out.
 */
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
