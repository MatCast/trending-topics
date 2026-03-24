<template>
  <div class="max-w-2xl mx-auto space-y-8 pb-12">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-black tracking-tight mb-2">Settings</h1>
      <p class="text-base-content/50 text-sm font-medium">Manage your extraction preferences and automated schedules.</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-20">
      <div class="flex flex-col items-center gap-4">
        <span class="loading loading-spinner loading-lg text-primary"></span>
        <span class="text-xs font-bold uppercase tracking-widest text-base-content/30 italic">Loading Profile...</span>
      </div>
    </div>

    <div v-else class="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      <!-- Extraction Parameters Section -->
      <section class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </div>
          <h2 class="text-xs font-black uppercase tracking-[0.2em] text-base-content/50">Data Parameters</h2>
          <div class="h-px bg-base-300 grow ml-2 opacity-50"></div>
        </div>
        
        <ExtractionSettings 
          v-model="settings" 
          :saving="isSaving"
          @change="saveSettings"
        />
        <p class="text-[10px] text-base-content/40 font-medium px-1 leading-relaxed">
          These settings define the standard scope for all background and manual searches. 
          Changes are applied instantly to your profile.
        </p>
      </section>

      <!-- Schedule Section -->
      <section class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary border border-primary/20">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-xs font-black uppercase tracking-[0.2em] text-base-content/50">Automation Schedule</h2>
          <div class="h-px bg-base-300 grow ml-2 opacity-50"></div>
        </div>

        <div v-if="isFreeTier" class="bg-warning/5 border border-warning/20 rounded-2xl p-6 flex gap-5">
           <div class="p-3 bg-warning/20 rounded-xl text-warning shadow-sm self-start">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
           </div>
           <div>
             <h3 class="font-bold text-base text-base-content">Scheduling is a Pro Feature</h3>
             <p class="text-sm opacity-60 mt-2 leading-relaxed">Automate your trend discovery. Enable hourly, daily, or weekly extractions to have fresh insights waiting for you every morning.</p>
             <button class="btn btn-sm btn-warning mt-4 px-6 rounded-lg opacity-50 cursor-not-allowed">Upgrade to Pro</button>
           </div>
        </div>

        <div v-else class="bg-base-100 border border-base-300 rounded-2xl shadow-sm overflow-hidden transition-all duration-500 hover:shadow-md">
          <div class="p-6 space-y-6">
            <!-- Schedule Type Selection -->
            <div class="form-control">
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <button 
                  v-for="opt in scheduleOptions" 
                   :key="opt.value"
                   class="btn btn-sm grow rounded-lg border-base-300"
                   :class="schedule.type === opt.value ? 'btn-primary shadow-lg shadow-primary/20' : 'btn-ghost bg-base-200/50'"
                   @click="schedule.type = opt.value"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- Contextual Settings Container -->
            <div class="transition-all duration-300 ease-out" v-if="schedule.type !== 'manual'">
              <div class="bg-base-200/50 rounded-xl p-5 border border-base-300/50 space-y-6">
                
                <!-- Hourly interval -->
                <div v-if="schedule.type === 'hourly'" class="form-control">
                  <label class="label pt-0 pb-2"><span class="label-text-alt font-black uppercase tracking-widest opacity-40">Interval (Hours)</span></label>
                  <div class="flex items-center gap-6">
                    <input v-model.number="schedule.interval_hours" type="range" min="1" max="24" class="range range-primary range-xs grow" />
                    <span class="badge badge-primary font-mono font-bold py-3 px-3">Every {{ schedule.interval_hours }}h</span>
                  </div>
                </div>

                <!-- Daily/Weekly hour -->
                <div v-if="schedule.type === 'daily' || schedule.type === 'weekly'" class="form-control">
                  <label class="label pt-0 pb-2"><span class="label-text-alt font-black uppercase tracking-widest opacity-40">Execution Time (UTC)</span></label>
                  <select class="select select-bordered select-sm w-full font-mono text-xs rounded-lg" v-model="schedule.hour_of_day">
                    <option v-for="h in 24" :key="h - 1" :value="h - 1">{{ String(h - 1).padStart(2, '0') }}:00 Universal Time</option>
                  </select>
                </div>

                <!-- Weekly day -->
                <div v-if="schedule.type === 'weekly'" class="form-control">
                  <label class="label pt-0 pb-2"><span class="label-text-alt font-black uppercase tracking-widest opacity-40">Frequency Day</span></label>
                  <div class="grid grid-cols-7 gap-1.5">
                    <button 
                      v-for="(day, idx) in days" 
                       :key="idx" 
                       class="btn btn-sm rounded-lg"
                       :class="schedule.day_of_week === idx ? 'btn-primary shadow-md' : 'btn-ghost bg-base-100'"
                       @click="schedule.day_of_week = idx"
                    >
                      {{ day }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="bg-base-200/50 p-4 border-t border-base-300 flex items-center justify-between">
            <div v-if="showSuccess" class="flex items-center gap-2 text-success px-2 animate-in fade-in zoom-in">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span class="text-[10px] font-black uppercase tracking-tighter">Schedule Synced</span>
            </div>
            <div v-else></div>
            <button class="btn btn-primary btn-sm px-8 rounded-lg text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/10" 
              :class="{ 'btn-disabled': isSaving }" 
              @click="saveSettings"
            >
              <span v-if="isSaving" class="loading loading-spinner loading-xs"></span>
              {{ isSaving ? 'Saving' : 'Apply Schedule' }}
            </button>
          </div>
        </div>
      </section>

      <!-- Advanced Section -->
      <section class="space-y-4 opacity-80 pt-4">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-base-300 flex items-center justify-center text-base-content border border-base-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h2 class="text-xs font-black uppercase tracking-[0.2em] text-base-content/50">Connectivity</h2>
          <div class="h-px bg-base-300 grow ml-2 opacity-50"></div>
        </div>

        <div class="bg-base-100 border border-base-300 rounded-2xl p-6">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 class="font-bold text-sm">Reddit Fetch Method</h3>
              <p class="text-xs opacity-50 mt-1">Experimental: Choose how data is retrieved from Reddit.</p>
            </div>
            <select class="select select-sm select-bordered rounded-lg font-bold text-xs" v-model="settings.reddit_fetch_method" @change="saveSettings">
               <option value="rapidapi">RapidAPI (Recommended)</option>
               <option value="direct">Direct (Fallback)</option>
            </select>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()
const { isFreeTier, fetchProfile } = useUser()

const isLoading = ref(true)
const isSaving = ref(false)
const showSuccess = ref(false)

const scheduleOptions = [
  { label: 'Manual', value: 'manual' },
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' }
]

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const settings = ref<any>({
  time_window_hours: 3,
  max_trends_per_source: 3,
  reddit_fetch_method: 'rapidapi'
})

const schedule = ref<any>({
  type: 'manual',
  interval_hours: 3,
  hour_of_day: 9,
  day_of_week: 0,
})

async function fetchSettings() {
  isLoading.value = true
  try {
    const data = await apiFetch<any>('/api/settings')
    settings.value = {
      time_window_hours: data.time_window_hours || 3,
      max_trends_per_source: data.max_trends_per_source || 3,
      reddit_fetch_method: data.reddit_fetch_method || 'rapidapi'
    }
    schedule.value = data.schedule || { type: 'manual', interval_hours: 3, hour_of_day: 9, day_of_week: 0 }
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  } finally {
    isLoading.value = false
  }
}

async function saveSettings() {
  if (isSaving.value) return
  isSaving.value = true
  showSuccess.value = false
  try {
    await apiFetch('/api/settings', {
      method: 'PUT',
      body: {
        ...settings.value,
        schedule: schedule.value,
      },
    })
    // Sync global profile
    await fetchProfile()
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 2000)
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}

// Separate watcher for settings to auto-save
watch(
  () => [settings.value.time_window_hours, settings.value.max_trends_per_source],
  () => { if (!isLoading.value) saveSettings() },
  { deep: true }
)

onMounted(() => fetchSettings())
</script>
