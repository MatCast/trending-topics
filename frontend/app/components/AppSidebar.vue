<script setup lang="ts">
import { Home, Globe, Hash, Settings, LogOut, TrendingUp } from 'lucide-vue-next'
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup,
  SidebarGroupContent, SidebarGroupLabel, SidebarHeader,
  SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail,
} from '@/components/ui/sidebar'
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const { user, signOut } = useAuth()

const navItems = [
  { title: 'Dashboard', url: '/', icon: Home },
  { title: 'Sources', url: '/sources', icon: Globe },
  { title: 'Keywords', url: '/keywords', icon: Hash },
]

async function handleSignOut() {
  await signOut()
  navigateTo('/login')
}
</script>

<template>
  <Sidebar collapsible="offcanvas">
    <!-- Header: App logo/title -->
    <SidebarHeader class="border-b-2 border-border p-4">
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <NuxtLink to="/" class="flex items-center gap-3">
              <div class="flex aspect-square size-8 items-center justify-center border-2 border-black bg-primary shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <TrendingUp class="size-5" />
              </div>
              <span class="font-black text-xl tracking-tight">Trend Finder</span>
            </NuxtLink>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <!-- Navigation -->
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel class="px-4 pt-6 pb-2 text-xs font-black uppercase tracking-widest text-muted-foreground">Navigation</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu class="px-2 space-y-1">
            <SidebarMenuItem v-for="item in navItems" :key="item.title">
              <SidebarMenuButton
                as-child
                class="hover:bg-primary hover:text-primary-foreground border-2 border-transparent hover:border-black transition-all"
              >
                <NuxtLink :to="item.url" class="flex items-center gap-3 py-2 px-3">
                  <component :is="item.icon" class="size-5" />
                  <span class="font-bold">{{ item.title }}</span>
                </NuxtLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <!-- Footer: User profile + sign out -->
    <SidebarFooter class="border-t-2 border-border p-2">
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <SidebarMenuButton class="w-full justify-start gap-3 h-12 border-2 border-transparent hover:border-black hover:bg-muted transition-all">
                <div class="flex aspect-square size-8 items-center justify-center border-2 border-black bg-secondary font-black text-sm">
                  {{ (user?.displayName || user?.email || '?').charAt(0).toUpperCase() }}
                </div>
                <div class="flex flex-col text-left overflow-hidden">
                  <span class="truncate text-xs font-black">{{ user?.displayName || 'User' }}</span>
                  <span class="truncate text-[10px] text-muted-foreground">{{ user?.email }}</span>
                </div>
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              side="top"
              align="start"
              class="w-56 border-2 border-black rounded-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
            >
              <DropdownMenuItem as-child class="cursor-pointer font-bold focus:bg-primary focus:text-primary-foreground">
                <NuxtLink to="/settings" class="flex items-center w-full">
                  <Settings class="size-4 mr-2" />
                  Settings
                </NuxtLink>
              </DropdownMenuItem>
              <DropdownMenuItem
                @click="handleSignOut"
                class="cursor-pointer font-bold text-destructive focus:bg-destructive focus:text-destructive-foreground"
              >
                <LogOut class="size-4 mr-2" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>

    <SidebarRail />
  </Sidebar>
</template>
