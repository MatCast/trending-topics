<template>
  <div class="space-y-8">
    <!-- Unified Scheduler Toggle -->
    <SchedulerToggle 
      v-if="!isFreeTier"
    />

    <!-- Conditional Content -->
    <div v-if="schedule.active || isFreeTier" class="space-y-8 animate-in fade-in zoom-in duration-300">
      <!-- Extraction Parameters Section -->
      <section class="space-y-4">
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">1. Data Parameters (Scheduled)</span>
          <div class="h-0.5 bg-black grow ml-4 opacity-30"></div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
           <Card 
             class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-none hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer group bg-white"
             @click="windowInput?.focus()"
           >
             <CardHeader class="pb-2">
               <div class="flex justify-between items-center">
                 <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Window</span>
                 <ArrowRight class="size-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
               </div>
             </CardHeader>
             <CardContent>
               <div class="flex items-baseline gap-2">
                 <input 
                   ref="windowInput"
                   type="number" 
                   v-model.number="schedule.time_window_hours" 
                   class="bg-transparent border-none p-0 focus:ring-0 font-black text-4xl w-24 text-black selection:bg-primary/30" 
                   min="1" max="168" 
                 />
                 <span class="text-xs font-black uppercase text-muted-foreground">Hours</span>
               </div>
             </CardContent>
           </Card>

           <Card 
             class="border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-none hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all cursor-pointer group bg-white"
             @click="maxInput?.focus()"
           >
             <CardHeader class="pb-2">
               <div class="flex justify-between items-center">
                 <span class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Limit</span>
                 <ArrowRight class="size-3 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
               </div>
             </CardHeader>
             <CardContent>
               <div class="flex items-baseline gap-2">
                 <input 
                   ref="maxInput"
                   type="number" 
                   v-model.number="schedule.max_trends_per_source" 
                   class="bg-transparent border-none p-0 focus:ring-0 font-black text-4xl w-24 text-black selection:bg-primary/30" 
                   min="1" max="50" 
                 />
                 <span class="text-xs font-black uppercase text-muted-foreground">Trends</span>
               </div>
             </CardContent>
           </Card>
        </div>
        <p class="text-[10px] font-bold text-muted-foreground uppercase tracking-widest px-1">These parameters only affect automated runs.</p>
      </section>

      <!-- Schedule Section -->
      <section class="space-y-4">
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground">2. Run Schedule</span>
          <div class="h-0.5 bg-black/10 grow"></div>
        </div>

        <!-- Free Tier Notice -->
        <div v-if="isFreeTier" class="bg-primary/10 border-2 border-black p-6 space-y-4 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
           <div class="flex gap-4">
             <div class="size-10 flex items-center justify-center border-2 border-black bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                <Lock class="size-5 text-black" />
             </div>
             <div>
               <h4 class="font-black text-sm uppercase">Scheduling Locked</h4>
               <p class="text-xs font-bold text-muted-foreground mt-1 leading-relaxed">Automated scheduling is only available for Pro users.</p>
             </div>
           </div>
           <Button class="w-full border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-[10px] hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-none transition-all" variant="neutral" disabled>
             Compare Plans
           </Button>
        </div>

        <div v-else class="space-y-6">
          <!-- Schedule Type -->
          <div class="space-y-3">
            <label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground px-1">Run Frequency</label>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <Button 
                v-for="opt in scheduleOptions" 
                :key="opt.value"
                variant="neutral"
                class="border-2 border-black rounded-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-[10px] h-10 transition-all"
                :class="schedule.type === opt.value ? 'bg-primary text-black translate-x-0.5 translate-y-0.5 shadow-none' : 'bg-white hover:bg-muted'"
                @click="schedule.type = opt.value"
              >
                {{ opt.label }}
              </Button>
            </div>
          </div>

          <!-- Conditional Contextual Params -->
          <div class="animate-in fade-in slide-in-from-top-2 duration-300" v-if="schedule.type !== 'manual'">
            <div class="bg-muted/30 border-2 border-black p-6 space-y-6 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              
              <!-- Hourly interval -->
              <div v-if="schedule.type === 'hourly'" class="space-y-4">
                <div class="flex justify-between items-center">
                  <label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Every N hours</label>
                  <Badge class="border-2 border-black bg-primary text-black font-black uppercase rounded-none">{{ schedule.interval_hours }}h</Badge>
                </div>
                <input 
                  v-model.number="schedule.interval_hours" 
                  type="range" 
                  min="1" 
                  max="24" 
                  class="w-full h-8 appearance-none bg-transparent cursor-pointer group
                    [&::-webkit-slider-runnable-track]:h-2 
                    [&::-webkit-slider-runnable-track]:bg-white 
                    [&::-webkit-slider-runnable-track]:border-2 
                    [&::-webkit-slider-runnable-track]:border-black
                    [&::-webkit-slider-thumb]:appearance-none 
                    [&::-webkit-slider-thumb]:size-5 
                    [&::-webkit-slider-thumb]:bg-primary 
                    [&::-webkit-slider-thumb]:border-2 
                    [&::-webkit-slider-thumb]:border-black
                    [&::-webkit-slider-thumb]:-mt-1.75
                    [&::-webkit-slider-thumb]:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]" 
                />
              </div>

              <!-- Daily/Weekly hour -->
              <div v-if="schedule.type === 'daily' || schedule.type === 'weekly'" class="space-y-3">
                <label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Execution Time (UTC)</label>
                <div class="relative">
                  <select 
                    class="w-full h-10 border-2 border-black bg-white px-4 font-black uppercase text-[10px] appearance-none focus:outline-none focus:ring-0 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]" 
                    v-model="schedule.hour_of_day"
                  >
                    <option v-for="h in 24" :key="h - 1" :value="h - 1">{{ String(h - 1).padStart(2, '0') }}:00 UTC</option>
                  </select>
                  <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                    <ChevronDown class="size-3 text-black" />
                  </div>
                </div>
              </div>

              <!-- Weekly day -->
              <div v-if="schedule.type === 'weekly'" class="space-y-3">
                <label class="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Day of week</label>
                <div class="grid grid-cols-7 gap-2">
                  <Button 
                    v-for="(day, idx) in days" 
                    :key="idx" 
                    variant="neutral"
                    class="border-2 border-black rounded-none shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] uppercase font-black text-[10px] p-0 h-10 w-full transition-all"
                    :class="schedule.day_of_week === idx ? 'bg-primary text-black translate-x-0.5 translate-y-0.5 shadow-none' : 'bg-white hover:bg-muted'"
                    @click="schedule.day_of_week = idx"
                  >
                    {{ day }}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Deactivated State -->
    <div v-else class="py-20 text-center space-y-6 border-4 border-dashed border-muted flex flex-col items-center">
       <div class="size-20 flex items-center justify-center border-4 border-black bg-muted shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
          <PowerOff class="size-10 text-muted-foreground" />
       </div>
       <div>
         <h4 class="text-xl font-black uppercase tracking-widest">Scheduler Deactivated</h4>
         <p class="text-xs font-bold text-muted-foreground mt-2 uppercase tracking-tight">Turn on the toggle to configure automated runs</p>
       </div>
    </div>

    <!-- Actions Area -->
    <slot name="actions"></slot>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, Lock, PowerOff, ChevronDown } from 'lucide-vue-next'
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useSettings } from '~/composables/useSettings'

const props = defineProps<{
  isFreeTier: boolean
  isSaving: boolean
}>()

const { schedule } = useSettings()

defineEmits(['save'])

const windowInput = ref<HTMLInputElement | null>(null)
const maxInput = ref<HTMLInputElement | null>(null)

const scheduleOptions = [
  { label: 'Manual', value: 'manual' },
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' }
]

const days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
</script>
