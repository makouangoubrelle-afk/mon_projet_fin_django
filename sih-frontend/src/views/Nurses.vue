<template>

  <div class="space-y-6">

    <div class="page-heading">

      <div>

        <h2 class="text-xl font-bold text-white">💉 Infirmiers(ères)</h2>

        <p class="text-slate-400 text-sm">Par service — en service ou en pause</p>

      </div>

      <button @click="showAdd = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter</button>

    </div>



    <div class="page-card p-4 flex flex-wrap gap-3 items-center">

      <select v-model="filtreService" class="modal-input text-sm max-w-xs" @change="load">

        <option value="">Tous les services</option>

        <option v-for="s in services" :key="s.id" :value="s.id">{{ s.nom }}</option>

      </select>

      <span class="text-xs text-slate-500">{{ enService }} en service · {{ enPause }} en pause</span>

    </div>



    <div class="table-card">

      <table class="w-full text-sm">

        <thead>

          <tr class="text-slate-500 text-xs uppercase">

            <th class="p-4 text-left">Nom</th>

            <th class="p-4 text-left">Service</th>

            <th class="p-4 text-left">Téléphone</th>

            <th class="p-4 text-left">Statut</th>

            <th class="p-4 text-left">Actions</th>

          </tr>

        </thead>

        <tbody>

          <tr v-for="n in infirmiers" :key="n.id" class="border-t border-white/5 hover:bg-white/3">

            <td class="p-4 text-white font-medium">{{ n.prenom }} {{ n.nom }}</td>

            <td class="p-4 text-slate-400">{{ n.service_nom || '—' }}</td>

            <td class="p-4 text-slate-400">{{ n.telephone }}</td>

            <td class="p-4">

              <span v-if="!n.est_actif" class="text-xs px-2 py-0.5 rounded-full bg-slate-500/20 text-slate-400">Inactif</span>

              <span v-else class="text-xs px-2 py-0.5 rounded-full"

                :class="n.en_pause ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'">

                {{ n.en_pause ? 'En pause' : 'En service' }}

              </span>

            </td>

            <td class="p-4">

              <ActionMenu :items="menuItems(n)" @action="(k) => onAction(k, n)" />

            </td>

          </tr>

          <tr v-if="!infirmiers.length"><td colspan="5" class="p-8 text-center text-slate-500">Aucun infirmier</td></tr>

        </tbody>

      </table>

    </div>



    <div v-if="showAdd" class="modal" @click.self="showAdd = false">

      <div class="modal-content max-w-md">

        <h3 class="text-white font-semibold mb-4">Nouvel infirmier(ère)</h3>

        <form @submit.prevent="create" class="space-y-3">

          <input v-model="form.nom" placeholder="Nom *" class="modal-input" required />

          <input v-model="form.prenom" placeholder="Prénom *" class="modal-input" required />

          <input v-model="form.email" type="email" placeholder="Email *" class="modal-input" required />

          <input v-model="form.telephone" placeholder="Téléphone *" class="modal-input" required />

          <select v-model="form.service_id" class="modal-input">

            <option value="">Service</option>

            <option v-for="s in services" :key="s.id" :value="s.id">{{ s.nom }}</option>

          </select>

          <div class="modal-buttons">

            <button type="button" @click="showAdd = false" class="btn-cancel">Annuler</button>

            <button type="submit" class="btn-save">Enregistrer</button>

          </div>

        </form>

      </div>

    </div>

  </div>

</template>



<script setup>

import { ref, computed, onMounted } from 'vue'

import { nurseService, clinicalService } from '../services/api.js'

import ActionMenu from '../components/ActionMenu.vue'



const infirmiers = ref([])

const services = ref([])

const showAdd = ref(false)

const filtreService = ref('')

const form = ref({ nom: '', prenom: '', email: '', telephone: '', service_id: '' })



const enService = computed(() => infirmiers.value.filter(n => n.est_actif && !n.en_pause).length)

const enPause = computed(() => infirmiers.value.filter(n => n.est_actif && n.en_pause).length)



function menuItems(n) {

  return [

    { key: 'pause', icon: '⏸', label: n.en_pause ? 'Reprendre service' : 'Mettre en pause' },

    { key: 'toggle', icon: '⭐', label: n.est_actif ? 'Désactiver' : 'Activer' },

    { key: 'delete', icon: '🗑️', label: 'Supprimer', danger: true },

  ]

}



async function onAction(key, n) {

  if (key === 'pause') await nurseService.togglePause(n.id)

  else if (key === 'toggle') await nurseService.toggle(n.id)

  else if (key === 'delete' && confirm('Supprimer ?')) await nurseService.delete(n.id)

  await load()

}



async function load() {

  infirmiers.value = await nurseService.list(filtreService.value || null)

  services.value = await clinicalService.services()

}



async function create() {

  const payload = { ...form.value }

  if (payload.service_id) payload.service_id = Number(payload.service_id)

  else delete payload.service_id

  await nurseService.create(payload)

  showAdd.value = false

  form.value = { nom: '', prenom: '', email: '', telephone: '', service_id: '' }

  await load()

}



onMounted(load)

</script>

