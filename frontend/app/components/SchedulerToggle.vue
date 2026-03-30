<template>
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6 bg-white p-6 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all">
    <div class="flex items-center gap-4">
      <div class="size-12 flex items-center justify-center border-2 border-black bg-primary/20 shadow-[2px_2px_0_0_rgba(0,0,0,1)]">
        <Zap class="size-6 text-black" />
      </div>
      <div>
        <div class="flex items-center gap-3">
          <span class="text-xs font-black uppercase tracking-widest text-black">Activate Automation</span>
          <div v-if="active" class="size-2 bg-primary border border-black animate-pulse"></div>
        </div>
        <p v-if="schedule.last_run_at" class="text-[10px] font-bold text-muted-foreground mt-1 uppercase tracking-tight">
          Last ran: <span class="font-black text-black">{{ formatDate(schedule.last_run_at) }}</span>
        </p>
        <p v-else class="text-[10px] font-bold text-muted-foreground mt-1 uppercase tracking-tight italic">Never ran yet</p>
      </div>
    </div>
    <div class="flex items-center gap-4 pt-4 sm:pt-0 border-t-2 border-black/5 sm:border-0">
      <span
        class="text-[10px] font-black uppercase tracking-widest transition-colors"
        :class="active ? 'text-black' : 'text-muted-foreground'"
      >
        {{ active ? 'Active' : 'Disabled' }}
      </span>
      <Loader2 v-if="isSaving" class="size-4 animate-spin text-muted-foreground" />
      <Switch
        v-else
        :checked="active"
        :disabled="isSaving"
        @update:checked="toggle"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Zap, Loader2 } from 'lucide-vue-next'
import { Switch } from '@/components/ui/switch'
import { useFormatDate } from '~/composables/useFormatDate'
import { useScheduleToggle } from '~/composables/useScheduleToggle'
import { useSettings } from '~/composables/useSettings'

const { active, isSaving, toggle } = useScheduleToggle()
const { schedule } = useSettings()
const { formatDate } = useFormatDate()
</script>
