<template>
  <div v-if="isOpen" class="fixed inset-0 z-100 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm cursor-pointer" @click="close"></div>

    <!-- Modal Content -->
    <div class="p-0 rounded-none border-2 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] bg-white w-full max-w-lg overflow-hidden relative z-10 animate-in fade-in zoom-in duration-200">
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
        <Button variant="ghost" size="icon" class="size-8 text-white hover:bg-white/10" @click="close">
          <X class="size-4" />
        </Button>
      </div>

      <!-- Modal Body -->
      <div class="p-8 space-y-8">
        <SchedulingForm
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
                <Button variant="neutral" class="flex-1 sm:flex-none border-2 border-black rounded-none uppercase font-black text-[10px] h-10 hover:bg-muted" @click="close">Close</Button>
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
  </div>
</template>

<script setup lang="ts">
import { Clock, X, Check, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useSettings } from '~/composables/useSettings'

const props = defineProps<{
  isFreeTier: boolean
}>()

const { isSaving, saveSettings } = useSettings()

const isOpen = ref(false)
const showSaved = ref(false)

async function onSave() {
  const success = await saveSettings()
  if (success) {
    showSaved.value = true
    setTimeout(() => { showSaved.value = false }, 2000)
  }
}

function handlePopState() {
  if (isOpen.value) {
    isOpen.value = false
  }
}

function show() {
  isOpen.value = true
  window.history.pushState({ modal: 'scheduler' }, '')
  window.addEventListener('popstate', handlePopState)
}

function close() {
  if (isOpen.value) {
    isOpen.value = false
    // If the modal was closed via UI, we need to sync history
    if (window.history.state?.modal === 'scheduler') {
      window.history.back()
    }
  }
  window.removeEventListener('popstate', handlePopState)
}

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopState)
})

defineExpose({
  show,
  close,
  showSuccess: () => {
    showSaved.value = true
    setTimeout(() => { showSaved.value = false }, 2000)
  }
})
</script>
