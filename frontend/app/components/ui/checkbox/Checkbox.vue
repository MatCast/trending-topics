<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { useVModel, reactiveOmit } from '@vueuse/core'
import { Check } from 'lucide-vue-next'
import { CheckboxIndicator, CheckboxRoot } from 'reka-ui'
import { cn } from '@/utils'

const props = withDefaults(defineProps<{
  checked?: boolean | 'indeterminate'
  defaultChecked?: boolean
  disabled?: boolean
  required?: boolean
  name?: string
  value?: string
  id?: string
  class?: HTMLAttributes['class']
}>(), {})

const emits = defineEmits<{
  'update:checked': [payload: boolean | 'indeterminate']
}>()

const modelValue = useVModel(props, 'checked', emits)

const delegatedProps = reactiveOmit(props, 'checked', 'class')
</script>

<template>
  <CheckboxRoot
    v-bind="delegatedProps"
    v-model="modelValue"
    :class="
      cn(
        'peer size-4 shrink-0 outline-2 outline-border ring-offset-white focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-black focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-main data-[state=checked]:text-white cursor-pointer',
        props.class
      )
    "
  >
    <CheckboxIndicator class="flex items-center justify-center text-current">
      <slot>
        <Check class="size-4 text-main-foreground" />
      </slot>
    </CheckboxIndicator>
  </CheckboxRoot>
</template>
