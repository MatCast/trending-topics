<template>
  <div class="hero min-h-[calc(100vh-5rem)]">
    <div class="hero-content text-center">
      <div class="max-w-md">
        <!-- Logo & Branding -->
        <div class="mb-8">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary/10 mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <h1 class="text-4xl font-bold mb-3">Trend Finder</h1>
          <p class="text-base-content/60 text-lg">Discover trending news topics.</p>
        </div>

        <!-- Features -->
        <div class="flex flex-col gap-3 mb-8 text-left">
          <div class="flex items-center gap-3 px-4 py-3 bg-base-100 rounded-xl border border-base-300">
            <span class="text-xl">🔥</span>
            <span class="text-sm">Real-time trends from Reddit, Hacker News & Bluesky</span>
          </div>
          <div class="flex items-center gap-3 px-4 py-3 bg-base-100 rounded-xl border border-base-300">
            <span class="text-xl">📊</span>
            <span class="text-sm">Engagement-based scoring & filtering</span>
          </div>
          <div class="flex items-center gap-3 px-4 py-3 bg-base-100 rounded-xl border border-base-300">
            <span class="text-xl">📋</span>
            <span class="text-sm">Export to CSV for easy analysis</span>
          </div>
        </div>

        <!-- Sign In Button -->
        <button
          class="btn btn-primary btn-lg gap-3 w-full"
          :class="{ 'btn-disabled': isSigningIn }"
          @click="handleSignIn"
        >
          <span v-if="isSigningIn" class="loading loading-spinner"></span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24">
            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {{ isSigningIn ? 'Signing in...' : 'Continue with Google' }}
        </button>

        <!-- Error Message (Hidden while signing in) -->
        <div v-if="errorMessage && !isSigningIn" class="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl text-error text-xs font-medium animate-in fade-in duration-200">
          {{ errorMessage }}
        </div>

        <!-- Manual Reset (for slow Firebase popup detection) -->
        <div v-if="isSigningIn && showReset" class="mt-4 p-3 bg-base-200/50 rounded-xl border border-base-300/50 animate-in fade-in slide-in-from-top-1 duration-500">
          <p class="text-[10px] uppercase font-bold tracking-wider text-base-content/40 mb-2">Still waiting for the popup?</p>
          <button @click="forceReset" class="btn btn-xs btn-outline btn-ghost w-full hover:bg-base-300">
            Click here to reset
          </button>
        </div>

        <p class="text-xs text-base-content/40 mt-4">
          By signing in, you agree to our terms of service.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { signInWithGoogle, isAuthenticated } = useAuth()
const { apiFetch } = useApi()
const isSigningIn = ref(false)
const errorMessage = ref('')
const showReset = ref(false)
let resetTimer: any = null
let currentAttemptId = 0

// Redirect if already authenticated
watch(isAuthenticated, async (val) => {
  if (val) {
    // Check if user has sources configured
    try {
      const sources = await apiFetch<any[]>('/api/sources')
      if (!sources || sources.length === 0) {
        navigateTo('/onboarding')
      } else {
        navigateTo('/')
      }
    } catch {
      navigateTo('/onboarding')
    }
  }
}, { immediate: true })

async function handleSignIn() {
  const attemptId = ++currentAttemptId
  isSigningIn.value = true
  errorMessage.value = ''
  showReset.value = false

  // Force Vue to flush DOM updates so the error message visibly disappears 
  // and the spinner shows up before any instant Firebase failures.
  await nextTick()
  await new Promise(r => setTimeout(r, 100))

  // Show reset link after 3 seconds if still loading
  resetTimer = setTimeout(() => {
    if (attemptId === currentAttemptId) {
      showReset.value = true
    }
  }, 3000)

  try {
    await signInWithGoogle()
  } catch (error: any) {
    if (attemptId !== currentAttemptId) return // Ignore stale promise results
    console.error('Sign in error:', error)
    if (error.code === 'auth/popup-closed-by-user') {
      errorMessage.value = 'Sign-in window was closed. Please try again.'
    } else if (error.code === 'auth/cancelled-popup-request') {
      errorMessage.value = 'A sign-in window is already open. Please find and close it to try again.'
    } else if (error.code === 'auth/popup-blocked') {
      errorMessage.value = 'Sign-in popup was blocked. Please allow popups for this site.'
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    if (attemptId === currentAttemptId) {
      isSigningIn.value = false
      clearTimeout(resetTimer)
    }
  }
}

function forceReset() {
  currentAttemptId++ // Invalidate any pending promises
  isSigningIn.value = false
  showReset.value = false
  clearTimeout(resetTimer)
  errorMessage.value = 'Login attempt was manually reset. You can try again.'
}
</script>
