<template>
  <dialog id="scheduled_extraction_modal" ref="modalRef" class="modal bg-black/50 backdrop-blur-sm" @close="onClose">
    <div class="modal-box p-0 rounded-none border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-white max-w-lg overflow-hidden">
      <!-- Modal Header -->
      <div class="bg-black px-6 py-5 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="size-10 flex items-center justify-center border-2 border-white bg-white/10 text-white">
            <Clock class="size-6" />
          </div>
          <div>
            <h3 class="font-black text-lg uppercase tracking-tight text-white">Scheduled Extraction</h3>
            <p class="text-[10px] uppercase font-black text-white/50 tracking-widest">Automation Settings</p>
          </div>
        </div>
        <form method="dialog">
          <Button variant="ghost" size="icon" class="size-8 text-white hover:bg-white/10">
            <X class="size-4" />
          </Button>
        </form>
      </div>

      <!-- Modal Body -->
      <div class="p-8 space-y-8">
        <SchedulingForm 
          v-model="fullSchedule"
          :is-free-tier="isFreeTier"
          :is-saving="isSaving"
          @save="onSave"
        >
          <template #actions>
            <!-- Modal Footer -->
            <div class="pt-8 border-t-2 border-black flex flex-col sm:flex-row items-center justify-between gap-4">
              <div class="min-h-5">
                <transition enter-active-class="transition duration-300" enter-from-class="opacity-0 -translate-x-2" enter-to-class="opacity-100 translate-x-0">
                  <div v-if="showSaved" class="flex items-center gap-2 text-black">
                      <Check class="size-4" />
                      <span class="text-[10px] font-black uppercase tracking-widest">Settings Synchronized</span>
                  </div>
                </transition>
              </div>
              
              <div class="flex gap-3 w-full sm:w-auto">
                <form method="dialog" class="flex-1 sm:flex-none">
                  <Button variant="outline" class="w-full border-2 border-black rounded-none uppercase font-black text-[10px] h-10 hover:bg-muted">Close</Button>
                </form>
                <Button 
                  v-if="!isFreeTier" 
                  class="flex-1 sm:flex-none border-2 border-black rounded-none uppercase font-black text-[10px] h-10 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all" 
                  :disabled="isSaving" 
                  @click="onSave"
                >
                  <Loader2 v-if="isSaving" class="size-4 animate-spin mr-2" />
                  {{ isSaving ? 'Saving' : 'Save Schedule' }}
                </Button>
              </div>
            </div>
          </template>
        </SchedulingForm>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { Clock, X, Check, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const props = defineProps<{
  settings: {
    time_window_hours: number
    max_trends_per_source: number
  }
  schedule: {
    active?: boolean
    type: string
    interval_hours: number
    hour_of_day: number
    day_of_week: number
    time_window_hours?: number
    max_trends_per_source?: number
    last_run_at?: string
  }
  isFreeTier: boolean
  isSaving: boolean
}>()

const emit = defineEmits(['save', 'update-settings'])

const fullSchedule = ref({ 
  ...props.schedule,
  active: props.schedule?.active ?? false,
  time_window_hours: props.schedule.time_window_hours || props.settings.time_window_hours,
  max_trends_per_source: props.schedule.max_trends_per_source || props.settings.max_trends_per_source
})

const showSaved = ref(false)

// Sync when props change
watch(() => props.schedule, (newVal) => { 
  fullSchedule.value = { 
    ...newVal,
    active: newVal?.active ?? false,
    time_window_hours: newVal.time_window_hours || props.settings.time_window_hours,
    max_trends_per_source: newVal.max_trends_per_source || props.settings.max_trends_per_source
  }
}, { deep: true })

const modalRef = ref<HTMLDialogElement | null>(null)
let isHandlingPop = false

function handlePopState() {
  if (modalRef.value?.open) {
    isHandlingPop = true
    modalRef.value.close()
    isHandlingPop = false
  }
}

function onSave() {
  emit('save', {
    schedule: { ...fullSchedule.value }
  })
}

function onClose() {
  window.removeEventListener('popstate', handlePopState)
  if (!isHandlingPop && window.history.state?.modal === 'scheduler') {
    window.history.back()
  }
}

defineExpose({
  show: () => {
    if (modalRef.value) {
      modalRef.value.showModal()
      window.history.pushState({ modal: 'scheduler' }, '')
      window.addEventListener('popstate', handlePopState)
    }
  },
  showSuccess: () => {
    showSaved.value = true
    setTimeout(() => { showSaved.value = false }, 2000)
  }
})
</script>
