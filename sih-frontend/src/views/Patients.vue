<template>

  <div class="space-y-6">

    <div class="page-heading">

      <div>

        <h2 class="text-xl font-bold text-white">{{ isPatientView ? '👤 Mon dossier' : '👥 Patients' }}</h2>

        <p class="text-slate-400 text-sm">{{ isPatientView ? 'Votre statut, produits et QR code' : `${filteredPatients.length} patient(s) enregistré(s)` }}</p>

      </div>

      <div v-if="!isPatientView" class="flex gap-2">

        <button @click="exportPdf" class="px-4 py-2.5 rounded-xl text-sm font-medium bg-red-600/20 text-red-300 border border-red-500/30 hover:bg-red-600/30">📄 PDF</button>

        <button @click="exportExcel" class="px-4 py-2.5 rounded-xl text-sm font-medium bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30">📊 Excel</button>

        <button @click="openModal" class="action-button px-5 py-2.5 rounded-xl text-sm font-medium">+ Ajouter un patient</button>

      </div>

    </div>



    <div v-if="isPatientView && patientError" class="page-card p-4 border border-amber-500/30 bg-amber-500/10">

      <p class="text-amber-200 text-sm">{{ patientError }}</p>

      <router-link to="/mon-espace" class="inline-block mt-2 text-sm text-teal-400">Accéder par nom →</router-link>

    </div>



    <div v-if="!isPatientView" class="page-card p-4 space-y-3">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <input
          v-model="filtre.nom"
          type="text"
          placeholder="Rechercher par nom ou prénom…"
          class="modal-input text-sm"
        />
        <input
          v-model="filtre.identite"
          type="text"
          placeholder="N° dossier ou identité…"
          class="modal-input text-sm"
        />
        <form @submit.prevent="chercherParEmail" class="flex gap-2">
          <input
            v-model="searchEmail"
            type="text"
            placeholder="Email portail (ex: patient@sghl.com)"
            class="modal-input text-sm flex-1"
          />
          <button type="submit" class="btn-save text-sm whitespace-nowrap" :disabled="searching">
            {{ searching ? '…' : 'Chercher' }}
          </button>
        </form>
      </div>
      <p v-if="searchError" class="text-red-400 text-sm">{{ searchError }}</p>
      <p v-if="loading" class="text-slate-500 text-sm">Chargement de la liste…</p>
      <p v-else-if="!filteredPatients.length" class="text-slate-500 text-sm">Aucun patient trouvé. Ajoutez-en un avec « + Ajouter un patient ».</p>
    </div>



    <div class="table-card hidden md:block">

      <div class="overflow-x-auto">

        <table class="w-full text-sm">

          <thead>

            <tr class="text-slate-500 text-xs uppercase">

              <th class="text-left p-4">N° identité</th>

              <th class="text-left p-4">Nom et prénom</th>

              <th v-if="!isPatientView" class="text-left p-4">Email portail</th>

              <th v-if="!isPatientView" class="text-left p-4">Sexe</th>

              <th class="text-left p-4">GSM</th>

              <th class="text-left p-4">Âge</th>

              <th class="text-left p-4">Statut</th>

              <th class="text-left p-4">Produits</th>

              <th class="text-left p-4">QR Code</th>

              <th v-if="!isPatientView" class="text-left p-4">Chat</th>

              <th v-if="!isPatientView" class="text-left p-4">Actions</th>

            </tr>

          </thead>

          <tbody>

            <tr
              v-for="p in filteredPatients"
              :key="p.id"
              class="border-t border-white/5 hover:bg-white/3 cursor-pointer"
              @click="openDossier(p)"
            >

              <td class="p-4 text-teal-400 font-mono text-xs">{{ p.numero_identite || p.sgl_id }}</td>

              <td class="p-4 text-white font-medium">{{ p.nom }} {{ p.prenom }}</td>

              <td v-if="!isPatientView" class="p-4" @click.stop>
                <button
                  v-if="p.email"
                  type="button"
                  @click="showPortalInfo(p)"
                  class="text-xs text-teal-400 hover:text-teal-300 font-mono text-left"
                  :title="'Accès portail patient'"
                >
                  {{ p.email }}
                </button>
                <span v-else class="text-xs text-slate-500">—</span>
              </td>

              <td v-if="!isPatientView" class="p-4 text-slate-400">{{ p.genre_label }}</td>

              <td class="p-4 text-slate-400">{{ p.telephone }}</td>

              <td class="p-4 text-slate-400">{{ p.age ?? '—' }}</td>

              <td class="p-4">

                <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="statutClass(p.statut)">

                  {{ p.statut_label || '—' }}

                </span>

              </td>

              <td class="p-4" @click.stop>

                <button @click="showProduits(p)" class="text-xs text-amber-400 hover:text-amber-300">

                  {{ p.nb_produits || 0 }} produit(s)

                </button>

              </td>

              <td class="p-4" @click.stop>

                <button @click="showQr(p)" class="inline-block">

                  <img v-if="qrThumbs[p.id]" :src="qrThumbs[p.id]" alt="QR" class="w-10 h-10 rounded bg-white p-0.5" />

                  <span v-else class="text-xs text-teal-400">Voir QR</span>

                </button>

              </td>

              <td v-if="!isPatientView" class="p-4" @click.stop>
                <button
                  type="button"
                  @click="selectChatPatient(p)"
                  class="text-xs px-3 py-1.5 rounded-lg transition"
                  :class="selectedChatPatient?.id === p.id
                    ? 'bg-teal-500/30 text-teal-100 border border-teal-500/40'
                    : 'bg-white/5 text-teal-300 hover:bg-teal-500/15'"
                >
                  💬
                  <span v-if="chatUnread[p.id]" class="ml-1 px-1.5 rounded-full bg-red-500/40 text-red-100">{{ chatUnread[p.id] }}</span>
                </button>
              </td>

              <td v-if="!isPatientView" class="p-4" @click.stop>

                <ActionMenu :items="patientMenu" @action="(k) => onPatientAction(k, p)" />

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>



    <!-- Liste mobile (cartes) -->
    <div v-if="!loading" class="md:hidden space-y-3">
      <p v-if="!filteredPatients.length" class="text-slate-500 text-sm px-1">Aucun patient trouvé.</p>
      <button
        v-for="p in filteredPatients"
        :key="`mobile-${p.id}`"
        type="button"
        class="page-card w-full p-4 text-left"
        @click="openDossier(p)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-white font-semibold truncate">{{ p.nom }} {{ p.prenom }}</p>
            <p class="text-teal-400 text-xs font-mono mt-1">{{ p.numero_identite || p.sgl_id }}</p>
          </div>
          <span class="text-xs px-2 py-0.5 rounded-full font-medium shrink-0" :class="statutClass(p.statut)">
            {{ p.statut_label || '—' }}
          </span>
        </div>
        <div class="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-400">
          <span>📱 {{ p.telephone || '—' }}</span>
          <span>🎂 {{ p.age ?? '—' }} ans</span>
          <span v-if="!isPatientView" class="col-span-2 truncate">✉️ {{ p.email || '—' }}</span>
        </div>
        <div v-if="!isPatientView" class="mt-3 flex flex-wrap gap-2" @click.stop>
          <button type="button" class="text-xs px-3 py-1.5 rounded-lg bg-teal-500/15 text-teal-200" @click="selectChatPatient(p)">
            💬 Chat
          </button>
          <button type="button" class="text-xs px-3 py-1.5 rounded-lg bg-white/5 text-slate-300" @click="showQr(p)">QR</button>
          <button type="button" class="text-xs px-3 py-1.5 rounded-lg bg-white/5 text-slate-300" @click="showProduits(p)">Produits</button>
        </div>
      </button>
    </div>



    <!-- Chat médical global -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div v-if="!isPatientView" class="hidden lg:flex page-card p-4 lg:col-span-1 flex-col max-h-[600px]">
        <h3 class="text-white font-semibold mb-1 flex items-center gap-2">
          📥 Conversations patients
          <span v-if="totalChatUnread" class="text-xs px-2 py-0.5 rounded-full bg-red-500/30 text-red-200">{{ totalChatUnread }}</span>
        </h3>
        <p class="text-slate-500 text-xs mb-3">Messages et demandes de rendez-vous</p>
        <div class="flex-1 overflow-y-auto space-y-2">
          <button
            v-for="item in chatInbox"
            :key="item.patient_id"
            type="button"
            @click="selectChatPatientById(item.patient_id, item.patient_nom)"
            class="w-full text-left p-3 rounded-xl border transition"
            :class="selectedChatPatient?.id === item.patient_id
              ? 'border-teal-500/40 bg-teal-500/10'
              : 'border-white/10 bg-white/5 hover:bg-white/10'"
          >
            <div class="flex justify-between gap-2">
              <span class="text-white text-sm font-medium">{{ item.patient_nom }}</span>
              <span v-if="item.non_lus_equipe" class="shrink-0 w-5 h-5 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center">{{ item.non_lus_equipe }}</span>
            </div>
            <p class="text-slate-500 text-xs mt-1 truncate">{{ item.dernier_message }}</p>
            <p class="text-slate-600 text-[10px] mt-1">{{ item.sgl_id }}</p>
          </button>
          <p v-if="!chatInbox.length" class="text-slate-500 text-sm text-center py-6">Aucune conversation. Cliquez 💬 sur un patient.</p>
        </div>
      </div>

      <div :class="isPatientView ? 'lg:col-span-3' : 'lg:col-span-2'">
        <PatientGlobalChat
          :patient-id="activeChatPatientId"
          :patient-nom="activeChatPatientNom"
          @message-sent="loadChatInbox"
        />
      </div>
    </div>



    <!-- Modal Ajouter un patient -->

    <div v-if="showModal" class="modal" @click.self="showModal = false">

      <div class="modal-content max-w-2xl max-h-[90vh] overflow-y-auto">

        <h3 class="text-white font-semibold text-lg mb-5">Ajouter un patient</h3>

        <form @submit.prevent="createPatient" class="space-y-4">

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

            <label class="form-field">

              <span>Date de naissance</span>

              <input v-model="form.date_naissance" type="date" class="modal-input" @input="onDateChange" />

              <p class="text-slate-500 text-xs mt-1">Optionnel si vous renseignez l'âge.</p>

            </label>

            <label class="form-field">

              <span>Nom et prénom *</span>

              <input v-model="form.nom_complet" placeholder="Ex: FATIMA DEMO" class="modal-input" required />

            </label>

            <label class="form-field sm:col-span-2">

              <span>Email portail patient</span>

              <input v-model="form.email" type="email" placeholder="Optionnel — ex: prenom.nom@patient.sghl.com (généré auto si vide)" class="modal-input" />

              <p class="text-slate-500 text-xs mt-1">Cet email permet au patient de se connecter sur /login et d'accéder à Mon espace.</p>

            </label>

            <label class="form-field">

              <span>Sexe *</span>

              <select v-model="form.genre" class="modal-input" required>

                <option value="F">Femme</option>

                <option value="M">Homme</option>

              </select>

            </label>

            <label class="form-field">

              <span>N° identité *</span>

              <input v-model="form.numero_identite" placeholder="Ex: G253135" class="modal-input" required />

            </label>

            <label class="form-field">

              <span>GSM *</span>

              <input v-model="form.telephone" placeholder="+242 06 812 34 56" class="modal-input" required />

            </label>

            <label class="form-field">

              <span>Âge *</span>

              <input
                v-model.number="form.age"
                type="number"
                min="0"
                max="130"
                required
                placeholder="Ex: 35"
                class="modal-input"
                @input="onAgeInput"
              />

              <p class="text-slate-500 text-xs mt-1">Saisissez l'âge en années — la date de naissance se calcule automatiquement.</p>

            </label>

            <label class="form-field sm:col-span-2">

              <span>Adresse *</span>

              <input v-model="form.adresse" placeholder="Adresse complète" class="modal-input" required />

            </label>

            <label class="form-field">

              <span>Situation *</span>

              <select v-model="form.situation_familiale" class="modal-input" required>

                <option value="Célibataire">Célibataire</option>

                <option value="Marié(e)">Marié(e)</option>

                <option value="Divorcé(e)">Divorcé(e)</option>

                <option value="Veuf(ve)">Veuf(ve)</option>

              </select>

            </label>

            <label class="form-field">

              <span>Enfants *</span>

              <input v-model.number="form.nombre_enfants" type="number" min="0" class="modal-input" required />

            </label>

            <label class="form-field">

              <span>Assurance</span>

              <select v-model="form.assurance_id" class="modal-input">

                <option value="">Sans assurance</option>

                <option v-for="a in assurances" :key="a.id" :value="a.id">{{ a.nom }}</option>

              </select>

            </label>

            <label class="form-field">

              <span>Profession</span>

              <input v-model="form.profession" placeholder="Profession" class="modal-input" />

            </label>

            <label class="form-field">

              <span>Poids en kg</span>

              <input v-model.number="form.poids_kg" type="number" step="0.1" min="0" placeholder="70" class="modal-input" />

            </label>

            <label class="form-field">

              <span>Taille (ex: 1,73)</span>

              <input v-model.number="form.taille_m" type="number" step="0.01" min="0" max="3" placeholder="1.73" class="modal-input" />

            </label>

            <label class="form-field">

              <span>Groupe sanguin</span>

              <select v-model="form.groupe_sanguin" class="modal-input">

                <option value="">—</option>

                <option v-for="g in groupesSanguins" :key="g" :value="g">{{ g }}</option>

              </select>

            </label>

            <label class="form-field md:col-span-2">
              <span>Allergies</span>
              <input v-model="form.allergies" placeholder="Pénicilline, arachides…" class="modal-input" />
            </label>
            <label class="form-field md:col-span-2">
              <span>Antécédents médicaux</span>
              <textarea v-model="form.antecedents_medicaux" rows="2" class="modal-input" placeholder="Diabète, hypertension…" />
            </label>
            <label class="form-field">
              <span>Contact urgence — nom</span>
              <input v-model="form.contact_urgence_nom" class="modal-input" />
            </label>
            <label class="form-field">
              <span>Contact urgence — téléphone</span>
              <input v-model="form.contact_urgence_telephone" class="modal-input" />
            </label>
            <label class="form-field md:col-span-2">
              <span>Lien (parent, conjoint…)</span>
              <input v-model="form.contact_urgence_lien" class="modal-input" />
            </label>

          </div>

          <div v-if="error" class="text-red-400 text-sm">{{ error }}</div>

          <div class="modal-buttons pt-2">

            <button type="button" @click="showModal = false" class="btn-cancel">Annuler</button>

            <button type="submit" class="btn-save" :disabled="saving">{{ saving ? 'Enregistrement...' : 'Enregistrer' }}</button>

          </div>

        </form>

      </div>

    </div>



    <div v-if="qrPatient" class="modal" @click.self="qrPatient = null">

      <div class="modal-content max-w-sm text-center">

        <h3 class="text-white font-semibold mb-2">{{ qrPatient.nom }} {{ qrPatient.prenom }}</h3>

        <p class="text-xs text-slate-500 mb-4">Code QR — SGHL</p>

        <img v-if="qrImage" :src="qrImage" alt="QR" class="mx-auto w-48 h-48 bg-white p-3 rounded-xl" />

        <p class="text-[10px] text-slate-600 font-mono mt-3 break-all">{{ qrPatient.qr_code }}</p>

      </div>

    </div>



    <div v-if="produitsPatient" class="modal" @click.self="produitsPatient = null">

      <div class="modal-content max-w-lg">

        <h3 class="text-white font-semibold mb-1">Produits / Médicaments</h3>

        <p class="text-sm text-slate-400 mb-4">{{ produitsPatient.nom }} {{ produitsPatient.prenom }}</p>

        <div v-if="produitsLoading" class="text-slate-500 text-sm">Chargement...</div>

        <div v-else-if="!produitsList.length" class="text-slate-500 text-sm">Aucun produit dispensé.</div>

        <table v-else class="w-full text-sm">

          <thead>

            <tr class="text-slate-500 text-xs uppercase">

              <th class="p-2 text-left">Médicament</th>

              <th class="p-2 text-left">Qté</th>

              <th class="p-2 text-left">Montant</th>

              <th class="p-2 text-left">Payé</th>

            </tr>

          </thead>

          <tbody>

            <tr v-for="pr in produitsList" :key="pr.id" class="border-t border-white/5">

              <td class="p-2 text-white">{{ pr.medicament }}</td>

              <td class="p-2 text-slate-400">{{ pr.quantite }}</td>

              <td class="p-2 text-slate-300">{{ formatMoney(pr.montant) }}</td>

              <td class="p-2"><span :class="pr.est_paye ? 'text-green-400' : 'text-amber-400'">{{ pr.est_paye ? 'Oui' : 'Non' }}</span></td>

            </tr>

          </tbody>

        </table>

      </div>

    </div>



    <!-- Accès portail patient -->
    <div v-if="portalInfo" class="modal" @click.self="portalInfo = null">
      <div class="modal-content max-w-md">
        <h3 class="text-white font-semibold mb-1">🧑 Accès portail patient</h3>
        <p class="text-sm text-slate-400 mb-4">{{ portalInfo.nom }} {{ portalInfo.prenom }}</p>
        <div class="p-4 rounded-xl bg-teal-500/10 border border-teal-500/30 mb-4">
          <p class="text-xs text-slate-500 uppercase mb-1">Email de connexion</p>
          <p class="text-teal-300 font-mono text-sm break-all">{{ portalInfo.email }}</p>
        </div>
        <ol class="text-sm text-slate-400 space-y-2 mb-4 list-decimal list-inside">
          <li>Le patient va sur la page <strong class="text-white">Connexion</strong></li>
          <li>Il entre cet email et reçoit un code OTP</li>
          <li>Il accède à <strong class="text-white">Mon espace</strong> (statut, ordonnances, labo…)</li>
        </ol>
        <div class="flex gap-2">
          <button type="button" @click="copyPortalEmail" class="btn-save flex-1 text-sm">
            {{ copiedEmail ? 'Copié ✓' : 'Copier l\'email' }}
          </button>
          <button type="button" @click="portalInfo = null" class="btn-cancel flex-1 text-sm">Fermer</button>
        </div>
      </div>
    </div>

  </div>

