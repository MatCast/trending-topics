<template>
  <div class="max-w-2xl mx-auto space-y-12 pb-24 animate-in fade-in duration-500">
    <!-- Header -->
    <div class="space-y-2">
      <h1 class="text-4xl font-black uppercase tracking-tight text-black">System Settings</h1>
      <p class="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">Calibration & Automation Protocols</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-24 gap-4">
      <div class="size-16 flex items-center justify-center border-4 border-black bg-white shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] animate-bounce">
        <Loader2 class="size-8 text-black animate-spin" />
      </div>
      <p class="text-[10px] font-black uppercase tracking-widest text-black">Accessing Profile...</p>
    </div>

    <div v-else class="space-y-12">

      <!-- Extraction Parameters Section -->
      <section class="space-y-6">
        <div class="flex items-center gap-4">
          <div class="size-10 border-4 border-black bg-primary flex items-center justify-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <SlidersHorizontal class="size-5 text-black" />
          </div>
          <h2 class="text-xl font-black uppercase tracking-tight text-black">Data Parameters</h2>
        </div>

        <Card class="border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none bg-white p-8">
          <ExtractionSettings v-model="settings" :saving="isSaving" @change="handleSaveSettings" />
          <div class="mt-8 pt-6 border-t-2 border-black border-dashed">
            <p class="text-[10px] font-black text-muted-foreground uppercase leading-relaxed">
              These settings define the standard scope for all background and manual searches.
              Execution parameters are synched instantly.
            </p>
          </div>
        </Card>
      </section>

      <!-- Schedule Section -->
      <section class="space-y-6">
        <div class="flex items-center gap-4">
          <div class="size-10 border-4 border-black bg-primary flex items-center justify-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <Clock class="size-5 text-black" />
          </div>
          <h2 class="text-xl font-black uppercase tracking-tight text-black">Automation Schedule</h2>
        </div>

        <div v-if="isFreeTier">
          <Card class="border-4 border-black bg-yellow-400 p-8 shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none">
            <div class="flex flex-col md:flex-row items-start gap-6">
              <div class="p-4 border-4 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] shrink-0">
                <Lock class="size-8 text-black" />
              </div>
              <div class="space-y-4">
                <h3 class="text-2xl font-black uppercase tracking-tight text-black">Scheduling Locked</h3>
                <p class="text-xs font-black uppercase leading-relaxed text-black/80">
                  Automate your trend discovery. Enable hourly, daily, or weekly extractions to have fresh insights waiting for you.
                </p>
                <Button
                  class="h-12 border-4 border-black bg-black text-white rounded-none shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] uppercase font-black px-8 opacity-50 cursor-not-allowed">
                  Upgrade Required
                </Button>
              </div>
            </div>
          </Card>
        </div>

        <Card v-else class="border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none bg-white overflow-hidden">
          <div class="p-8">
            <SchedulingForm v-model="schedule" :is-free-tier="false" :is-saving="isSaving" @save="handleSaveSettings">
              <template #actions>
                <div v-if="schedule.active" class="pt-8 mt-8 border-t-4 border-black border-double flex items-center justify-between">
                  <div v-if="showSuccess" class="flex items-center gap-2 text-black bg-primary px-4 py-2 border-2 border-black animate-in fade-in zoom-in">
                    <Check class="size-4" />
                    <span class="text-[10px] font-black uppercase">Schedule Synced</span>
                  </div>
                  <div v-else></div>
                  <Button
                    class="h-14 border-4 border-black bg-primary text-black rounded-none shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] uppercase font-black px-10 hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all disabled:opacity-50"
                    :disabled="isSaving" @click="handleSaveSettings">
                    <Loader2 v-if="isSaving" class="size-5 mr-2 animate-spin" />
                    {{ isSaving ? 'Executing...' : 'Apply Schedule' }}
                  </Button>
                </div>
              </template>
            </SchedulingForm>
          </div>
        </Card>
      </section>

      <!-- Advanced Section -->
      <section class="space-y-6">
        <div class="flex items-center gap-4">
          <div class="size-10 border-4 border-black bg-muted flex items-center justify-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
            <ShieldCheck class="size-5 text-black" />
          </div>
          <h2 class="text-xl font-black uppercase tracking-tight text-black">Deployment Protocols</h2>
        </div>

        <Card class="border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] rounded-none bg-white p-8">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div class="space-y-1">
              <h3 class="text-lg font-black uppercase tracking-tight text-black">Reddit Access Method</h3>
              <p class="text-[10px] font-black uppercase text-muted-foreground">Experiment selecting data retrieval pipeline.</p>
            </div>

            <div class="relative w-full sm:w-64">
              <select
                class="w-full h-12 bg-white border-4 border-black rounded-none appearance-none px-4 font-black uppercase text-xs focus:ring-0 focus:border-black cursor-pointer shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] text-black"
                v-model="settings.reddit_fetch_method" @change="handleSaveSettings">
                <option value="rapidapi">RapidAPI (Recommended)</option>
                <option value="direct">Direct Integration</option>
              </select>
              <ChevronDown class="absolute right-4 top-1/2 -translate-y-1/2 size-4 pointer-events-none text-black" />
            </div>
          </div>
        </Card>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SlidersHorizontal, Clock, Lock, Check, Loader2, ShieldCheck, ChevronDown } from 'lucide-vue-next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useSettings } from '~/composables/useSettings'

definePageMeta({ layout: 'default' })

const { isFreeTier } = useUser()
const {
  settings,
  schedule,
  isLoading,
  isSaving,
  fetchSettings,
  saveSettings
} = useSettings()

const showSuccess = ref(false)

async function handleSaveSettings() {
  const success = await saveSettings()
  if (success) {
    showSuccess.value = true
    setTimeout(() => { showSuccess.value = false }, 2000)
  }
}

const isReady = ref(false)

onMounted(async () => {
  await fetchSettings()
  nextTick(() => { isReady.value = true }) // arm AFTER fetch + render
})

watch(
  () => [settings.value.time_window_hours, settings.value.max_trends_per_source],
  () => { if (isReady.value) handleSaveSettings() }
)
</script>
