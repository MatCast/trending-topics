<template>
  <dialog id="scheduled_extraction_modal" class="modal modal-bottom sm:modal-middle" @close="onClose">
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
      <div class="p-6 space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
        
        <!-- Extraction Parameters Section -->
        <section class="space-y-3">
          <div class="flex items-center gap-2">
            <span class="text-[11px] font-bold uppercase tracking-widest text-primary/70">1. Data Parameters</span>
            <div class="h-px bg-primary/10 grow"></div>
          </div>
          <ExtractionSettings 
            v-model="localSettings" 
            :saving="isSaving"
            @change="syncSettings"
          />
          <p class="text-[10px] text-base-content/50 italic px-1">These parameters apply to both manual and scheduled runs.</p>
        </section>

        <!-- Schedule Section -->
        <section class="space-y-4">
          <div class="flex items-center gap-2">
            <span class="text-[11px] font-bold uppercase tracking-widest text-primary/70">2. Run Schedule</span>
            <div class="h-px bg-primary/10 grow"></div>
          </div>

          <!-- Free Tier Notice -->
          <div v-if="isFreeTier" class="bg-warning/10 border border-warning/20 rounded-xl p-4 flex gap-4">
             <div class="text-warning mt-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
             </div>
             <div>
               <h4 class="font-bold text-xs">Scheduling Locked</h4>
               <p class="text-xs opacity-70 mt-1 leading-relaxed">Automated scheduling is only available for Pro users. Upgrade to enable automatic trend tracking.</p>
               <button class="btn btn-xs btn-warning mt-2" disabled>Compare Plans</button>
             </div>
          </div>

          <div v-else class="space-y-5">
            <!-- Schedule Type -->
            <div class="form-control">
              <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-bold text-base-content/60 uppercase">Run Frequency</span></label>
              <div class="join w-full">
                <button 
                  v-for="opt in scheduleOptions" 
                  :key="opt.value"
                  class="join-item btn btn-sm grow border-base-300"
                  :class="localSchedule.type === opt.value ? 'btn-primary' : 'btn-ghost bg-base-200/50'"
                  @click="localSchedule.type = opt.value"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Conditional Contextual Params -->
            <div class="transition-all duration-300 ease-out" v-if="localSchedule.type !== 'manual'">
              <div class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 space-y-4">
                
                <!-- Hourly interval -->
                <div v-if="localSchedule.type === 'hourly'" class="form-control">
                  <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Every N hours</span></label>
                  <div class="flex items-center gap-4">
                    <input v-model.number="localSchedule.interval_hours" type="range" min="1" max="24" class="range range-primary range-xs grow" />
                    <span class="badge badge-primary font-mono font-bold">{{ localSchedule.interval_hours }}h</span>
                  </div>
                </div>

                <!-- Daily/Weekly hour -->
                <div v-if="localSchedule.type === 'daily' || localSchedule.type === 'weekly'" class="form-control">
                  <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Time of day (UTC)</span></label>
                  <select class="select select-sm select-bordered w-full font-mono text-xs" v-model="localSchedule.hour_of_day">
                    <option v-for="h in 24" :key="h - 1" :value="h - 1">{{ String(h - 1).padStart(2, '0') }}:00 UTC</option>
                  </select>
                </div>

                <!-- Weekly day -->
                <div v-if="localSchedule.type === 'weekly'" class="form-control">
                  <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Day of week</span></label>
                  <div class="grid grid-cols-7 gap-1">
                    <button 
                      v-for="(day, idx) in days" 
                      :key="idx" 
                      class="btn btn-xs rounded-md"
                      :class="localSchedule.day_of_week === idx ? 'btn-primary shadow-sm' : 'btn-ghost glass'"
                      @click="localSchedule.day_of_week = idx"
                    >
                      {{ day }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Modal Footer -->
      <div class="p-6 bg-base-200/30 border-t border-base-300 flex items-center justify-between">
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
    type: string
    interval_hours: number
    hour_of_day: number
    day_of_week: number
  }
  isFreeTier: boolean
  isSaving: boolean
}>()

const emit = defineEmits(['save', 'update-settings'])

const localSettings = ref({ ...props.settings })
const localSchedule = ref({ ...props.schedule })
const showSaved = ref(false)

const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
const scheduleOptions = [
  { label: 'Manual', value: 'manual' },
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' }
]

// Sync when props change
watch(() => props.settings, (newVal) => { localSettings.value = { ...newVal } }, { deep: true })
watch(() => props.schedule, (newVal) => { localSchedule.value = { ...newVal } }, { deep: true })

function syncSettings() {
  emit('update-settings', { ...localSettings.value })
}

function onSave() {
  emit('save', {
    settings: localSettings.value,
    schedule: localSchedule.value
  })
}

function onClose() {
  // Handled by method=dialog mostly
}

defineExpose({
  showSuccess: () => {
    showSaved.value = true
    setTimeout(() => { showSaved.value = false }, 2000)
  }
})
</script>
