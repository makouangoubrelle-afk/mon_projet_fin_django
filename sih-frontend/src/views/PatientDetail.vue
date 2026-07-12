<template>
  <div v-if="loading" class="text-slate-500 p-4">Chargement du dossier...</div>
  <div v-else-if="loadError" class="page-card p-6 border border-red-500/30 bg-red-500/10">
    <p class="text-red-300 font-medium mb-2">Impossible d'ouvrir le dossier</p>
    <p class="text-red-200/80 text-sm">{{ loadError }}</p>
    <button @click="$router.push('/patients')" class="mt-4 text-sm text-teal-400 hover:text-teal-300">← Retour à la liste</button>
  </div>
  <div v-else-if="dossier" class="space-y-6">
    <button @click="$router.back()" class="text-sm text-teal-400 hover:text-teal-300">← Retour</button>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Carte patient -->
      <div class="page-card p-6 lg:col-span-1">
        <div class="flex flex-col items-center text-center">
          <img :src="avatarUrl" alt="" class="w-24 h-24 rounded-full object-cover border-4 border-teal-500/30 mb-4" />
          <h2 class="text-xl font-bold text-white">{{ profil.nom }} {{ profil.prenom }}</h2>
          <p class="text-slate-400 text-sm mt-1">{{ profil.telephone }}</p>
          <p class="text-slate-500 text-xs mt-1">{{ profil.adresse }}</p>
          <p class="text-slate-400 text-sm mt-2">{{ profil.profession || '—' }}</p>
          <p v-if="profil.poids_kg" class="text-teal-400 text-sm mt-1">{{ profil.poids_kg }} Kg, {{ profil.taille_m }} m</p>
          <span class="mt-3 px-3 py-1 rounded-full bg-green-500/20 text-green-300 text-xs">NORMAL</span>
        </div>
        <div class="mt-6 space-y-2 text-sm border-t border-white/10 pt-4">
          <p><span class="text-slate-500">Situation :</span> <span class="text-white">{{ profil.situation_familiale }}</span></p>
          <p><span class="text-slate-500">Enfants :</span> <span class="text-white">{{ profil.nombre_enfants ?? 0 }}</span></p>
          <p><span class="text-slate-500">N° dossier :</span> <span class="text-teal-300 font-mono">{{ profil.sgl_id }}</span></p>
          <p><span class="text-slate-500">Groupe sanguin :</span> <span class="text-white">{{ profil.groupe_sanguin || '—' }}</span></p>
          <p><span class="text-slate-500">Assurance :</span> <span class="text-white">{{ profil.assurance_nom || '—' }}</span></p>
          <p><span class="text-slate-500">1ère consultation :</span> <span class="text-white">{{ formatDate(profil.date_enregistrement) }}</span></p>
          <div v-if="profil.contact_urgence_nom" class="mt-3 pt-3 border-t border-white/10">
            <p class="text-xs text-slate-500 uppercase mb-1">Contact d'urgence</p>
            <p class="text-white text-sm">{{ profil.contact_urgence_nom }} ({{ profil.contact_urgence_lien || '—' }})</p>
            <p class="text-teal-400 text-sm">{{ profil.contact_urgence_telephone }}</p>
          </div>
          <p v-if="imc"><span class="text-slate-500">IMC :</span> <span class="text-white">{{ imc }}</span></p>
        </div>
        <div class="mt-6 p-4 rounded-xl bg-white/5 text-center">
          <p class="text-xs text-slate-500 mb-2">Code QR patient</p>
          <img v-if="qrDataUrl" :src="qrDataUrl" alt="QR" class="mx-auto w-32 h-32 rounded-lg bg-white p-2" />
          <p class="text-[10px] text-slate-600 font-mono mt-2 break-all">{{ profil.qr_code }}</p>
        </div>
      </div>

      <!-- Onglets dossier -->
      <div class="page-card p-0 lg:col-span-2 overflow-hidden flex flex-col md:flex-row min-h-[480px]">
        <nav class="md:w-52 bg-white/5 border-b md:border-b-0 md:border-r border-white/10 p-2 shrink-0">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
            class="w-full text-left px-4 py-3 rounded-lg text-sm mb-1 transition"
            :class="activeTab === tab.id ? 'bg-teal-500/20 text-teal-300 font-medium' : 'text-slate-400 hover:bg-white/5'">
            {{ tab.label }}
          </button>
        </nav>
        <div class="flex-1 p-6 overflow-y-auto max-h-[520px]">
          <div v-if="activeTab === 'antecedents'" class="space-y-4 text-sm">
            <div><p class="text-slate-500 text-xs uppercase mb-1">Antécédents médicaux</p>
              <p class="text-slate-300 whitespace-pre-line">{{ profil.antecedents_medicaux || profil.informations_medicales || 'Aucun antécédent.' }}</p></div>
            <div><p class="text-slate-500 text-xs uppercase mb-1">Allergies</p>
              <p class="text-red-300 whitespace-pre-line">{{ profil.allergies || 'Aucune allergie connue.' }}</p></div>
          </div>
          <div v-else-if="activeTab === 'rdv'" class="space-y-3">
            <div v-for="rv in dossier.rendez_vous || []" :key="rv.id" class="p-3 rounded-xl bg-white/5 text-sm">
              <p class="text-white">{{ rv.motif }}</p>
              <p class="text-xs text-slate-500">{{ formatDate(rv.date_rdv) }} — {{ rv.statut_label || rv.statut }}</p>
            </div>
            <p v-if="!(dossier.rendez_vous || []).length" class="text-slate-500">Aucun rendez-vous.</p>
          </div>
          <div v-else-if="activeTab === 'hospi'" class="space-y-3">
            <div v-for="a in dossier.hospitalisations || []" :key="a.id" class="p-3 rounded-xl bg-white/5 text-sm">
              <p class="text-white">{{ a.motif_hospitalisation || 'Hospitalisation' }}</p>
              <p class="text-xs text-slate-500">{{ formatDate(a.date_entree) }} — {{ a.est_cloture ? 'Sortie' : 'En cours' }}</p>
              <p v-if="a.chambre" class="text-xs text-teal-400 mt-1">{{ a.chambre }}</p>
            </div>
            <p v-if="!(dossier.hospitalisations || []).length" class="text-slate-500">Aucune hospitalisation.</p>
          </div>
          <div v-else-if="activeTab === 'factures'" class="space-y-3">
            <div v-for="f in dossier.factures || []" :key="f.id" class="p-3 rounded-xl bg-white/5 text-sm flex justify-between">
              <span class="text-white">{{ f.reference }}</span>
              <span class="text-teal-300">{{ f.montant_patient_net }} CDF — {{ f.statut }}</span>
            </div>
            <p v-if="!(dossier.factures || []).length" class="text-slate-500">Aucune facture.</p>
          </div>
          <div v-else-if="activeTab === 'motifs'" class="space-y-3">
            <div v-for="c in dossier.consultations" :key="c.id" class="p-3 rounded-xl bg-white/5 text-sm">
              <p class="text-white">{{ c.motif_consultation }}</p>
              <p class="text-xs text-slate-500 mt-1">{{ formatDate(c.date_consultation) }}</p>
            </div>
            <p v-if="!dossier.consultations.length" class="text-slate-500 text-sm">Aucun motif.</p>
          </div>
          <div v-else-if="activeTab === 'cliniques'" class="space-y-3">
            <div v-for="c in dossier.consultations" :key="'cl'+c.id" class="p-3 rounded-xl bg-white/5 text-sm">
              <p v-if="c.diagnostic" class="text-teal-300">{{ c.diagnostic }}</p>
              <p class="text-slate-400 mt-1">TA: {{ c.tension_arterielle || '—' }} · Temp: {{ c.temperature || '—' }}°C · Poids: {{ c.poids || '—' }} kg</p>
            </div>
          </div>
          <div v-else-if="activeTab === 'biologiques'" class="space-y-3">
            <div v-for="a in dossier.analyses" :key="a.id" class="p-3 rounded-xl bg-white/5 text-sm">
              <p class="text-white font-medium">{{ a.examen_nom }}</p>
              <pre class="text-slate-300 mt-1 whitespace-pre-line font-sans">{{ a.resultat || 'En cours...' }}</pre>
            </div>
          </div>
          <div v-else-if="activeTab === 'radiologiques'" class="text-slate-500 text-sm">Examens radiologiques — à renseigner via Urgences ou consultation.</div>
          <div v-else-if="activeTab === 'diagnostic'" class="space-y-3">
            <div v-for="c in dossier.consultations.filter(x => x.diagnostic)" :key="'d'+c.id" class="p-3 rounded-xl bg-white/5">
              <p class="text-white">{{ c.diagnostic }}</p>
              <p class="text-xs text-slate-500">{{ formatDate(c.date_consultation) }}</p>
            </div>
          </div>
          <div v-else-if="activeTab === 'traitements'" class="space-y-3">
            <div v-for="o in dossier.ordonnances" :key="o.id" class="p-3 rounded-xl bg-white/5 text-sm whitespace-pre-line">{{ o.medicaments }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="page-card p-6 text-slate-500 text-sm">
    Dossier introuvable.
    <button @click="$router.push('/patients')" class="block mt-3 text-teal-400 hover:text-teal-300">← Retour à la liste</button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import QRCode from 'qrcode'
import { patientService } from '../services/api.js'

const route = useRoute()
const dossier = ref(null)
const loading = ref(true)
const loadError = ref('')
const activeTab = ref('antecedents')
const qrDataUrl = ref('')

const tabs = [
  { id: 'antecedents', label: 'Antécédents & allergies' },
  { id: 'rdv', label: 'Rendez-vous' },
  { id: 'hospi', label: 'Hospitalisations' },
  { id: 'motifs', label: 'Motifs de consultation' },
  { id: 'cliniques', label: 'Examens cliniques' },
  { id: 'biologiques', label: 'Examens Biologiques' },
  { id: 'radiologiques', label: 'Examens Radiologiques' },
  { id: 'diagnostic', label: 'Diagnostic' },
  { id: 'traitements', label: 'Les traitements' },
  { id: 'factures', label: 'Factures & paiements' },
]

const profil = computed(() => dossier.value?.profil || {})
const imc = computed(() => {
  const p = profil.value
  if (p.poids_kg && p.taille_m) return (p.poids_kg / (p.taille_m * p.taille_m)).toFixed(2)
  return null
})
const avatarUrl = computed(() =>
  `https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=200&h=200&fit=crop&crop=face`
)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function loadDossier(id) {
  loading.value = true
  loadError.value = ''
  dossier.value = null
  qrDataUrl.value = ''
  activeTab.value = 'antecedents'
  try {
    dossier.value = await patientService.dossier(id)
    if (profil.value.qr_code) {
      qrDataUrl.value = await QRCode.toDataURL(`SGHL-PATIENT:${profil.value.qr_code}`, { width: 200, margin: 1 })
    }
  } catch (e) {
    console.error('[PatientDetail] load:', e)
    loadError.value = e.message || 'Dossier introuvable.'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadDossier(Number(route.params.id)))

watch(
  () => route.params.id,
  (id) => {
    if (id) loadDossier(Number(id))
  }
)
</script>
