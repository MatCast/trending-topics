<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-primary/5 p-5 rounded-xl border border-primary/10 shadow-xs transition-all duration-300 hover:shadow-md">
    <div class="flex items-center gap-4">
      <div class="p-2.5 bg-primary/10 rounded-xl text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-black uppercase tracking-widest text-base-content/80">Activate Automation</span>
          <div v-if="modelValue" class="badge badge-success badge-xs animate-pulse"></div>
        </div>
        <p v-if="lastRunAt" class="text-[10px] opacity-50 mt-1">
          Last ran: <span class="font-mono">{{ formatDate(lastRunAt) }}</span>
        </p>
        <p v-else class="text-[10px] opacity-50 mt-1 italic font-medium">Never ran yet</p>
      </div>
    </div>
    <div class="flex items-center gap-4">
      <span 
        class="text-[10px] font-bold uppercase tracking-widest transition-colors duration-300" 
        :class="modelValue ? 'text-success' : 'text-base-content/30'"
      >
        {{ modelValue ? 'Active' : 'Disabled' }}
      </span>
      <input 
        type="checkbox" 
        :checked="modelValue"
        @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked); $emit('change')"
        class="toggle toggle-primary"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useFormatDate } from '~/composables/useFormatDate'

const props = defineProps<{
  modelValue: boolean
  lastRunAt?: string | Date
}>()

defineEmits(['update:modelValue', 'change'])

const { formatDate } = useFormatDate()
</script>
