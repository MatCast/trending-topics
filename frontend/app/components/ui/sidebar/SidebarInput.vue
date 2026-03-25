<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { cn } from '@/utils';
import { Input } from "@/components/ui/input";

const props = defineProps<{
    class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <Input
    data-sidebar="input"
    :class="cn('bg-secondary-background h-8 w-full shadow-none', props.class)"
  >
    <slot />
  </Input>
</template>
