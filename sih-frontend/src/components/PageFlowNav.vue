<template>
  <div v-if="flow.total > 1 && flow.current" class="page-flow-nav mb-6">
    <div class="page-card p-4 border border-teal-500/20 bg-slate-900/80 backdrop-blur">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Parcours guidé</p>
          <p class="text-white text-sm font-medium truncate">
            Étape {{ flow.step }} / {{ flow.total }} — {{ flow.currentLabel }}
          </p>
          <div class="flex flex-wrap gap-1 mt-2">
            <span
              v-for="(p, i) in flow.pages"
              :key="p.path"
              class="w-2 h-2 rounded-full transition"
              :class="i + 1 === flow.step ? 'bg-teal-400 scale-125' : i + 1 < flow.step ? 'bg-teal-600/60' : 'bg-white/15'"
              :title="p.title"
            />
          </div>
        </div>

        <div class="flex flex-wrap gap-2 shrink-0">
          <button
            v-if="flow.prev"
            type="button"
            @click="goPrev"
            class="px-4 py-2 rounded-xl text-sm border border-white/10 text-slate-300 hover:bg-white/5 hover:text-white transition"
          >
            ← {{ flow.prevLabel }}
          </button>
          <button
            v-if="flow.next"
            type="button"
            @click="goNext"
            class="px-4 py-2 rounded-xl text-sm font-medium bg-teal-500/20 border border-teal-500/40 text-teal-200 hover:bg-teal-500/30 transition"
          >
            {{ flow.nextLabel }} →
          </button>
          <span v-else class="px-4 py-2 text-xs text-emerald-400">✓ Fin du parcours</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { usePageFlow } from '../composables/usePageFlow.js'

const { flow, goPrev, goNext } = usePageFlow()
</script>
