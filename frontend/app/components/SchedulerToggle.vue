<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6 bg-white p-6 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all">
    <div class="flex items-center gap-4">
      <div class="size-12 flex items-center justify-center border-2 border-black bg-primary/20 shadow-[2px_2px_0_0_rgba(0,0,0,1)]">
        <Zap class="size-6 text-black" />
      </div>
      <div>
        <div class="flex items-center gap-3">
          <span class="text-xs font-black uppercase tracking-widest text-black">Activate Automation</span>
          <div v-if="modelValue" class="size-2 bg-primary border border-black animate-pulse"></div>
        </div>
        <p v-if="lastRunAt" class="text-[10px] font-bold text-muted-foreground mt-1 uppercase tracking-tight">
          Last ran: <span class="font-black text-black">{{ formatDate(lastRunAt) }}</span>
        </p>
        <p v-else class="text-[10px] font-bold text-muted-foreground mt-1 uppercase tracking-tight italic">Never ran yet</p>
      </div>
    </div>
    <div class="flex items-center gap-4 pt-4 sm:pt-0 border-t-2 border-black/5 sm:border-0">
      <span 
        class="text-[10px] font-black uppercase tracking-widest transition-colors" 
        :class="modelValue ? 'text-black' : 'text-muted-foreground'"
      >
        {{ modelValue ? 'Active' : 'Disabled' }}
      </span>
      <Switch 
        :checked="modelValue"
        @update:checked="(val: boolean) => { $emit('update:modelValue', val); $emit('change') }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Zap } from 'lucide-vue-next'
import { Switch } from '@/components/ui/switch'
import { useFormatDate } from '~/composables/useFormatDate'

const props = defineProps<{
  modelValue: boolean
  lastRunAt?: string | Date
}>()

defineEmits(['update:modelValue', 'change'])

const { formatDate } = useFormatDate()
</script>
