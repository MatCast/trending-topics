<template>
  <div class="max-w-3xl mx-auto">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold mb-2">Welcome! Let's set up your sources 🚀</h1>
      <p class="text-base-content/60">Configure where you want to find trending topics.</p>
    </div>

    <!-- Progress Steps -->
    <ul class="steps steps-horizontal w-full mb-8">
      <li class="step" :class="{ 'step-primary': currentStep >= 1 }">Keywords</li>
      <li class="step" :class="{ 'step-primary': currentStep >= 2 }">Reddit</li>
      <li class="step" :class="{ 'step-primary': currentStep >= 3 }">Other Sources</li>
      <li class="step" :class="{ 'step-primary': currentStep >= 4 }">Preferences</li>
    </ul>

    <!-- Step 1: Global Keywords -->
    <div v-if="currentStep === 1" class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <h2 class="card-title">Global Keywords</h2>
        <p class="text-base-content/60 text-sm mb-4">
          These keywords will be used to filter content from sources that support keyword search (Hacker News, Bluesky).
          For Reddit, keywords are optional — you can toggle them per subreddit.
        </p>

        <div class="form-control">
          <label class="label"><span class="label-text">Add keywords</span></label>
          <div class="join w-full">
            <input
              v-model="newKeyword"
              type="text"
              placeholder="e.g., AI, Startup, GPT"
              class="input input-bordered join-item flex-1"
              @keyup.enter="addKeyword"
            />
            <button class="btn btn-primary join-item" @click="addKeyword">Add</button>
          </div>
        </div>

        <div class="flex flex-wrap gap-2 mt-4">
          <div
            v-for="(kw, idx) in globalKeywords"
            :key="idx"
            class="badge badge-lg badge-primary gap-2"
          >
            {{ kw }}
            <button class="btn btn-ghost btn-xs" @click="globalKeywords.splice(idx, 1)">✕</button>
          </div>
          <span v-if="!globalKeywords.length" class="text-base-content/40 text-sm">No keywords added yet</span>
        </div>

        <div class="card-actions justify-end mt-6">
          <button class="btn btn-primary" @click="currentStep = 2">
            Next: Reddit Sources →
          </button>
        </div>
      </div>
    </div>

    <!-- Step 2: Reddit Sources -->
    <div v-if="currentStep === 2" class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <h2 class="card-title flex items-center gap-2">
          <svg class="w-6 h-6 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
          </svg>
          Reddit Subreddits
        </h2>
        <p class="text-base-content/60 text-sm mb-4">
          Add subreddits to monitor for rising posts. You can toggle keyword filtering per subreddit.
        </p>

        <div class="form-control">
          <label class="label"><span class="label-text">Add subreddit</span></label>
          <div class="join w-full">
            <span class="join-item btn btn-disabled">r/</span>
            <input
              v-model="newSubreddit"
              type="text"
              placeholder="e.g., startups"
              class="input input-bordered join-item flex-1"
              :class="{ 'input-error': redditError }"
              @keyup.enter="addRedditSource"
              @input="redditError = ''"
            />
            <button class="btn btn-primary join-item" @click="addRedditSource">Add</button>
          </div>
          <label v-if="redditError" class="label">
            <span class="label-text-alt text-error font-medium">{{ redditError }}</span>
          </label>
        </div>

        <div class="space-y-2 mt-4">
          <div
            v-for="(src, idx) in redditSources"
            :key="idx"
            class="flex items-center justify-between p-3 bg-base-200 rounded-lg"
          >
            <div class="flex items-center gap-3">
              <span class="font-medium">r/{{ src.params.subreddit }}</span>
              <label class="label cursor-pointer gap-2">
                <span class="label-text text-xs opacity-60">Keywords</span>
                <input type="checkbox" class="toggle toggle-sm toggle-primary" v-model="src.use_global_keywords" />
              </label>
            </div>
            <button class="btn btn-ghost btn-sm btn-square" @click="redditSources.splice(idx, 1)">✕</button>
          </div>
          <p v-if="!redditSources.length" class="text-base-content/40 text-sm p-3">No subreddits added yet</p>
        </div>

        <div class="card-actions justify-between mt-6">
          <button class="btn btn-ghost" @click="currentStep = 1">← Back</button>
          <button class="btn btn-primary" @click="currentStep = 3">Next: Other Sources →</button>
        </div>
      </div>
    </div>

    <!-- Step 3: HN & Bluesky -->
    <div v-if="currentStep === 3" class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <h2 class="card-title">Other Sources</h2>
        <p class="text-base-content/60 text-sm mb-4">
          Enable additional trend sources. These use your global keywords for searching.
        </p>

        <!-- Hacker News -->
        <div class="p-4 bg-base-200 rounded-xl mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <span class="text-xl font-bold text-orange-400">Y</span>
              <div>
                <h3 class="font-semibold">Hacker News</h3>
                <p class="text-xs text-base-content/60">Top stories filtered by your keywords</p>
              </div>
            </div>
            <input type="checkbox" class="toggle toggle-primary" v-model="enableHN" />
          </div>
        </div>

        <!-- Bluesky -->
        <div class="p-4 bg-base-200 rounded-xl mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <span class="text-xl">🦋</span>
              <div>
                <h3 class="font-semibold">Bluesky</h3>
                <p class="text-xs text-base-content/60">Search posts using your global keywords</p>
              </div>
            </div>
            <input type="checkbox" class="toggle toggle-primary" v-model="enableBluesky" />
          </div>
        </div>

        <!-- Indie Hackers -->
        <div class="p-4 bg-base-200 rounded-xl">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <svg class="w-6 h-6 text-indigo-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 4c1.105 0 2 .895 2 2s-.895 2-2 2-2-.895-2-2 .895-2 2-2zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm6 6H6v-1.5c0-1.93 1.57-3.5 3.5-3.5h5c1.93 0 3.5 1.57 3.5 3.5V20z"/>
              </svg>
              <div>
                <h3 class="font-semibold">Indie Hackers</h3>
                <p class="text-xs text-base-content/60">Top stories from Indie Hackers RSS feed</p>
              </div>
            </div>
            <input type="checkbox" class="toggle toggle-primary" v-model="enableIH" />
          </div>
        </div>

        <div class="card-actions justify-between mt-6">
          <button class="btn btn-ghost" @click="currentStep = 2">← Back</button>
          <button class="btn btn-primary" @click="currentStep = 4">Next: Preferences →</button>
        </div>
      </div>
    </div>

    <!-- Step 4: Preferences -->
    <div v-if="currentStep === 4" class="card bg-base-100 shadow-xl border border-base-300">
      <div class="card-body">
        <h2 class="card-title">Preferences</h2>
        <p class="text-base-content/60 text-sm mb-4">Fine-tune your extraction settings.</p>

        <div class="grid gap-4">
          <div class="form-control">
            <label class="label"><span class="label-text">Time window (hours)</span></label>
            <input v-model.number="timeWindowHours" type="number" min="1" max="168" class="input input-bordered" />
            <label class="label"><span class="label-text-alt">How far back to look for trending content</span></label>
          </div>

          <div class="form-control">
            <label class="label"><span class="label-text">Max results per source</span></label>
            <input v-model.number="maxTrendsPerSource" type="number" min="1" max="50" class="input input-bordered" />
            <label class="label"><span class="label-text-alt">Maximum number of trending topics to keep per source</span></label>
          </div>
        </div>

        <div class="card-actions justify-between mt-6">
          <button class="btn btn-ghost" @click="currentStep = 3">← Back</button>
          <button
            class="btn btn-primary"
            :class="{ 'btn-disabled loading': isSaving }"
            @click="saveAndContinue"
          >
            <span v-if="isSaving" class="loading loading-spinner loading-sm"></span>
            {{ isSaving ? 'Saving...' : 'Complete Setup ✓' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const { apiFetch } = useApi()

const currentStep = ref(1)
const isSaving = ref(false)

// Step 1: Keywords
const globalKeywords = ref<string[]>([])
const newKeyword = ref('')

function addKeyword() {
  const kw = newKeyword.value.trim()
  if (kw && !globalKeywords.value.includes(kw)) {
    globalKeywords.value.push(kw)
    newKeyword.value = ''
  }
}

// Step 2: Reddit
const redditSources = ref<any[]>([])
const newSubreddit = ref('')
const redditError = ref('')

function addRedditSource() {
  const sub = newSubreddit.value.trim()
  redditError.value = ''

  if (!sub) return

  // 1. Format validation (3-21 chars, alphanumeric/underscores)
  const redditRegex = /^[a-zA-Z0-9_]{3,21}$/
  if (!redditRegex.test(sub)) {
    redditError.value = 'Invalid subreddit name (3-21 chars, no spaces/special chars)'
    return
  }

  // 2. Case-insensitive uniqueness check
  const isDuplicate = redditSources.value.some(
    s => s.params.subreddit.toLowerCase() === sub.toLowerCase()
  )
  if (isDuplicate) {
    redditError.value = `r/${sub} is already in your list`
    return
  }

  redditSources.value.push({
    type: 'reddit',
    name: `r/${sub}`,
    enabled: true,
    use_global_keywords: false,
    params: { subreddit: sub },
  })
  newSubreddit.value = ''
}

// Step 3: Other sources
const enableHN = ref(true)
const enableBluesky = ref(false)
const enableIH = ref(true)

// Step 4: Preferences
const timeWindowHours = ref(3)
const maxTrendsPerSource = ref(3)

async function saveAndContinue() {
  isSaving.value = true
  try {
    // Save user settings
    await apiFetch('/api/settings', {
      method: 'PUT',
      body: {
        global_keywords: globalKeywords.value,
        time_window_hours: timeWindowHours.value,
        max_trends_per_source: maxTrendsPerSource.value,
      },
    })

    // Save Reddit sources
    for (const src of redditSources.value) {
      await apiFetch('/api/sources', { method: 'POST', body: src })
    }

    // Save HN source if enabled
    if (enableHN.value) {
      await apiFetch('/api/sources', {
        method: 'POST',
        body: {
          type: 'hackernews',
          name: 'Hacker News',
          enabled: true,
          use_global_keywords: true,
          params: { url: 'https://hnrss.org/newest?points=10' },
        },
      })
    }

    // Save Bluesky source if enabled
    if (enableBluesky.value) {
      await apiFetch('/api/sources', {
        method: 'POST',
        body: {
          type: 'bluesky',
          name: 'Bluesky',
          enabled: true,
          use_global_keywords: true,
          params: {},
        },
      })
    }

    // Save Indie Hackers source if enabled
    if (enableIH.value) {
      await apiFetch('/api/sources', {
        method: 'POST',
        body: {
          type: 'indiehackers',
          name: 'Indie Hackers',
          enabled: true,
          use_global_keywords: true,
          params: {},
        },
      })
    }

    navigateTo('/')
  } catch (error) {
    console.error('Failed to save onboarding config:', error)
  } finally {
    isSaving.value = false
  }
}
</script>