</template>



<script setup>

import { ref, computed, onMounted, onUnmounted, reactive, watch, onActivated } from 'vue'

import { useRouter, useRoute } from 'vue-router'

import QRCode from 'qrcode'

import { patientService, waitingService, chatService, getUser, resolvePatientId, isPatientAccess, isStaffUser } from '../services/api.js'

import ActionMenu from '../components/ActionMenu.vue'
import PatientGlobalChat from '../components/PatientGlobalChat.vue'
import { usePageFlow } from '../composables/usePageFlow.js'

const { goNextIfAuto } = usePageFlow()



const router = useRouter()
const route = useRoute()

const user = computed(() => getUser())

const isPatientView = computed(() => isPatientAccess() && !isStaffUser())

const patients = ref([])

const assurances = ref([])

const showModal = ref(false)

const saving = ref(false)

const error = ref('')

const filtre = ref({ nom: '', identite: '' })

const qrPatient = ref(null)

const qrImage = ref('')

const qrThumbs = reactive({})

const produitsPatient = ref(null)

const produitsList = ref([])

const produitsLoading = ref(false)

const patientError = ref('')

const searchEmail = ref('')

const searchError = ref('')

const searching = ref(false)
const loading = ref(false)

const portalInfo = ref(null)

const copiedEmail = ref(false)

