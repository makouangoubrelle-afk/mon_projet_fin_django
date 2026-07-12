<template>

  <div class="space-y-6">

    <div class="page-heading">

      <div>

        <h2 class="text-xl font-bold text-white">🏢 Services & Redirections</h2>

        <p class="text-slate-400 text-sm">Parcours des pages en ordre — pause services et secrétaires</p>

      </div>

      <button v-if="canStructure" @click="openAdd" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter un service</button>

    </div>



    <div v-if="canTheme" class="page-card p-6">

      <h3 class="text-white font-semibold mb-2">🎨 Design de l'interface</h3>

      <p class="text-slate-500 text-sm mb-4">En tant que secrétaire générale, choisissez le thème appliqué à l'application.</p>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">

        <button

          v-for="(theme, key) in themes"

          :key="key"

          type="button"

          @click="pickTheme(key)"

          class="p-4 rounded-xl border text-left transition"

          :class="currentTheme === key ? 'border-white/40 bg-white/10' : 'border-white/10 bg-white/5 hover:bg-white/10'"

        >

          <div class="w-full h-8 rounded-lg mb-2" :style="{ background: theme.accent }"></div>

          <p class="text-white text-sm">{{ theme.label }}</p>

          <p v-if="currentTheme === key" class="text-xs theme-accent-text mt-1">Actif</p>

        </button>

      </div>

    </div>



    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

      <div v-for="svc in services" :key="svc.id" class="page-card p-6 transition"

        :class="svc.en_pause ? 'border-amber-500/40 opacity-90' : 'hover:border-teal-500/30'">

        <div class="flex items-start justify-between mb-4">

          <div class="w-12 h-12 rounded-2xl bg-teal-500/20 flex items-center justify-center text-xl">🏥</div>

          <div class="flex flex-col items-end gap-1">

            <span class="text-xs bg-teal-500/10 text-teal-300 px-2 py-1 rounded-full">{{ svc.code }}</span>

            <span class="text-xs px-2 py-0.5 rounded-full font-medium"

              :class="svc.en_pause ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'">

              {{ svc.en_pause ? 'En pause' : 'Actif' }}

            </span>

          </div>

        </div>

        <h3 class="text-white font-semibold text-lg">{{ svc.nom }}</h3>

        <div class="mt-4 space-y-2 text-sm">

          <p class="text-slate-400">📍 <span class="text-white">{{ svc.batiment }}</span>, Étage {{ svc.etage }}</p>

          <p class="text-slate-400">📞 <span class="text-white">{{ svc.telephone || '—' }}</span></p>

          <p class="text-slate-400">💉 Infirmiers en service : <span class="text-teal-300">{{ svc.infirmiers_en_service }}/{{ svc.infirmiers_total }}</span></p>

          <div class="mt-3 p-3 rounded-xl bg-white/5 border border-white/5">

            <p class="text-[10px] uppercase tracking-wider text-slate-500 mb-1">Secrétaire du service</p>

            <div class="flex items-center justify-between gap-2">

              <p class="text-white font-medium flex items-center gap-2">

                <span>📋</span>{{ svc.secretaire_nom || 'Non assignée' }}

              </p>

              <span v-if="svc.secretaire_nom" class="text-[10px] px-2 py-0.5 rounded-full shrink-0"

                :class="svc.secretaire_en_pause ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'">

                {{ svc.secretaire_en_pause ? 'Pause' : 'Disponible' }}

              </span>

            </div>

          </div>

        </div>

        <div class="mt-4 flex flex-wrap gap-2">

          <button v-if="canRedirects" @click="togglePause(svc)" class="text-xs px-3 py-1.5 rounded-lg border border-white/10 hover:bg-white/5"

            :class="svc.en_pause ? 'text-emerald-400' : 'text-amber-400'">

            {{ svc.en_pause ? '▶ Reprendre service' : '⏸ Pause service' }}

          </button>

          <button v-if="canStructure" @click="openEdit(svc)" class="text-xs px-3 py-1.5 rounded-lg text-teal-400 border border-teal-500/20 hover:bg-teal-500/10">Modifier</button>

        </div>

      </div>

    </div>



    <div class="page-card p-6">

      <h3 class="text-white font-semibold mb-4">📋 Secrétaires — statut pause</h3>

      <table class="w-full text-sm">

        <thead>

          <tr class="text-slate-500 text-xs uppercase">

            <th class="p-3 text-left">Nom</th>

            <th class="p-3 text-left">Email</th>

            <th class="p-3 text-left">Service</th>

            <th class="p-3 text-left">Statut</th>

            <th class="p-3 text-left">Action</th>

          </tr>

        </thead>

        <tbody>

          <tr v-for="s in secretaires" :key="s.id" class="border-t border-white/5">

            <td class="p-3 text-white">{{ s.nom_complet }}</td>

            <td class="p-3 text-slate-400">{{ s.email }}</td>

            <td class="p-3 text-slate-400">{{ s.service_nom || '—' }}</td>

            <td class="p-3">

              <span class="text-xs px-2 py-0.5 rounded-full"

                :class="s.en_pause ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'">

                {{ s.en_pause ? 'En pause' : 'Disponible' }}

              </span>

            </td>

            <td class="p-3">

              <button v-if="canRedirects" @click="toggleSecPause(s)" class="text-xs text-teal-400 hover:text-teal-300">

                {{ s.en_pause ? 'Reprendre' : 'Mettre en pause' }}

              </button>

            </td>

          </tr>

        </tbody>

      </table>

    </div>



    <div class="page-card p-6">

      <h3 class="text-white font-semibold mb-2">🔀 Plan de redirection des pages (ordre officiel)</h3>

      <p class="text-slate-500 text-sm mb-4">Après connexion, chaque rôle est redirigé vers la 1<sup>re</sup> page de son parcours, puis suit cet ordre dans le menu.</p>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <div v-for="role in rolesNav" :key="role" class="rounded-xl border border-white/10 bg-white/5 p-4">

          <p class="text-white font-medium mb-3">{{ ROLE_LABELS[role] }}</p>

          <ol class="space-y-1.5 text-sm max-h-48 overflow-y-auto">

            <li v-for="step in redirectPlanForRole(role)" :key="step.path" class="flex items-center gap-2">

              <span class="text-[10px] w-6 h-6 rounded-full flex items-center justify-center shrink-0"

                :class="step.isHome ? 'bg-teal-500/30 text-teal-200' : 'bg-white/10 text-slate-400'">

                {{ step.step }}

              </span>

              <router-link :to="step.path" class="text-slate-300 hover:text-teal-300 truncate">

                {{ step.title }}

                <span v-if="step.isHome" class="text-teal-400 text-[10px] ml-1">(accueil)</span>

              </router-link>

            </li>

          </ol>

        </div>

      </div>

    </div>



    <div v-if="showModal" class="modal" @click.self="showModal = false">

      <div class="modal-content max-w-md">

        <h3 class="text-white font-semibold mb-4">{{ editing ? 'Modifier le service' : 'Nouveau service' }}</h3>

        <form @submit.prevent="save" class="space-y-3">

          <input v-if="!editing" v-model="form.code" placeholder="Code (ex: CARDIO) *" class="modal-input" required />

          <input v-model="form.nom" placeholder="Nom du service *" class="modal-input" required />

          <input v-model="form.batiment" placeholder="Bâtiment" class="modal-input" />

          <input v-model="form.etage" placeholder="Étage" class="modal-input" />

          <input v-model="form.telephone" placeholder="Téléphone" class="modal-input" />

          <select v-model="form.secretaire_id" class="modal-input">

            <option value="">Secrétaire (optionnel)</option>

            <option v-for="s in secretaires" :key="s.id" :value="s.id">{{ s.nom_complet }}</option>

          </select>

          <div class="modal-buttons">

            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>

            <button type="submit" class="btn-save">Enregistrer</button>

          </div>

        </form>

      </div>

    </div>

  </div>

