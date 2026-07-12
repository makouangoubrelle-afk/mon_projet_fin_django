<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">🏥 Paramètres de l'hôpital</h2>
        <p class="text-slate-400 text-sm">Identité, coordonnées et sauvegarde des données</p>
      </div>
    </div>

    <div v-if="msg" class="p-3 rounded-xl bg-teal-500/10 border border-teal-500/30 text-teal-300 text-sm">{{ msg }}</div>
    <div v-if="error" class="text-red-400 text-sm">{{ error }}</div>

    <form v-if="form" class="page-card p-6 grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="save">
      <label class="form-field md:col-span-2"><span>Nom de l'établissement</span>
        <input v-model="form.nom_hopital" class="modal-input" required /></label>
      <label class="form-field"><span>Téléphone</span><input v-model="form.telephone" class="modal-input" /></label>
      <label class="form-field"><span>Email</span><input v-model="form.email" type="email" class="modal-input" /></label>
      <label class="form-field md:col-span-2"><span>Adresse</span><textarea v-model="form.adresse" class="modal-input" rows="2" /></label>
      <label class="form-field"><span>Directeur</span><input v-model="form.directeur" class="modal-input" /></label>
      <label class="form-field"><span>Horaires</span><input v-model="form.horaires_ouverture" class="modal-input" /></label>
      <label class="form-field"><span>Devise</span><input v-model="form.devise" class="modal-input" /></label>
      <label class="form-field"><span>Fuseau horaire</span><input v-model="form.fuseau_horaire" class="modal-input" /></label>
      <div class="md:col-span-2 flex justify-end">
        <button type="submit" class="btn-save" :disabled="saving">{{ saving ? '…' : 'Enregistrer' }}</button>
      </div>
    </form>

    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">💾 Sauvegarde des données</h3>
      <p class="text-slate-400 text-sm mb-4">Crée une copie de la base PostgreSQL dans le dossier <code class="text-teal-400">backups/</code> (fichier .sql).</p>
      <button type="button" class="btn-save" :disabled="backing" @click="doBackup">
        {{ backing ? 'Sauvegarde…' : 'Lancer une sauvegarde' }}
      </button>
      <ul v-if="backups.length" class="mt-4 space-y-2 text-sm">
        <li v-for="b in backups" :key="b.filename" class="flex justify-between p-2 rounded-lg bg-white/5 text-slate-300">
          <span>{{ b.filename }}</span>
          <span class="text-slate-500">{{ (b.size_bytes / 1024).toFixed(0) }} Ko</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { coreService } from '../services/api.js'

const form = ref(null)
const backups = ref([])
const saving = ref(false)
const backing = ref(false)
const msg = ref('')
const error = ref('')

async function load() {
  try {
    form.value = await coreService.settings()
    const res = await coreService.backups()
    backups.value = res.backups || []
  } catch (e) {
    error.value = e.message
  }
}

async function save() {
  saving.value = true
  msg.value = ''
  try {
    form.value = await coreService.updateSettings(form.value)
    msg.value = 'Paramètres enregistrés.'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function doBackup() {
  backing.value = true
  try {
    const res = await coreService.backup()
    msg.value = `Sauvegarde créée : ${res.filename}`
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    backing.value = false
  }
}

onMounted(load)
</script>