const selectedChatPatient = ref(null)

const chatInbox = ref([])

const chatUnread = ref({})

let inboxPollTimer = null

const totalChatUnread = computed(() =>
  Object.values(chatUnread.value).reduce((a, b) => a + (b || 0), 0)
)

const activeChatPatientId = computed(() => {
  if (isPatientView.value && filteredPatients.value[0]?.id) {
    return filteredPatients.value[0].id
  }
  return selectedChatPatient.value?.id || null
})

const activeChatPatientNom = computed(() => {
  if (isPatientView.value && filteredPatients.value[0]) {
    const p = filteredPatients.value[0]
    return `${p.nom} ${p.prenom}`
  }
  return selectedChatPatient.value
    ? `${selectedChatPatient.value.nom} ${selectedChatPatient.value.prenom}`
    : ''
})

const patientMenu = [

  { key: 'dossier', icon: '📁', label: 'Voir dossier' },

  { key: 'espace', icon: '🧑', label: 'Accès portail' },

    { key: 'attente', icon: '🪑', label: "Salle d'attente / VIP" },

  { key: 'qr', icon: '📱', label: 'QR Code' },

  { key: 'produits', icon: '💊', label: 'Voir produits' },

  { key: 'chat', icon: '💬', label: 'Ouvrir le chat' },

]

