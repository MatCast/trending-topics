<script setup lang="ts">
import { type HTMLAttributes } from 'vue'
import { useVModel, reactiveOmit } from '@vueuse/core'
import {
  SwitchRoot,
  SwitchThumb,
} from 'reka-ui'
import { cn } from '@/utils/cn'

const props = withDefaults(defineProps<{
  checked?: boolean
  defaultChecked?: boolean
  disabled?: boolean
  required?: boolean
  name?: string
  value?: string
  id?: string
  class?: HTMLAttributes['class']
  size?: 'default' | 'sm'
}>(), {
  size: 'default'
})

const emits = defineEmits<{
  'update:checked': [payload: boolean]
}>()

const modelValue = useVModel(props, 'checked', emits)

const delegatedProps = reactiveOmit(props, 'checked', 'class', 'size')
</script>

<template>
  <SwitchRoot
    v-bind="delegatedProps"
    v-model="modelValue"
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
