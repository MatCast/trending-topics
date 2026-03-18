/**
 * Firebase client plugin — initializes Firebase Auth on the client side.
 */
import { initializeApp } from 'firebase/app'
import { getAuth, type Auth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const firebaseConfig = {
    apiKey: config.public.firebaseApiKey,
    authDomain: config.public.firebaseAuthDomain,
    projectId: config.public.firebaseProjectId,
    appId: config.public.firebaseAppId,
    messagingSenderId: config.public.firebaseMessagingSenderId as string,
    storageBucket: config.public.firebaseStorageBucket as string,
  }

  // Diagnostic logs to help debug configuration issues in the browser
  if (!firebaseConfig.apiKey) {
    console.warn('Firebase: Missing apiKey in configuration.')
  }
  if (!firebaseConfig.authDomain) {
    console.warn('Firebase: Missing authDomain in configuration.')
  }

  const app = initializeApp(firebaseConfig)
  const auth = getAuth(app)
  const db = getFirestore(app)

  return {
    provide: {
      firebaseAuth: auth,
      firebaseFirestore: db,
    },
  }
})
