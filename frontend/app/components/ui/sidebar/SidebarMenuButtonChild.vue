<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { Primitive } from "reka-ui";
import { cn } from "@/utils";
import { sidebarMenuButtonVariants } from "./index";

const props = withDefaults(
    defineProps<{
        as?: any;
        asChild?: boolean;
        variant?: "default" | "outline";
        size?: "default" | "sm" | "lg";
        isActive?: boolean;
        class?: HTMLAttributes["class"];
    }>(),
    {
        as: "button",
        variant: "default",
        size: "default",
    },
);
</script>

<template>
  <Primitive
    data-sidebar="menu-button"
    :as="as"
    :as-child="asChild"
    :data-size="size"
    :data-active="isActive"
    :class="cn(sidebarMenuButtonVariants({ size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
