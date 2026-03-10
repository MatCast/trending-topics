<template>
  <div class="min-h-screen bg-base-200" data-theme="dark">
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

      <!-- Navigation links (only when authenticated) -->
      <div v-if="isAuthenticated" class="flex-none gap-2">
        <NuxtLink to="/" class="btn btn-ghost btn-sm">Dashboard</NuxtLink>
        <NuxtLink to="/sources" class="btn btn-ghost btn-sm">Sources</NuxtLink>
        <NuxtLink to="/keywords" class="btn btn-ghost btn-sm">Keywords</NuxtLink>
        <NuxtLink to="/settings" class="btn btn-ghost btn-sm">Settings</NuxtLink>

        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
            <div class="w-8 rounded-full">
              <img v-if="user?.photoURL" :src="user.photoURL" :alt="user.displayName || 'User'" />
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
  </div>
</template>

<script setup lang="ts">
const { user, isAuthenticated, signOut } = useAuth()

async function handleSignOut() {
  await signOut()
  navigateTo('/login')
}
</script>
