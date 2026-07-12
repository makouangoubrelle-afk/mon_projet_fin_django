<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">📜 Journal & sécurité</h2>
        <p class="text-slate-400 text-sm">Historique des connexions et journal des activités</p>
      </div>
    </div>

    <div class="flex gap-2">
      <button v-for="t in tabs" :key="t.id" type="button"
        class="px-4 py-2 rounded-xl text-sm border transition"
        :class="tab === t.id ? 'bg-teal-500/20 border-teal-500/40 text-teal-200' : 'border-white/10 text-slate-400'"
        @click="tab = t.id; load()">
        {{ t.label }}
      </button>
    </div>

    <div v-if="error" class="text-red-400 text-sm">{{ error }}</div>

    <div class="page-card overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-white/5 text-slate-500 text-xs uppercase">
          <tr v-if="tab === 'login'">
            <th class="p-3 text-left">Date</th>
            <th class="p-3 text-left">Email</th>
            <th class="p-3 text-left">Rôle</th>
            <th class="p-3 text-left">IP</th>
            <th class="p-3 text-left">Résultat</th>
          </tr>
          <tr v-else>
            <th class="p-3 text-left">Date</th>
            <th class="p-3 text-left">Utilisateur</th>
            <th class="p-3 text-left">Action</th>
            <th class="p-3 text-left">Module</th>
            <th class="p-3 text-left">Détail</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="tab === 'login'">
            <tr v-for="row in logins" :key="row.id" class="border-t border-white/5">
              <td class="p-3 text-slate-400 text-xs">{{ fmt(row.created_at) }}</td>
              <td class="p-3 text-white">{{ row.email }}</td>
              <td class="p-3 text-slate-300">{{ row.role }}</td>
              <td class="p-3 text-slate-500">{{ row.ip_address || '—' }}</td>
              <td class="p-3">
                <span class="text-xs" :class="row.success ? 'text-emerald-400' : 'text-red-400'">
                  {{ row.success ? 'OK' : 'Échec' }}
                </span>
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="row in activities" :key="row.id" class="border-t border-white/5">
              <td class="p-3 text-slate-400 text-xs whitespace-nowrap">{{ fmt(row.created_at) }}</td>
              <td class="p-3 text-white text-xs">{{ row.email }}<br><span class="text-slate-500">{{ row.role }}</span></td>
              <td class="p-3 text-teal-300">{{ row.action }}</td>
              <td class="p-3 text-slate-400">{{ row.module }}</td>
              <td class="p-3 text-slate-500 text-xs max-w-xs truncate">{{ row.detail }}</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { coreService } from '../services/api.js'

const tab = ref('login')
const tabs = [
  { id: 'login', label: '🔐 Connexions' },
  { id: 'activity', label: '📋 Activités' },
]
const logins = ref([])
const activities = ref([])
const error = ref('')

function fmt(d) {
  return new Date(d).toLocaleString('fr-FR')
}

async function load() {
  error.value = ''
  try {
    if (tab.value === 'login') {
      logins.value = await coreService.loginHistory(150)
    } else {
      activities.value = await coreService.activityLog(150)
    }
  } catch (e) {
    error.value = e.message
  }
}

onMounted(load)
</script>
