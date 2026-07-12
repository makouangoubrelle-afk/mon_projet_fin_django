<template>

  <div class="space-y-6">

    <div class="page-heading">

      <div>

        <h2 class="text-xl font-bold text-white">{{ isPatient ? '🔬 Mon laboratoire' : '🔬 Laboratoire' }}</h2>

        <p class="text-slate-400 text-sm">{{ analyses.length }} analyses</p>

      </div>

      <button v-if="!isPatient" @click="showAdd = true" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Nouvelle analyse</button>

    </div>



    <div v-if="patientError" class="page-card p-4 border border-amber-500/30 bg-amber-500/10">

      <p class="text-amber-200 text-sm">{{ patientError }}</p>

      <router-link to="/mon-espace" class="inline-block mt-2 text-sm text-teal-400">Accéder par nom →</router-link>

    </div>



    <div class="table-card">

      <table class="w-full text-sm">

        <thead>

          <tr class="text-slate-500 text-xs uppercase">

            <th v-if="!isPatient" class="p-4 text-left">Patient</th>

            <th class="p-4 text-left">Examen</th>

            <th class="p-4 text-left">Statut</th>

            <th class="p-4 text-left">Résultat</th>

            <th class="p-4 text-left">QR Patient</th>

            <th v-if="!isPatient" class="p-4 text-left">Actions</th>

          </tr>

        </thead>

        <tbody>

          <tr v-for="a in analyses" :key="a.id" class="border-t border-white/5 hover:bg-white/3">

            <td v-if="!isPatient" class="p-4 text-white">{{ a.patient_nom || '—' }}</td>

            <td class="p-4 text-slate-300">{{ a.examen_nom }}</td>

            <td class="p-4"><span class="text-xs px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300">{{ a.statut }}</span></td>

            <td class="p-4 text-slate-400 max-w-xs truncate">{{ a.resultat || '—' }}</td>

            <td class="p-4">

              <button v-if="a.patient_qr_code" @click="showQr(a)" class="inline-block">

                <img v-if="qrThumbs[a.id]" :src="qrThumbs[a.id]" alt="QR" class="w-10 h-10 rounded bg-white p-0.5" />

                <span v-else class="text-xs text-teal-400">QR</span>

              </button>

              <span v-else class="text-slate-600">—</span>

            </td>

            <td v-if="!isPatient" class="p-4">

              <ActionMenu :items="labMenu(a)" @action="(k) => onAction(k, a)" />

            </td>

          </tr>

        </tbody>

      </table>

    </div>



    <div v-if="showAdd || editing" class="modal" @click.self="closeModal">

      <div class="modal-content max-w-md">

        <h3 class="text-white font-semibold mb-4">{{ editing ? 'Modifier analyse' : 'Commander une analyse' }}</h3>

        <form @submit.prevent="save" class="space-y-3">

          <select v-if="!editing" v-model="form.patient_id" class="modal-input" required>

            <option value="">Patient *</option>

            <option v-for="p in patients" :key="p.id" :value="p.id">{{ p.nom }} {{ p.prenom }}</option>

          </select>

          <input v-model="form.examen_nom" placeholder="Nom de l'examen *" class="modal-input" required />

          <textarea v-model="form.resultat" placeholder="Résultat (optionnel)" class="modal-input" rows="3"></textarea>

          <div class="modal-buttons">

            <button type="button" @click="closeModal" class="btn-cancel">Annuler</button>

            <button type="submit" class="btn-save">Enregistrer</button>

          </div>

        </form>

      </div>

    </div>



    <div v-if="qrAnalyse" class="modal" @click.self="qrAnalyse = null">

      <div class="modal-content max-w-sm text-center">

        <h3 class="text-white font-semibold mb-2">{{ qrAnalyse.patient_nom }}</h3>

        <p class="text-xs text-slate-500 mb-4">QR Code — Analyse : {{ qrAnalyse.examen_nom }}</p>

        <img v-if="qrImage" :src="qrImage" alt="QR" class="mx-auto w-48 h-48 bg-white p-3 rounded-xl" />

        <p class="text-[10px] text-slate-600 font-mono mt-3 break-all">{{ qrAnalyse.patient_qr_code }}</p>

      </div>

    </div>

  </div>

</template>



<script setup>

import { ref, reactive, computed, onMounted } from 'vue'

import QRCode from 'qrcode'

import { labService, patientService, getUser, resolvePatientId } from '../services/api.js'

import ActionMenu from '../components/ActionMenu.vue'



const user = getUser()

const isPatient = computed(() => user?.role === 'PATIENT')

const analyses = ref([])

const patients = ref([])

const showAdd = ref(false)

const editing = ref(null)

const form = ref({ patient_id: '', examen_nom: '', resultat: '' })

const qrAnalyse = ref(null)

const qrImage = ref('')

const qrThumbs = reactive({})

const patientError = ref('')



function labMenu(a) {

  const items = [

    { key: 'edit', icon: '✏️', label: 'Modifier' },

    { key: 'qr', icon: '📱', label: 'QR Code patient' },

    { key: 'print', icon: '🖨️', label: 'Imprimer résultat' },

    { key: 'delete', icon: '🗑️', label: 'Supprimer', danger: true },

  ]

  if (a.statut !== 'VALIDE') items.unshift({ key: 'valider', icon: '✓', label: 'Valider' })

  return items

}



function closeModal() { showAdd.value = false; editing.value = null }



async function showQr(a) {

  qrAnalyse.value = a

  qrImage.value = await QRCode.toDataURL(`SGHL-PATIENT:${a.patient_qr_code}`, { width: 256 })

}



async function loadQrThumbs(list) {

  for (const a of list) {

    if (a.patient_qr_code && !qrThumbs[a.id]) {

      qrThumbs[a.id] = await QRCode.toDataURL(`SGHL-PATIENT:${a.patient_qr_code}`, { width: 80, margin: 0 })

    }

  }

}



async function onAction(key, a) {

  if (key === 'valider') await labService.valider(a.id)

  else if (key === 'edit') { editing.value = a; form.value = { examen_nom: a.examen_nom, resultat: a.resultat || '' }; showAdd.value = true }

  else if (key === 'qr') showQr(a)

  else if (key === 'print') window.print()

  else if (key === 'delete' && confirm('Supprimer ?')) await labService.delete(a.id)

  await load()

}



async function load() {

  patientError.value = ''

  let patientId = null

  if (isPatient.value) {

    patientId = await resolvePatientId()

    if (!patientId) {

      patientError.value = 'Dossier patient introuvable pour votre compte. Utilisez Mon espace patient avec votre nom.'

      analyses.value = []

      return

    }

  }

  const list = await labService.list(patientId)

  analyses.value = list

  await loadQrThumbs(list)

  if (!isPatient.value) patients.value = await patientService.list()

}



async function save() {

  if (editing.value) {

    await labService.update(editing.value.id, { examen_nom: form.value.examen_nom, resultat: form.value.resultat })

  } else {

    await labService.create({ patient_id: Number(form.value.patient_id), examen_nom: form.value.examen_nom, resultat: form.value.resultat })

  }

  closeModal()

  await load()

}



onMounted(load)

</script>