const groupesSanguins = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']



const emptyForm = () => ({

  nom_complet: '', email: '', date_naissance: '', age: null, genre: 'F', numero_identite: '', telephone: '',

  adresse: '', situation_familiale: 'Célibataire', nombre_enfants: 0, assurance_id: '',

  profession: '', poids_kg: null, taille_m: null, groupe_sanguin: '',
  allergies: '', antecedents_medicaux: '',
  contact_urgence_nom: '', contact_urgence_telephone: '', contact_urgence_lien: '',

})

const form = ref(emptyForm())



const filteredPatients = computed(() => {

  let list = patients.value

  if (isPatientView.value && user.value?.patient_id) {

    list = list.filter(p => p.id === user.value.patient_id)

  }

  if (filtre.value.nom) {

    const q = filtre.value.nom.toLowerCase()

    list = list.filter(p =>
      `${p.nom} ${p.prenom}`.toLowerCase().includes(q) ||
      (p.email || '').toLowerCase().includes(q)
    )

  }

  if (filtre.value.identite) {

    list = list.filter(p => (p.numero_identite || p.sgl_id || '').includes(filtre.value.identite))

  }

  return list

})



function statutClass(statut) {

  const map = {

    URGENCE: 'bg-red-500/20 text-red-300',

    HOSPITALISE: 'bg-purple-500/20 text-purple-300',

    EN_ATTENTE: 'bg-amber-500/20 text-amber-300',

    EN_CONSULTATION: 'bg-blue-500/20 text-blue-300',

    EXTERNE: 'bg-slate-500/20 text-slate-400',

  }

  return map[statut] || 'bg-teal-500/20 text-teal-300'

}



