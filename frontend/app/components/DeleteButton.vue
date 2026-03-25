<template>
  <Button
    variant="ghost"
    size="icon"
    :disabled="disabled || loading"
    class="relative group size-8 border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all hover:bg-red-500 hover:text-white hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none disabled:opacity-50 disabled:cursor-not-allowed"
    :title="title"
    @click="$emit('click', $event)"
  >
    <Loader2 v-if="loading" class="size-4 animate-spin" />
    <X v-else class="size-4 transition-transform group-hover:scale-110" />
  </Button>
</template>

<script setup lang="ts">
import { X, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

defineProps<{
  disabled?: boolean
  loading?: boolean
  title?: string
}>()

defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()
</script>