</template>



<script setup>

import { ref, onMounted } from 'vue'

import { clinicalService, secretaireService, canManageStructure, canManageRedirects, canManageUi } from '../services/api.js'

import { ROLES_WITH_NAV, ROLE_LABELS, redirectPlanForRole } from '../config/navigation.js'

import { THEMES, getStoredTheme, setStoredTheme } from '../utils/theme.js'



const rolesNav = ROLES_WITH_NAV
const canStructure = canManageStructure()
const canRedirects = canManageRedirects()
const canTheme = canManageUi()
const themes = THEMES
const currentTheme = ref(getStoredTheme())

function pickTheme(key) {
  if (!setStoredTheme(key)) return
  currentTheme.value = key
}



const services = ref([])

const secretaires = ref([])

const showModal = ref(false)

const editing = ref(null)

const form = ref({ code: '', nom: '', batiment: 'Bâtiment A', etage: 'RDC', telephone: '', secretaire_id: '' })



function openAdd() {
  if (!canStructure) return
  editing.value = null

  form.value = { code: '', nom: '', batiment: 'Bâtiment A', etage: 'RDC', telephone: '', secretaire_id: '' }

  showModal.value = true

}



function openEdit(svc) {
  if (!canStructure) return
  editing.value = svc

  form.value = {

    code: svc.code, nom: svc.nom, batiment: svc.batiment, etage: svc.etage,

    telephone: svc.telephone || '', secretaire_id: svc.secretaire_id || '',

  }

  showModal.value = true

}



async function load() {

  const [svcs, secs] = await Promise.all([clinicalService.services(), secretaireService.list()])

  services.value = svcs

  secretaires.value = secs

}



async function save() {
  if (!canStructure) return
  const payload = { ...form.value }

  if (payload.secretaire_id) payload.secretaire_id = Number(payload.secretaire_id)

  else delete payload.secretaire_id

  if (editing.value) {

    const { code, ...rest } = payload

    await clinicalService.updateService(editing.value.id, rest)

  } else {

    await clinicalService.createService(payload)

  }

  showModal.value = false

  await load()

}



async function togglePause(svc) {

  await clinicalService.toggleServicePause(svc.id)

  await load()

}



async function toggleSecPause(s) {

  await secretaireService.togglePause(s.id)

  await load()

}



onMounted(load)

</script>

