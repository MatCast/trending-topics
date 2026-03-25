<script setup lang="ts">
import type { Component, HTMLAttributes } from "vue";
import { reactiveOmit } from "@vueuse/core";
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import SidebarMenuButtonChild from "@/components/ui/sidebar/SidebarMenuButtonChild.vue";
import { useSidebar } from "@/components/ui/sidebar/utils";

defineOptions({
    inheritAttrs: false,
});

const props = withDefaults(
    defineProps<{
        as?: any;
        asChild?: boolean;
        variant?: "default" | "outline";
        size?: "default" | "sm" | "lg";
        isActive?: boolean;
        class?: HTMLAttributes["class"];
        tooltip?: string | Component;
    }>(),
    {
        as: "button",
        variant: "default",
        size: "default",
    },
);

const { isMobile, state } = useSidebar();

const delegatedProps = reactiveOmit(props, "tooltip");
</script>

<template>
  <SidebarMenuButtonChild
    v-if="!tooltip"
    v-bind="{ ...delegatedProps, ...$attrs }"
  >
    <slot />
  </SidebarMenuButtonChild>

  <Tooltip v-else>
    <TooltipTrigger as-child>
      <SidebarMenuButtonChild v-bind="{ ...delegatedProps, ...$attrs }">
        <slot />
      </SidebarMenuButtonChild>
    </TooltipTrigger>
    <TooltipContent
      side="right"
      align="center"
      :hidden="state !== 'collapsed' || isMobile"
    >
      <template v-if="typeof tooltip === 'string'">
        {{ tooltip }}
      </template>
      <component :is="tooltip" v-else />
    </TooltipContent>
  </Tooltip>
</template>
