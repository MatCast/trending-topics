<template>
  <div class="min-h-screen bg-base-200 pb-20 md:pb-0" data-theme="dark">
    <!-- Navbar -->
    <div class="navbar bg-base-100 shadow-lg border-b border-base-300 sticky top-0 z-50">
      <div class="flex-1">
        <NuxtLink to="/" class="btn btn-ghost text-xl font-bold gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Trend Finder
        </NuxtLink>
      </div>

      <!-- Navigation links (Authenticated) -->
      <div v-if="isAuthenticated" class="flex-none gap-2">
        <!-- Desktop Links -->
        <div class="hidden md:flex gap-2 mr-2">
          <NuxtLink to="/" class="btn btn-ghost btn-sm" active-class="btn-active">Dashboard</NuxtLink>
          <NuxtLink to="/sources" class="btn btn-ghost btn-sm" active-class="btn-active">Sources</NuxtLink>
          <NuxtLink to="/keywords" class="btn btn-ghost btn-sm" active-class="btn-active">Keywords</NuxtLink>
          <NuxtLink to="/settings" class="btn btn-ghost btn-sm" active-class="btn-active">Settings</NuxtLink>
        </div>

        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
            <div class="w-8 rounded-full">
              <img v-if="user?.photoURL" :src="user?.photoURL" :alt="user?.displayName || 'User'" />
              <div v-else class="bg-primary text-primary-content flex items-center justify-center w-full h-full rounded-full text-sm font-bold">
                {{ (user?.displayName || user?.email || '?')[0].toUpperCase() }}
              </div>
            </div>
          </div>
          <ul tabindex="0" class="menu menu-sm dropdown-content bg-base-100 rounded-box z-[1] mt-3 w-52 p-2 shadow-lg border border-base-300">
            <li class="menu-title">
              <span class="text-xs opacity-60">{{ user?.email }}</span>
            </li>
            <li><a @click="handleSignOut">Sign out</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <main class="container mx-auto px-4 py-6 max-w-7xl">
      <slot />
    </main>

    <!-- Mobile Bottom Navigation (Dock) -->
    <div v-if="isAuthenticated" class="dock md:hidden bg-base-100 border-t border-base-300 z-40 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
      <NuxtLink to="/" class="text-base-content/60" exact-active-class="dock-active bg-primary/10 text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
        <span class="dock-label text-[10px]">Home</span>
      </NuxtLink>
      <NuxtLink to="/sources" class="text-base-content/60" active-class="dock-active bg-primary/10 text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
        <span class="dock-label text-[10px]">Sources</span>
      </NuxtLink>
      <NuxtLink to="/keywords" class="text-base-content/60" active-class="dock-active bg-primary/10 text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" /></svg>
        <span class="dock-label text-[10px]">Keywords</span>
      </NuxtLink>
      <NuxtLink to="/settings" class="text-base-content/60" active-class="dock-active bg-primary/10 text-primary">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        <span class="dock-label text-[10px]">Settings</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, isAuthenticated, signOut } = useAuth()

async function handleSignOut() {
  await signOut()
  navigateTo('/login')
}
</script>
