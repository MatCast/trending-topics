<template>
  <div class="min-h-screen flex items-center justify-center p-6 bg-white animate-in fade-in duration-500">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo & Branding -->
      <div class="text-center space-y-4">
        <div class="inline-flex items-center justify-center size-24 border-4 border-black bg-primary shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] -rotate-6 mb-4">
          <TrendingUp class="size-12 text-black" />
        </div>
        <h1 class="text-5xl font-black uppercase tracking-tighter">Trend Finder</h1>
        <p class="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground">Pulse of the Internet</p>
      </div>

      <!-- Main Login Card -->
      <Card class="border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] rounded-none overflow-hidden">
        <div class="bg-black p-4">
          <h2 class="text-lg font-black uppercase text-white tracking-widest text-center">Authentication Required</h2>
        </div>

        <div class="p-8 space-y-8">
          <!-- Features -->
          <div class="space-y-3">
             <div
               v-for="(feature, idx) in features"
               :key="idx"
               class="flex items-center gap-4 p-4 border-2 border-black bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none"
             >
               <span class="text-2xl">{{ feature.icon }}</span>
               <span class="text-xs font-black uppercase tracking-tight leading-tight">{{ feature.text }}</span>
             </div>
          </div>

          <div class="space-y-4">
            <!-- Sign In Button -->
            <Button
              class="h-16 w-full gap-4 border-4 border-black bg-primary text-black rounded-none shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-lg hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all group disabled:opacity-50"
              :disabled="isSigningIn"
              @click="handleSignIn"
            >
              <Loader2 v-if="isSigningIn" class="size-6 animate-spin" />
              <div v-else class="size-6 flex items-center justify-center bg-white border-2 border-black group-hover:bg-black group-hover:text-white transition-colors">
                 <svg class="size-4 fill-current" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                 </svg>
              </div>
              {{ isSigningIn ? 'Processing...' : 'Sign in with Google' }}
            </Button>

            <!-- Error Message -->
            <div
              v-if="errorMessage && !isSigningIn"
              class="p-4 bg-red-400 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] animate-in slide-in-from-top-2"
            >
              <div class="flex items-center gap-3">
                <AlertCircle class="size-5 text-black shrink-0" />
                <p class="text-[10px] font-black uppercase text-black leading-tight">{{ errorMessage }}</p>
              </div>
            </div>

            <!-- Manual Reset -->
            <div
              v-if="isSigningIn && showReset"
              class="p-4 border-2 border-black border-dashed bg-muted/20 animate-in fade-in"
            >
              <p class="text-[8px] font-black uppercase tracking-widest text-muted-foreground mb-3 text-center">Stall detected in authorization popup</p>
              <Button
                variant="outline"
                size="sm"
                class="w-full border-2 border-black rounded-none uppercase font-black text-[10px] h-8 bg-white"
                @click="forceReset"
              >
                Force Session Reset
              </Button>
            </div>
          </div>
        </div>

        <div class="bg-muted p-4 border-t-4 border-black">
          <p class="text-[8px] font-bold text-center uppercase tracking-widest text-muted-foreground">
            By proceeding, you adhere to the deployment protocols.
          </p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TrendingUp, Loader2, AlertCircle } from 'lucide-vue-next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

definePageMeta({ layout: 'default' })

const { signInWithGoogle, isAuthenticated } = useAuth()
const { apiFetch } = useApi()
const isSigningIn = ref(false)
const errorMessage = ref('')
const showReset = ref(false)
let resetTimer: any = null
let currentAttemptId = 0

const features = [
  { icon: '🔥', text: 'Real-time intelligence from Reddit, HN & Bluesky' },
  { icon: '📊', text: 'Deep engagement scoring & pattern analysis' },
  { icon: '📋', text: 'Universal export protocols (CSV/JSON)' }
]

// Redirect if already authenticated
watch(isAuthenticated, async (val) => {
  if (val) {
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

  await nextTick()
  await new Promise(r => setTimeout(r, 100))

  resetTimer = setTimeout(() => {
    if (attemptId === currentAttemptId) {
      showReset.value = true
    }
  }, 3000)

  try {
    await signInWithGoogle()
  } catch (error: any) {
    if (attemptId !== currentAttemptId) return
    console.error('Sign in error:', error)
    if (error.code === 'auth/popup-closed-by-user') {
      errorMessage.value = 'Authorization aborted by user.'
    } else if (error.code === 'auth/cancelled-popup-request') {
      errorMessage.value = 'Active request detected. Close existing popups.'
    } else if (error.code === 'auth/popup-blocked') {
      errorMessage.value = 'Popup blockage detected. Adjust browser settings.'
    } else {
      errorMessage.value = 'Deployment failed. Check network protocols.'
    }
  } finally {
    if (attemptId === currentAttemptId) {
      isSigningIn.value = false
      clearTimeout(resetTimer)
    }
  }
}

function forceReset() {
  currentAttemptId++
  isSigningIn.value = false
  showReset.value = false
  clearTimeout(resetTimer)
  errorMessage.value = 'Session reset successful. Re-initialize deployment.'
}
</script>