function formatMoney(n) {

  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(n || 0) + ' FC'

}



async function loadQrThumbs(list) {
  for (const p of list) {
    if (p.qr_code && !qrThumbs[p.id]) {
      try {
        qrThumbs[p.id] = await QRCode.toDataURL(`SGHL-PATIENT:${p.qr_code}`, { width: 80, margin: 0 })
      } catch (e) {
        console.warn('[Patients] QR', p.id, e)
      }
    }
  }
}

function openDossier(p) {
  if (!p?.id || isPatientView.value) return
  router.push({ name: 'PatientDetail', params: { id: String(p.id) } })
}

async function onPatientAction(key, p) {
  try {
    if (key === 'dossier') {
      router.push({ name: 'PatientDetail', params: { id: String(p.id) } })
    } else if (key === 'espace') {
      showPortalInfo(p)
    } else if (key === 'attente') {
      const res = await waitingService.add({ patient_id: p.id, motif: 'Consultation' })
      alert(
        res.type_file === 'PRIVILEGE'
          ? `${p.nom} ajouté au salon VIP (client privilégié)`
          : `${p.nom} ajouté à la salle d'attente standard`
      )
      await load()
    } else if (key === 'qr') {
      await showQr(p)
    } else if (key === 'produits') {
      await showProduits(p)
    } else if (key === 'chat') {
      selectChatPatient(p)
    }
  } catch (e) {
    console.error('[Patients] action', key, e)
    alert(`Action impossible : ${e.message}`)
  }
}



