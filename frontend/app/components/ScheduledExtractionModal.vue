<template>
  <dialog id="scheduled_extraction_modal" ref="modalRef" class="modal modal-bottom sm:modal-middle" @close="onClose">
    <div class="modal-box p-0 overflow-hidden border border-base-300 shadow-2xl bg-base-100 rounded-2xl max-w-lg">
      <!-- Modal Header -->
      <div class="bg-linear-to-r from-primary/10 to-base-200 px-6 py-5 border-b border-base-300/50 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-primary/20 rounded-xl text-primary shadow-sm border border-primary/20">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-lg tracking-tight">Scheduled Extraction</h3>
            <p class="text-[10px] uppercase font-bold text-base-content/40 tracking-widest">Automation Settings</p>
          </div>
        </div>
        <form method="dialog">
          <button class="btn btn-sm btn-circle btn-ghost">✕</button>
        </form>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <SchedulingForm 
          v-model="fullSchedule"
          :is-free-tier="isFreeTier"
          :is-saving="isSaving"
          @save="onSave"
        >
          <template #actions>
            <!-- Modal Footer -->
            <div class="pt-6 mt-6 border-t border-base-300 flex items-center justify-between">
              <div v-if="showSaved" class="flex items-center gap-1.5 text-success animate-bounce">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span class="text-[10px] font-black uppercase tracking-widest">Settings Saved!</span>
              </div>
              <div v-else></div>
              
              <div class="flex gap-3">
                <form method="dialog">
                  <button class="btn btn-ghost btn-sm text-xs font-bold uppercase tracking-widest px-6">Close</button>
                </form>
                <button v-if="!isFreeTier" class="btn btn-primary btn-sm px-8 text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/20" 
                  :class="{ 'btn-disabled': isSaving }" 
                  @click="onSave"
                >
                  <span v-if="isSaving" class="loading loading-spinner loading-xs"></span>
                  {{ isSaving ? 'Saving' : 'Save Schedule' }}
                </button>
              </div>
            </div>
          </template>
        </SchedulingForm>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
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
  time_window_hours: props.schedule.time_window_hours || props.settings.time_window_hours,
  max_trends_per_source: props.schedule.max_trends_per_source || props.settings.max_trends_per_source
})

const showSaved = ref(false)

// Sync when props change
watch(() => props.schedule, (newVal) => { 
  fullSchedule.value = { 
    ...newVal,
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
