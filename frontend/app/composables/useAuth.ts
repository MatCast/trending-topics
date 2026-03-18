/**
 * Auth composable — manages Firebase Auth state and provides sign-in/sign-out.
 */
import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User,
} from 'firebase/auth'

const user = ref<User | null>(null)
const isLoading = ref(true)
const isInitialized = ref(false)

export function useAuth() {
  const { $firebaseAuth } = useNuxtApp()

  // Initialize auth listener once
  if (!isInitialized.value && $firebaseAuth) {
    isInitialized.value = true
    onAuthStateChanged($firebaseAuth, (firebaseUser) => {
      user.value = firebaseUser
      isLoading.value = false
    })
  }

  async function signInWithGoogle() {
    if (!$firebaseAuth) return
    const provider = new GoogleAuthProvider()
    try {
      await signInWithPopup($firebaseAuth, provider)
    } catch (error: any) {
      if (error?.code !== 'auth/popup-closed-by-user' && error?.code !== 'auth/cancelled-popup-request') {
        console.error('Sign in failed:', error)
      }
      throw error
    }
  }

  async function signOut() {
    if (!$firebaseAuth) return
    await firebaseSignOut($firebaseAuth)
    user.value = null
  }

  async function getIdToken(): Promise<string | null> {
    if (!user.value) return null
    try {
      return await user.value.getIdToken()
    } catch {
      return null
    }
  }

  const isAuthenticated = computed(() => !!user.value)

  /**
   * Returns a promise that resolves when the auth state is initialized.
   */
  async function waitForAuth(): Promise<void> {
    if (import.meta.server || !isLoading.value) return
    return new Promise((resolve) => {
      const stop = watch(isLoading, (loading) => {
        if (!loading) {
          stop()
          resolve()
        }
      })
    })
  }

  return {
    user: readonly(user),
    isLoading: readonly(isLoading),
    isAuthenticated,
    signInWithGoogle,
    signOut,
    getIdToken,
    waitForAuth,
  }
}
