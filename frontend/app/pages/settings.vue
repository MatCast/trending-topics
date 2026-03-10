<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <h1 class="text-2xl font-bold">Settings</h1>
      <p class="text-base-content/60 text-sm">Configure your global preferences and schedule.</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>

    <div v-else class="space-y-6">


      <!-- Extraction Preferences -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Extraction Preferences</h2>

          <div class="grid gap-4 mt-2">
            <div class="form-control">
              <label class="label"><span class="label-text">Time window (hours)</span></label>
              <input v-model.number="settings.time_window_hours" type="number" min="1" max="168" class="input input-bordered" />
              <label class="label"><span class="label-text-alt">How far back to look for trending content</span></label>
            </div>

            <div class="form-control">
              <label class="label"><span class="label-text">Max results per source</span></label>
              <input v-model.number="settings.max_trends_per_source" type="number" min="1" max="50" class="input input-bordered" />
            </div>
          </div>
        </div>
      </div>

      <!-- Schedule -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Schedule</h2>
          <p class="text-base-content/60 text-sm mb-3">Automatically run extractions on a schedule.</p>

          <div class="form-control">
            <label class="label"><span class="label-text">Schedule Type</span></label>
            <select class="select select-bordered" v-model="schedule.type">
              <option value="manual">Manual only</option>
              <option value="hourly">Every N hours</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <!-- Hourly interval -->
          <div v-if="schedule.type === 'hourly'" class="form-control mt-3">
            <label class="label"><span class="label-text">Every N hours</span></label>
            <input v-model.number="schedule.interval_hours" type="number" min="1" max="24" class="input input-bordered" />
          </div>

          <!-- Daily/Weekly hour -->
          <div v-if="schedule.type === 'daily' || schedule.type === 'weekly'" class="form-control mt-3">
            <label class="label"><span class="label-text">Hour of day (UTC)</span></label>
            <select class="select select-bordered" v-model="schedule.hour_of_day">
              <option v-for="h in 24" :key="h-1" :value="h-1">{{ String(h-1).padStart(2, '0') }}:00</option>
            </select>
          </div>

          <!-- Weekly day -->
          <div v-if="schedule.type === 'weekly'" class="form-control mt-3">
            <label class="label"><span class="label-text">Day of week</span></label>
            <select class="select select-bordered" v-model="schedule.day_of_week">
              <option :value="0">Monday</option>
              <option :value="1">Tuesday</option>
              <option :value="2">Wednesday</option>
              <option :value="3">Thursday</option>
              <option :value="4">Friday</option>
              <option :value="5">Saturday</option>
              <option :value="6">Sunday</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end">
        <button
          class="btn btn-primary"
          :class="{ 'btn-disabled': isSaving }"
          @click="saveSettings"
        >
          <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
          {{ isSaving ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>

      <!-- Success alert -->
      <div v-if="showSuccess" class="alert alert-success">
        <span>Settings saved successfully!</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()

const isLoading = ref(true)
const isSaving = ref(false)
const showSuccess = ref(false)
const newKeyword = ref('')

const settings = ref<any>({
  time_window_hours: 3,
  max_trends_per_source: 3,
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
    }
    schedule.value = data.schedule || { type: 'manual' }
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  } finally {
    isLoading.value = false
  }
}

// Auto-save watchers
watch(
  () => [settings.value.time_window_hours, settings.value.max_trends_per_source],
  () => { if (!isLoading.value) saveSettings() },
  { deep: true }
)

watch(
  () => schedule.value,
  () => { if (!isLoading.value) saveSettings() },
  { deep: true }
)



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
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 2000)
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => fetchSettings())
</script>