async function showQr(p) {

  qrPatient.value = p

  qrImage.value = await QRCode.toDataURL(`SGHL-PATIENT:${p.qr_code || p.sgl_id}`, { width: 256 })

}



async function showProduits(p) {

  produitsPatient.value = p

  produitsLoading.value = true

  try {

    produitsList.value = await patientService.produits(p.id)

  } finally {

    produitsLoading.value = false

  }

}



function exportExcel() {
  import('../utils/exportExcel.js').then(({ exportPatientsExcel }) => {
    exportPatientsExcel(filteredPatients.value)
  }).catch((e) => alert(`Export Excel impossible : ${e.message}`))
}

function exportPdf() {
  import('../utils/exportExcel.js').then(({ exportPatientsPdf }) => {
    exportPatientsPdf(filteredPatients.value)
  }).catch((e) => alert(`Export PDF impossible : ${e.message}`))
}



function calcAgeFromIso(iso) {
  if (!iso) return null
  const [y, m, d] = iso.split('-').map(Number)
  if (!y || !m || !d) return null
  const today = new Date()
  let age = today.getFullYear() - y
  const month = today.getMonth() + 1
  const day = today.getDate()
  if (month < m || (month === m && day < d)) age--
  return age >= 0 ? age : null
}

function isoFromAge(age) {
  const n = Number(age)
  if (!Number.isFinite(n) || n < 0 || n > 130) return ''
  const year = new Date().getFullYear() - Math.floor(n)
  return `${year}-06-15`
}

