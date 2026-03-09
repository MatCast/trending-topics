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
      <!-- Global Keywords -->
      <div class="card bg-base-100 shadow-xl border border-base-300">
        <div class="card-body">
          <h2 class="card-title">Global Keywords</h2>
          <p class="text-base-content/60 text-sm mb-3">Keywords used for filtering trends across keyword-based sources.</p>

          <div class="join w-full">
            <input
              v-model="newKeyword"
              type="text"
              placeholder="Add a keyword..."
              class="input input-bordered join-item flex-1"
              @keyup.enter="addKeyword"
            />
            <button class="btn btn-primary join-item" @click="addKeyword">Add</button>
          </div>

          <div class="flex flex-wrap gap-2 mt-3">
            <div
              v-for="(kw, idx) in settings.global_keywords"
              :key="idx"
              class="badge badge-lg badge-primary gap-2"
            >
              {{ kw }}
              <button @click="removeKeyword(idx)">✕</button>
            </div>
            <span v-if="!settings.global_keywords?.length" class="text-base-content/40 text-sm">No keywords</span>
          </div>
        </div>
      </div>

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
  global_keywords: [],
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
      global_keywords: data.global_keywords || [],
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

function addKeyword() {
  const kw = newKeyword.value.trim()
  if (kw && !settings.value.global_keywords.includes(kw)) {
    settings.value.global_keywords.push(kw)
    newKeyword.value = ''
  }
}

function removeKeyword(idx: number) {
  settings.value.global_keywords.splice(idx, 1)
}

async function saveSettings() {
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
    setTimeout(() => { showSuccess.value = false }, 3000)
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    isSaving.value = false
  }
}

onMounted(() => fetchSettings())
</script>
