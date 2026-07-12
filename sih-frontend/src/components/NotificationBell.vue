<template>
  <div class="relative">
    <button
      type="button"
      class="relative w-10 h-10 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-lg transition"
      title="Notifications"
      @click="open = !open"
    >
      🔔
      <span
        v-if="unreadCount"
        class="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center"
      >
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <div
      v-if="open"
      class="absolute right-0 top-12 w-80 max-h-96 overflow-y-auto rounded-2xl border border-white/10 bg-slate-900 shadow-2xl z-50"
    >
      <div class="flex items-center justify-between p-3 border-b border-white/10">
        <p class="text-white text-sm font-medium">Notifications</p>
        <button v-if="unreadCount" type="button" class="text-xs text-teal-400" @click="markAll">Tout lire</button>
      </div>
      <div v-if="loading" class="p-4 text-slate-500 text-sm">Chargement…</div>
      <div v-else-if="!items.length" class="p-4 text-slate-500 text-sm">Aucune notification.</div>
      <button
        v-for="n in items"
        :key="n.id"
        type="button"
        class="w-full text-left p-3 border-b border-white/5 hover:bg-white/5 transition"
        :class="n.is_read ? 'opacity-60' : ''"
        @click="onClick(n)"
      >
        <p class="text-white text-sm font-medium">{{ n.title }}</p>
        <p class="text-slate-400 text-xs mt-1 line-clamp-2">{{ n.message }}</p>
        <p class="text-[10px] text-slate-600 mt-1">{{ fmt(n.created_at) }}</p>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { coreService } from '../services/api.js'

const router = useRouter()
const open = ref(false)
const items = ref([])
const loading = ref(false)
const unreadCount = ref(0)
let timer = null

function fmt(d) {
  return new Date(d).toLocaleString('fr-FR')
}

async function load() {
  loading.value = true
  try {
    items.value = await coreService.notifications()
    unreadCount.value = items.value.filter((n) => !n.is_read).length
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function onClick(n) {
  if (!n.is_read) {
    await coreService.markNotificationRead(n.id)
    n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
  if (n.link) {
    open.value = false
    router.push(n.link)
  }
}

async function markAll() {
  await coreService.markAllNotificationsRead()
  items.value.forEach((n) => { n.is_read = true })
  unreadCount.value = 0
}

function onDocClick(e) {
  if (!e.target.closest('.relative')) open.value = false
}

onMounted(() => {
  load()
  timer = setInterval(load, 60000)
  document.addEventListener('click', onDocClick)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  document.removeEventListener('click', onDocClick)
})
</script>