function onAgeInput() {
  const n = form.value.age
  if (n != null && n !== '' && Number(n) >= 0) {
    form.value.date_naissance = isoFromAge(n)
  }
}

function onDateChange() {
  const a = calcAgeFromIso(form.value.date_naissance)
  if (a != null) form.value.age = a
}

function splitName(full) {

  const parts = full.trim().split(/\s+/)

  if (parts.length === 1) return { nom: parts[0], prenom: '—' }

  return { nom: parts[0], prenom: parts.slice(1).join(' ') }

}

function openModal() {
  form.value = emptyForm()
  error.value = ''
  showModal.value = true
  if (!assurances.value.length) loadAssurances()
}



function showPortalInfo(p) {
  if (!p?.email) {
    alert('Aucun email portail pour ce patient. Utilisez « Sync portails patients » dans Admin → Structure.')
    return
  }
  copiedEmail.value = false
  portalInfo.value = p
}



async function copyPortalEmail() {
  if (!portalInfo.value?.email) return
  try {
    await navigator.clipboard.writeText(portalInfo.value.email)
    copiedEmail.value = true
    setTimeout(() => { copiedEmail.value = false }, 2000)
  } catch {
    alert(portalInfo.value.email)
  }
}



async function chercherParEmail() {
  const q = searchEmail.value.trim()
  if (!q) return
  searching.value = true
  searchError.value = ''
  try {
    const profil = await patientService.parEmail(q)
    if (profil) {
      const exists = patients.value.some((p) => p.id === profil.id)
      if (!exists) patients.value = [profil, ...patients.value]
      filtre.value.nom = `${profil.nom} ${profil.prenom}`
      await loadQrThumbs([profil])
    } else {
      searchError.value = 'Aucun patient avec cet email.'
    }
  } catch (e) {
    searchError.value = e.message || 'Patient introuvable.'
  } finally {
    searching.value = false
  }
}



async function loadAssurances() {
  try {
    assurances.value = await patientService.assurances()
  } catch { /* ignore */ }
}



function selectChatPatient(p) {
  if (!p?.id) return
  selectedChatPatient.value = p
  if (chatUnread.value[p.id]) chatUnread.value[p.id] = 0
}

function selectChatPatientById(id, nom) {
  const p = patients.value.find((x) => x.id === id) || { id, nom: nom?.split(' ')[0], prenom: nom?.split(' ').slice(1).join(' ') }
  selectChatPatient(p)
}

async function loadChatInbox() {
  if (isPatientView.value) return
  try {
    chatInbox.value = await chatService.inbox()
    const unread = {}
    for (const item of chatInbox.value) {
      if (item.non_lus_equipe) unread[item.patient_id] = item.non_lus_equipe
    }
    chatUnread.value = unread
  } catch (e) {
    console.warn('[Patients] chat inbox:', e.message)
  }
}



