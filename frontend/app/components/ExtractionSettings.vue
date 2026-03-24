<template>
  <div class="flex flex-wrap items-center gap-4 py-2 px-3 bg-base-100/50 backdrop-blur-sm rounded-xl border border-base-300 shadow-inner">
    <!-- Time Window -->
    <div 
      class="flex items-center gap-2 px-3 py-1 bg-base-100 rounded-lg border border-base-200 shadow-sm transition-all hover:border-primary/30 cursor-pointer"
      @click="focusTime"
    >
      <div class="flex items-center gap-1.5 min-w-[140px]">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-xs font-bold uppercase tracking-wider text-base-content/60">In the Past</span>
      </div>
      <div class="flex items-center gap-2">
        <input
          ref="timeInput"
          v-model.number="localSettings.time_window_hours"
          type="number"
          min="1"
          max="168"
          class="input input-ghost input-xs w-16 text-center font-mono font-bold text-primary focus:bg-transparent px-0 focus:outline-none"
          @change="onSettingsChange"
        />
        <span class="text-[10px] font-bold text-base-content/40 uppercase">Hours</span>
      </div>
    </div>

    <!-- Max Results -->
    <div 
      class="flex items-center gap-2 px-3 py-1 bg-base-100 rounded-lg border border-base-200 shadow-sm transition-all hover:border-primary/30 cursor-pointer"
      @click="focusMax"
    >
      <div class="flex items-center gap-1.5 min-w-[140px]">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16" />
        </svg>
        <span class="text-xs font-bold uppercase tracking-wider text-base-content/60">Max Results</span>
      </div>
      <div class="flex items-center gap-2">
        <input
          ref="maxInput"
          v-model.number="localSettings.max_trends_per_source"
          type="number"
          min="1"
          max="50"
          class="input input-ghost input-xs w-16 text-center font-mono font-bold text-primary focus:bg-transparent px-0 focus:outline-none"
          @change="onSettingsChange"
        />
        <span class="text-[10px] font-bold text-base-content/40 uppercase">Sources</span>
      </div>
    </div>

    <div v-if="saving" class="flex items-center gap-2 ml-auto pr-2">
      <span class="loading loading-spinner loading-xs text-primary/50"></span>
      <span class="text-[10px] font-bold uppercase tracking-widest text-base-content/30 italic">Saving...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: {
    time_window_hours: number
    max_trends_per_source: number
  }
  saving?: boolean
}>()

const emit = defineEmits(['update:modelValue', 'change'])

const localSettings = ref({ ...props.modelValue })
const timeInput = ref<HTMLInputElement | null>(null)
const maxInput = ref<HTMLInputElement | null>(null)

// Sync when prop changes
watch(() => props.modelValue, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(localSettings.value)) {
    localSettings.value = { ...newVal }
  }
}, { deep: true })

function onSettingsChange() {
  emit('update:modelValue', { ...localSettings.value })
  emit('change', { ...localSettings.value })
}

function focusTime() {
  timeInput.value?.focus()
  timeInput.value?.select()
}

function focusMax() {
  maxInput.value?.focus()
  maxInput.value?.select()
}
</script>

<style scoped>
/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
