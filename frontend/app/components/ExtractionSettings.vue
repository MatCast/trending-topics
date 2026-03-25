<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
      <!-- Time Window -->
      <Card 
        class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-none hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer group bg-white"
        @click="focusTime"
      >
        <CardHeader class="pb-2">
          <div class="flex justify-between items-center">
            <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Search Window</span>
            <ArrowRight class="size-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent>
          <div class="flex items-baseline gap-2">
            <input
              ref="timeInput"
              v-model.number="localSettings.time_window_hours"
              type="number"
              min="1"
              max="168"
              class="bg-transparent border-none p-0 focus:ring-0 font-black text-4xl w-24 text-black selection:bg-primary/30"
              @change="onSettingsChange"
            />
            <span class="text-xs font-black uppercase text-muted-foreground">Hours</span>
          </div>
        </CardContent>
      </Card>

      <!-- Max Results -->
      <Card 
        class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-none hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer group bg-white"
        @click="focusMax"
      >
        <CardHeader class="pb-2">
          <div class="flex justify-between items-center">
            <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Results Limit</span>
            <ArrowRight class="size-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </CardHeader>
        <CardContent>
          <div class="flex items-baseline gap-2">
            <input
              ref="maxInput"
              v-model.number="localSettings.max_trends_per_source"
              type="number"
              min="1"
              max="50"
              class="bg-transparent border-none p-0 focus:ring-0 font-black text-4xl w-24 text-black selection:bg-primary/30"
              @change="onSettingsChange"
            />
            <span class="text-xs font-black uppercase text-muted-foreground">Per Source</span>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Saving Indicator -->
    <transition enter-active-class="transition duration-200" enter-from-class="opacity-0 translate-x-2" enter-to-class="opacity-100 translate-x-0">
      <div v-if="saving" class="flex items-center gap-2 justify-end px-2">
        <Loader2 class="size-3 animate-spin text-primary" />
        <span class="text-[10px] font-black uppercase tracking-widest text-primary italic">Syncing changes...</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ArrowRight, Loader2 } from 'lucide-vue-next'

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
