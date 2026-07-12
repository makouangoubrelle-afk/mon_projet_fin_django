<template>

  <div class="space-y-6">

    <div class="page-heading">

      <div>

        <h2 class="text-xl font-bold text-white">⭐ Clients privilégiés</h2>

        <p class="text-slate-400 text-sm">Cartes VIP — réductions, admission prioritaire et gestion</p>

      </div>

      <button @click="showModal = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter une carte</button>

    </div>



    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

      <div v-for="c in clients" :key="'card-'+c.id" class="page-card p-5"

        :class="c.est_actif ? 'border-amber-500/30' : 'border-white/5 opacity-60'">

        <div class="flex justify-between items-start mb-3">

          <span class="text-2xl">{{ carteIcon(c.type_carte) }}</span>

          <span class="text-xs px-2 py-0.5 rounded-full"

            :class="c.est_actif ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-500/20 text-slate-400'">

            {{ c.est_actif ? 'Active' : 'Inactive' }}

          </span>

        </div>

        <p class="text-white font-semibold">{{ c.patient_nom }}</p>

        <p class="text-xs text-amber-400 font-mono mt-1">{{ c.numero_carte }}</p>

        <p class="text-sm text-slate-400 mt-2">{{ c.type_carte_label }}</p>

        <p class="text-lg font-bold text-amber-300 mt-2">-{{ c.taux_reduction }}%</p>

      </div>

    </div>



    <!-- File d'attente VIP -->
    <div class="page-card p-6 border border-amber-500/30">
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <h3 class="text-white font-semibold">⭐ Salon VIP — file d'attente privilèges</h3>
          <p class="text-slate-500 text-sm">{{ vipQueue.length }} client(s) en attente prioritaire</p>
        </div>
        <router-link to="/waiting-room" class="text-sm text-amber-400 hover:text-amber-300">Voir les deux salles →</router-link>
      </div>
      <div v-if="!vipQueue.length" class="text-slate-500 text-sm">Aucun client privilégié en attente.</div>
      <div v-else class="space-y-2">
        <div
          v-for="e in vipQueue"
          :key="e.id"
          class="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20"
        >
          <div>
            <p class="text-white font-medium">{{ e.patient_nom }}</p>
            <p class="text-xs text-amber-400">{{ e.carte_type }} — {{ e.carte_numero }} (-{{ e.taux_reduction }}%)</p>
            <p class="text-xs text-slate-500">{{ e.statut_label }} · {{ e.motif }}</p>
          </div>
          <ActionMenu :items="queueMenuItems(e)" @action="(k) => onQueueAction(k, e)" />
        </div>
      </div>
    </div>



    <div class="page-card p-4">

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">

        <input v-model="filtre.nom" placeholder="Nom et prénom" class="modal-input text-sm" />

        <select v-model="filtre.type" class="modal-input text-sm">

          <option value="">Tous les types</option>

          <option value="VIP">VIP</option>

          <option value="OR">Or</option>

          <option value="PREMIUM">Premium</option>

          <option value="FAMILLE">Famille</option>

        </select>

        <button @click="load" class="btn-save text-sm">Filtrer</button>

      </div>

    </div>



    <div class="table-card">

      <table class="w-full text-sm">

        <thead>

          <tr class="text-slate-500 text-xs uppercase">

            <th class="p-4 text-left">Patient</th>

            <th class="p-4 text-left">N° carte</th>

            <th class="p-4 text-left">Type</th>

            <th class="p-4 text-left">Réduction</th>

            <th class="p-4 text-left">Statut</th>

            <th class="p-4 text-left">Actions</th>

          </tr>

        </thead>

        <tbody>

          <tr v-for="c in filtered" :key="c.id" class="border-t border-white/5 hover:bg-white/3">

            <td class="p-4 text-white font-medium">{{ c.patient_nom }}</td>

            <td class="p-4 text-amber-400 font-mono text-xs">{{ c.numero_carte }}</td>

            <td class="p-4 text-slate-400">{{ c.type_carte_label }}</td>

            <td class="p-4 text-amber-300 font-bold">-{{ c.taux_reduction }}%</td>

            <td class="p-4">

              <span class="text-xs px-2 py-0.5 rounded-full"

                :class="c.est_actif ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-500/20 text-slate-400'">

                {{ c.est_actif ? 'Active' : 'Inactive' }}

              </span>

            </td>

            <td class="p-4">

              <ActionMenu :items="menuItems(c)" @action="(k) => onAction(k, c)" />

            </td>

          </tr>

        </tbody>

      </table>

    </div>



    <div v-if="showModal" class="modal" @click.self="showModal = false">

      <div class="modal-content max-w-md">

        <h3 class="text-white font-semibold mb-4">Nouvelle carte privilège</h3>

        <form @submit.prevent="create" class="space-y-3">

          <select v-model="form.patient_id" class="modal-input" required>

            <option value="">Patient *</option>

            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>

          </select>

          <input v-model="form.numero_carte" placeholder="N° carte *" class="modal-input" required />

          <select v-model="form.type_carte" class="modal-input">

            <option value="VIP">Carte VIP</option>

            <option value="OR">Carte Or</option>

            <option value="PREMIUM">Carte Premium</option>

            <option value="FAMILLE">Carte Famille</option>

          </select>

          <label class="text-xs text-slate-500">Réduction (%)</label>

          <input v-model.number="form.taux_reduction" type="number" min="1" max="100" class="modal-input" />

          <input v-model="form.date_expiration" type="date" class="modal-input" />

          <textarea v-model="form.notes" placeholder="Notes" class="modal-input" rows="2"></textarea>

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

