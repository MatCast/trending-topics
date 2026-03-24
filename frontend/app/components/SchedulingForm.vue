<template>
  <div class="space-y-6">
    <!-- Unified Scheduler Toggle -->
    <SchedulerToggle 
      v-if="!isFreeTier"
      v-model="schedule.active"
      :last-run-at="schedule.last_run_at"
      @change="$emit('save')"
    />

    <!-- Conditional Content -->
    <div v-if="schedule.active || isFreeTier" class="space-y-8 animate-in fade-in zoom-in duration-500">
      <!-- Extraction Parameters Section -->
      <section class="space-y-3">
        <div class="flex items-center gap-2">
          <span class="text-[11px] font-bold uppercase tracking-widest text-primary/70">1. Data Parameters (Scheduled)</span>
          <div class="h-px bg-primary/10 grow"></div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
           <!-- Clickable input containers -->
           <div 
             class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 hover:border-primary/30 transition-all cursor-pointer group"
             @click="windowInput?.focus()"
           >
             <label class="label pt-0 pb-1 flex justify-between">
               <span class="label-text-alt font-black uppercase tracking-widest opacity-40">Window</span>
               <span class="text-[10px] font-bold text-primary opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
             </label>
             <div class="flex items-end gap-2 px-1">
               <input 
                 ref="windowInput"
                 type="number" 
                 v-model.number="schedule.time_window_hours" 
                 class="bg-transparent border-none p-0 focus:ring-0 font-mono text-2xl font-bold w-20 text-primary" 
                 min="1" max="168" 
               />
               <span class="text-xs font-bold opacity-30 pb-1.5">HOURS BACK</span>
             </div>
           </div>

           <div 
             class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 hover:border-primary/30 transition-all cursor-pointer group"
             @click="maxInput?.focus()"
           >
             <label class="label pt-0 pb-1 flex justify-between">
               <span class="label-text-alt font-black uppercase tracking-widest opacity-40">Limit</span>
               <span class="text-[10px] font-bold text-primary opacity-0 group-hover:opacity-100 transition-opacity">Edit</span>
             </label>
             <div class="flex items-end gap-2 px-1">
               <input 
                 ref="maxInput"
                 type="number" 
                 v-model.number="schedule.max_trends_per_source" 
                 class="bg-transparent border-none p-0 focus:ring-0 font-mono text-2xl font-bold w-20 text-primary" 
                 min="1" max="50" 
               />
               <span class="text-xs font-bold opacity-30 pb-1.5">RESULTS / SOURCE</span>
             </div>
           </div>
        </div>
        <p class="text-[10px] text-base-content/50 italic px-1">These parameters only affect automated runs.</p>
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
             <p class="text-xs opacity-70 mt-1 leading-relaxed">Automated scheduling is only available for Pro users.</p>
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
                class="join-item btn btn-sm grow border-base-300 font-bold"
                :class="schedule.type === opt.value ? 'btn-primary' : 'btn-ghost bg-base-200/50'"
                @click="schedule.type = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- Conditional Contextual Params -->
          <div class="transition-all duration-300 ease-out" v-if="schedule.type !== 'manual'">
            <div class="bg-base-200/50 rounded-xl p-4 border border-base-300/50 space-y-4">
              
              <!-- Hourly interval -->
              <div v-if="schedule.type === 'hourly'" class="form-control">
                <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Every N hours</span></label>
                <div class="flex items-center gap-4">
                  <input v-model.number="schedule.interval_hours" type="range" min="1" max="24" class="range range-primary range-xs grow" />
                  <span class="badge badge-primary font-mono font-bold">{{ schedule.interval_hours }}h</span>
                </div>
              </div>

              <!-- Daily/Weekly hour -->
              <div v-if="schedule.type === 'daily' || schedule.type === 'weekly'" class="form-control">
                <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Time of day (UTC)</span></label>
                <select class="select select-sm select-bordered w-full font-mono text-xs" v-model="schedule.hour_of_day">
                  <option v-for="h in 24" :key="h - 1" :value="h - 1">{{ String(h - 1).padStart(2, '0') }}:00 UTC</option>
                </select>
              </div>

              <!-- Weekly day -->
              <div v-if="schedule.type === 'weekly'" class="form-control">
                <label class="label pt-0 pb-1.5"><span class="label-text text-xs font-semibold">Day of week</span></label>
                <div class="grid grid-cols-7 gap-1">
                  <button 
                    v-for="(day, idx) in days" 
                    :key="idx" 
                    class="btn btn-xs rounded-md font-bold"
                    :class="schedule.day_of_week === idx ? 'btn-primary shadow-sm' : 'btn-ghost glass'"
                    @click="schedule.day_of_week = idx"
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

    <!-- Deactivated State -->
    <div v-else class="py-16 text-center space-y-4 opacity-30 animate-in fade-in slide-in-from-top-4 duration-500">
       <div class="flex justify-center">
          <div class="p-4 bg-base-300 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
            </svg>
          </div>
       </div>
       <div>
         <h4 class="text-xs font-black uppercase tracking-[0.2em]">Scheduler Deactivated</h4>
         <p class="text-[10px] mt-1 font-medium">Turn on the toggle to configure automated runs</p>
       </div>
    </div>

    <!-- Actions Area (Slotted for custom buttons or standard Save) -->
    <slot name="actions"></slot>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  isFreeTier: boolean
  isSaving: boolean
}>()

const schedule = defineModel<any>({ required: true })

defineEmits(['save'])

const windowInput = ref<HTMLInputElement | null>(null)
const maxInput = ref<HTMLInputElement | null>(null)

const scheduleOptions = [
  { label: 'Manual', value: 'manual' },
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' }
]

const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
</script>
