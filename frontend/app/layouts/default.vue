<script setup lang="ts">
import 'vue-sonner/style.css'
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar'
import { Toaster } from '@/components/ui/sonner'

const { isAuthenticated } = useAuth()
</script>

<template>
  <SidebarProvider>
    <!-- Navigation Sidebar (Only for authenticated users) -->
    <AppSidebar v-if="isAuthenticated" />

    <SidebarInset class="bg-background min-h-svh flex flex-col">
      <!-- Header bar (Only for authenticated users) -->
      <header 
        v-if="isAuthenticated" 
        class="flex h-14 shrink-0 items-center justify-between gap-2 border-b-2 border-border bg-background px-4 sticky top-0 z-40"
      >
        <div class="flex items-center gap-2">
          <SidebarTrigger class="-ml-1 border-2 border-black hover:bg-primary transition-all p-1" />
        </div>
        
        <!-- Optional: Action buttons or search can go here -->
      </header>

      <!-- Main page content -->
      <main 
        :class="[
          'flex-1 p-4 md:p-6 lg:p-8 max-w-7xl mx-auto w-full transition-all duration-300',
          !isAuthenticated ? 'flex items-center justify-center' : ''
        ]"
      >
        <slot />
      </main>
    </SidebarInset>

    <!-- Global Sonner Toasts -->
    <Toaster 
      position="top-right"
      :toast-options="{
        style: {
          borderRadius: '0px',
          border: '2px solid black',
          boxShadow: '4px 4px 0px 0px rgba(0,0,0,1)',
          background: 'white',
          color: 'black',
          fontWeight: 'bold',
        }
      }"
    />
  </SidebarProvider>
</template>

<style>
/* Global breadcrumb/transition overrides if needed */
.page-enter-active,
.page-leave-active {
  transition: all 0.2s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