async function load() {

  patientError.value = ''

  if (isPatientView.value) {

    const patientId = await resolvePatientId()

    if (!patientId) {

      patientError.value = 'Dossier patient introuvable. Connectez-vous avec votre email patient ou utilisez Mon espace.'

      patients.value = []

      return

    }

    try {

      const profil = await patientService.get(patientId)

      patients.value = profil ? [profil] : []

    } catch {

      patients.value = []

    }

    await loadQrThumbs(filteredPatients.value)

    return

  }

  loading.value = true
  searchError.value = ''
  try {
    patients.value = await patientService.list()
    console.log('[Patients] chargés:', patients.value.length)
  } catch (e) {
    console.error('[Patients] load:', e)
    searchError.value = e.message || 'Impossible de charger la liste. Vérifiez que le backend tourne : python manage.py runserver 8001'
    patients.value = []
  } finally {
    loading.value = false
  }

  if (patients.value.length) {
    loadQrThumbs(patients.value).catch((e) => console.warn('[Patients] QR thumbs:', e))
  }

  await loadAssurances()

  await loadChatInbox()

}



async function createPatient() {
  saving.value = true
  error.value = ''

  try {
    if (!form.value.nom_complet?.trim()) {
      error.value = 'Le nom et prénom sont obligatoires.'
      return
    }
    if (!form.value.telephone?.trim()) {
      error.value = 'Le numéro GSM est obligatoire.'
      return
    }
    if (!form.value.numero_identite?.trim()) {
      error.value = 'Le N° identité est obligatoire.'
      return
    }
    if (!form.value.adresse?.trim()) {
      error.value = 'L\'adresse est obligatoire.'
      return
    }

    const { nom, prenom } = splitName(form.value.nom_complet)

    let dateNaissance = form.value.date_naissance
    if (!dateNaissance && form.value.age != null && form.value.age !== '') {
      dateNaissance = isoFromAge(form.value.age)
    }
    if (!dateNaissance) {
      error.value = 'Indiquez l\'âge du patient (ou la date de naissance).'
      return
    }

    const payload = {
      nom,
      prenom,
      date_naissance: dateNaissance,
      genre: form.value.genre,
      telephone: form.value.telephone.trim(),
      adresse: form.value.adresse.trim(),
      numero_identite: form.value.numero_identite.trim(),
      situation_familiale: form.value.situation_familiale,
      nombre_enfants: Number(form.value.nombre_enfants) || 0,
      profession: form.value.profession || undefined,
      poids_kg: form.value.poids_kg || undefined,
      taille_m: form.value.taille_m || undefined,
      groupe_sanguin: form.value.groupe_sanguin || undefined,
      allergies: form.value.allergies || undefined,
      antecedents_medicaux: form.value.antecedents_medicaux || undefined,
      contact_urgence_nom: form.value.contact_urgence_nom || undefined,
      contact_urgence_telephone: form.value.contact_urgence_telephone || undefined,
      contact_urgence_lien: form.value.contact_urgence_lien || undefined,
    }

    if (form.value.assurance_id) payload.assurance_id = Number(form.value.assurance_id)
    if (form.value.email?.trim()) payload.email = form.value.email.trim()

    console.log('[Patients] POST /reception/patients', payload)
    const created = await patientService.create(payload)
    console.log('[Patients] créé:', created)

    showModal.value = false
    searchEmail.value = created.email || ''
    filtre.value = { nom: '', identite: '' }
    await load()

    alert(`Patient ${created.nom} ${created.prenom} enregistré avec succès.\nN° dossier : ${created.sgl_id}`)

    if (created?.email) {
      showPortalInfo(created)
    }
    goNextIfAuto()
  } catch (e) {
    console.error('[Patients] create:', e)
    error.value = e.message || 'Erreur lors de l\'enregistrement.'
  } finally {
    saving.value = false
  }
}



onMounted(() => {
  load()
  inboxPollTimer = setInterval(() => {
    if (!isPatientView.value) loadChatInbox()
  }, 20000)
})

onUnmounted(() => {
  if (inboxPollTimer) clearInterval(inboxPollTimer)
})

onActivated(() => {
  if (route.path === '/patients') load()
})

watch(
  () => route.path,
  (path) => {
    if (path === '/patients') load()
  }
)

</script>



<style scoped>

.form-field { display: flex; flex-direction: column; gap: 0.35rem; }

.form-field span { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }

</style>

