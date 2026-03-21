<template>
  <div class="flex flex-wrap items-center gap-2">
    <span 
      class="badge font-bold truncate max-w-full"
      :class="[sizeClass, isLimitReached ? 'badge-warning' : 'badge-ghost']"
    >
      {{ current }} / {{ isUnlimited ? '∞' : limit }} {{ type }}
    </span>
    <div v-if="showWarning && isLimitReached" class="text-xs text-warning flex items-center gap-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span>{{ warningMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const sizeClass = computed(() => {
  if (props.size === 'xs') return 'badge-xs';
  if (props.size === 'sm') return 'badge-sm';
  if (props.size === 'lg') return 'badge-lg';
  return '';
});
</script>
