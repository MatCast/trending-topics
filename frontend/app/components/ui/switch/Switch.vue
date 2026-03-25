<script setup lang="ts">
import type { SwitchRootEmits, SwitchRootProps } from 'reka-ui'
import { type HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import {
  SwitchRoot,
  SwitchThumb,
  useForwardPropsEmits,
} from 'reka-ui'
import { cn } from '@/utils/cn'

const props = withDefaults(defineProps<SwitchRootProps & { 
  class?: HTMLAttributes['class']
  size?: 'default' | 'sm'
}>(), {
  size: 'default'
})

const emits = defineEmits<SwitchRootEmits>()

const delegatedProps = reactiveOmit(props, 'class', 'size')

const forwarded = useForwardPropsEmits(delegatedProps, emits)
</script>

<template>
  <SwitchRoot
    v-bind="forwarded"
    :class="cn(
      'peer inline-flex shrink-0 cursor-pointer items-center rounded-none border-2 border-black transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-zinc-200',
      size === 'default'
        ? 'h-7 w-14 px-1.5 shadow-[4px_4px_0px_0px_black]'
        : 'h-5 w-10 px-1 shadow-[2px_2px_0px_0px_black]',
      props.class,
    )"
  >
    <SwitchThumb
      :class="cn(
        'pointer-events-none block rounded-none border-2 border-black bg-white ring-0 transition-transform duration-200 shadow-[1px_1px_0px_0px_black]',
        size === 'default'
          ? 'h-4 w-4 data-[state=checked]:translate-x-6 data-[state=unchecked]:translate-x-0'
          : 'h-3 w-3 data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0'
      )"
    >
      <slot name="thumb" />
    </SwitchThumb>
  </SwitchRoot>
</template>
