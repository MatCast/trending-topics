<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- Time Window -->
      <div 
        class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 hover:border-primary/30 transition-all cursor-pointer group"
        @click="focusTime"
      >
        <label class="label pt-0 pb-1 flex justify-between">
          <span class="label-text-alt font-black uppercase tracking-widest opacity-50">Window</span>
          <span class="text-[10px] font-bold text-primary opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
        </label>
        <div class="flex items-end gap-2 px-1">
          <input
            ref="timeInput"
            v-model.number="localSettings.time_window_hours"
            type="number"
            min="1"
            max="168"
            class="bg-transparent border-none p-0 focus:ring-0 font-mono text-2xl font-bold w-20 text-primary"
            @change="onSettingsChange"
          />
          <span class="text-xs font-bold opacity-30 pb-1.5 uppercase">Hours Back</span>
        </div>
      </div>

      <!-- Max Results -->
      <div 
        class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 hover:border-primary/30 transition-all cursor-pointer group"
        @click="focusMax"
      >
        <label class="label pt-0 pb-1 flex justify-between">
          <span class="label-text-alt font-black uppercase tracking-widest opacity-50">Limit</span>
          <span class="text-[10px] font-bold text-primary opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
        </label>
        <div class="flex items-end gap-2 px-1">
          <input
            ref="maxInput"
            v-model.number="localSettings.max_trends_per_source"
            type="number"
            min="1"
            max="50"
            class="bg-transparent border-none p-0 focus:ring-0 font-mono text-2xl font-bold w-20 text-primary"
            @change="onSettingsChange"
          />
          <span class="text-xs font-bold opacity-30 pb-1.5 uppercase">Results / Source</span>
        </div>
      </div>
    </div>

    <!-- Saving Indicator -->
    <div v-if="saving" class="flex items-center gap-2 justify-end px-2">
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