import { ref, computed, onMounted } from 'vue'

import { useRouter } from 'vue-router'

import { privilegeService, patientService, waitingService, clinicalService } from '../services/api.js'

import ActionMenu from '../components/ActionMenu.vue'



const router = useRouter()

const clients = ref([])

const patients = ref([])

const vipQueue = ref([])

const showModal = ref(false)

const filtre = ref({ nom: '', type: '' })

const form = ref({ patient_id: '', numero_carte: '', type_carte: 'VIP', taux_reduction: 15, date_expiration: '', notes: '' })



const filtered = computed(() => {

  let list = clients.value

  if (filtre.value.nom) {

    const q = filtre.value.nom.toLowerCase()

    list = list.filter(c => c.patient_nom?.toLowerCase().includes(q))

  }

  if (filtre.value.type) list = list.filter(c => c.type_carte === filtre.value.type)

  return list

})



function carteIcon(type) {

  return { VIP: '👑', OR: '🥇', PREMIUM: '💎', FAMILLE: '👨‍👩‍👧' }[type] || '⭐'

}



function menuItems(c) {

  return [

    { key: 'dossier', icon: '📁', label: 'Voir dossier' },

    { key: 'attente', icon: '🪑', label: "Salon VIP (file prioritaire)" },

    { key: 'hospitaliser', icon: '🏥', label: 'Hospitaliser' },

    { key: 'facture', icon: '💰', label: 'Facturation' },

    { key: 'toggle', icon: '⭐', label: c.est_actif ? 'Désactiver carte' : 'Activer carte' },

  ]

}



async function onAction(key, c) {

  if (key === 'dossier') router.push(`/patients/${c.patient_id}`)

  else if (key === 'attente') {

    await waitingService.add({
      patient_id: c.patient_id,
      motif: 'Client privilégié — consultation prioritaire',
      priorite: 'URGENT',
      type_file: 'PRIVILEGE',
    })

    alert(`${c.patient_nom} ajouté au salon VIP`)

    await load()

  } else if (key === 'hospitaliser') {

    try {

      const lits = await clinicalService.lits()

      const libre = lits.find(l => !l.est_occupe)

      if (!libre) { alert('Aucun lit disponible'); return }

      await clinicalService.hospitaliser({

        patient_id: c.patient_id,

        lit_id: libre.id,

        motif_hospitalisation: 'Admission client privilégié',

      })

      alert(`${c.patient_nom} hospitalisé(e) — lit ${libre.code_lit}`)

    } catch (e) { alert(e.message) }

  } else if (key === 'facture') router.push('/bills')

  else if (key === 'toggle') { await privilegeService.toggle(c.id); await load() }

}



function queueMenuItems() {

  return [

    { key: 'consultation', icon: '🩺', label: 'En consultation' },

    { key: 'terminer', icon: '✓', label: 'Terminer' },

    { key: 'supprimer', icon: '🗑️', label: 'Retirer', danger: true },

  ]

}



async function onQueueAction(key, e) {

  if (key === 'consultation') await waitingService.setStatut(e.id, 'EN_CONSULTATION')

  else if (key === 'terminer') await waitingService.setStatut(e.id, 'TERMINE')

  else if (key === 'supprimer') await waitingService.remove(e.id)

  await load()

}



async function load() {

  clients.value = await privilegeService.list()

  patients.value = await patientService.list()

  vipQueue.value = await waitingService.list('PRIVILEGE')

}



async function create() {

  const payload = { ...form.value, patient_id: Number(form.value.patient_id) }

  if (!payload.date_expiration) delete payload.date_expiration

  await privilegeService.create(payload)

  showModal.value = false

  form.value = { patient_id: '', numero_carte: '', type_carte: 'VIP', taux_reduction: 15, date_expiration: '', notes: '' }

  await load()

}



onMounted(load)

</script>

