<template>
  <div class="flex flex-wrap items-center gap-2">
    <Badge 
      variant="outline"
      class="font-black border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] px-2 py-0.5 rounded-none uppercase text-[10px] tracking-wider"
      :class="isLimitReached ? 'bg-primary text-primary-foreground' : 'bg-white text-black'"
    >
      {{ current }} / {{ isUnlimited ? '∞' : limit }} {{ type }}
    </Badge>
    <div v-if="showWarning && isLimitReached" class="text-[10px] text-destructive font-black uppercase flex items-center gap-1">
      <AlertCircle class="size-3" />
      <span>{{ warningMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'

const props = withDefaults(defineProps<{
  current: number;
  limit: number;
  type?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  showWarning?: boolean;
  warningMessage?: string;
}>(), {
  type: '',
  size: 'sm',
  showWarning: false,
  warningMessage: 'Limit reached.'
});

const isUnlimited = computed(() => props.limit === -1);
const isLimitReached = computed(() => !isUnlimited.value && props.current >= props.limit);
</script>
