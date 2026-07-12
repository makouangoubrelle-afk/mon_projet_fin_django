<template>
  <div class="patient-portal space-y-6">
    <div class="max-w-4xl mx-auto space-y-6">

        <div v-if="loadError" class="page-card p-8 text-center">
          <p class="text-red-400">{{ loadError }}</p>
          <router-link to="/login" class="inline-block mt-4 text-teal-400 text-sm hover:underline">← Retour à la connexion</router-link>
        </div>

        <div v-if="loading" class="text-center text-slate-500 py-12">Chargement de votre dossier…</div>

        <template v-else-if="dossier">

          <!-- Carte profil -->
          <section class="page-card overflow-hidden">
            <div class="p-6 md:p-8 bg-gradient-to-br from-teal-500/15 via-transparent to-cyan-500/10">
              <div class="flex flex-wrap items-start justify-between gap-6">
                <div>
                  <span class="text-xs px-3 py-1 rounded-full font-medium" :class="statutClass(dossier.profil.statut)">
                    {{ dossier.profil.statut_label || '—' }}
                  </span>
                  <h2 class="text-2xl md:text-3xl font-bold text-white mt-3">
                    {{ dossier.profil.nom }} {{ dossier.profil.prenom }}
                  </h2>
                  <p class="text-slate-400 text-sm mt-1">
                    {{ dossier.profil.genre_label }} · {{ dossier.profil.age }} ans · {{ dossier.profil.telephone }}
                  </p>
                </div>
                <div class="flex items-start gap-4">
                  <div v-if="qrDataUrl" class="text-center p-2 rounded-xl bg-white/5">
                    <img :src="qrDataUrl" alt="QR" class="w-16 h-16 rounded-lg bg-white p-1" />
                    <p class="text-[9px] text-slate-500 mt-1">QR</p>
                  </div>
                  <div v-if="dossier.profil.groupe_sanguin" class="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/25 text-center">
                    <p class="text-[10px] text-red-300 uppercase">Groupe</p>
                    <p class="text-xl font-bold text-red-400">{{ dossier.profil.groupe_sanguin }}</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Navigation principale -->
          <nav class="flex flex-wrap gap-2">
            <button
              v-for="tab in primaryTabs"
              :key="tab.id"
              type="button"
              @click="activeTab = tab.id"
              class="px-4 py-2.5 rounded-xl text-sm font-medium border transition"
              :class="activeTab === tab.id ? 'nav-pill-active' : 'nav-pill'"
            >
              {{ tab.icon }} {{ tab.label }}
              <span v-if="tab.count !== undefined" class="ml-1 opacity-70">({{ tab.count }})</span>
            </button>
            <button
              v-for="tab in secondaryTabs"
              :key="tab.id"
              type="button"
              @click="activeTab = tab.id"
              class="px-3 py-2 rounded-xl text-xs border transition"
              :class="activeTab === tab.id ? 'nav-pill-active' : 'nav-pill opacity-80'"
            >
              {{ tab.icon }} {{ tab.label }}
            </button>
          </nav>

          <!-- Contenu onglets -->
          <section class="page-card p-6 md:p-8">

            <!-- Statut -->
            <div v-show="activeTab === 'statut'">
              <h3 class="text-lg font-semibold text-white mb-5">📊 Mon statut</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div class="p-4 rounded-xl bg-white/5">
                  <p class="text-xs text-slate-500 uppercase mb-1">Statut hospitalier</p>
                  <span class="text-sm px-3 py-1 rounded-full font-medium" :class="statutClass(dossier.profil.statut)">
                    {{ dossier.profil.statut_label || '—' }}
                  </span>
                </div>
                <div class="p-4 rounded-xl bg-white/5">
                  <p class="text-xs text-slate-500 uppercase mb-1">Produits dispensés</p>
                  <p class="text-amber-300 font-medium">{{ dossier.profil.nb_produits || 0 }} produit(s)</p>
                </div>
                <div v-if="dossier.localisation" class="p-4 rounded-xl bg-white/5 sm:col-span-2">
                  <p class="text-xs text-slate-500 uppercase mb-1">Localisation</p>
                  <p class="text-white">{{ dossier.localisation.batiment }} — Étage {{ dossier.localisation.etage }}</p>
                  <p class="text-slate-400 text-sm">{{ dossier.localisation.salle }}</p>
                  <p v-if="dossier.localisation.service_nom" class="text-teal-400 text-sm mt-1">{{ dossier.localisation.service_nom }}</p>
                </div>
              </div>
              <div v-if="dossier.localisation" class="rounded-xl overflow-hidden border border-white/10 mb-4">
                <HospitalMap :markers="[mapMarker]" :center="mapCenter" height="280px" />
              </div>
              <div v-if="dossier.hospitalisations.some(h => !h.est_cloture)" class="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
                <p class="text-purple-300 font-medium text-sm">🏥 Hospitalisation en cours</p>
                <p v-for="h in dossier.hospitalisations.filter(x => !x.est_cloture)" :key="h.id" class="text-slate-300 text-sm mt-1">
                  {{ h.motif_hospitalisation }} — {{ h.chambre || 'Chambre en attente' }}
                </p>
              </div>
              <div class="mt-6 pt-6 border-t border-white/10">
                <h4 class="text-sm font-medium text-slate-400 mb-3">Informations personnelles</h4>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                  <div><span class="text-slate-500 text-xs block">Naissance</span><span class="text-white">{{ formatDate(dossier.profil.date_naissance) }}</span></div>
                  <div><span class="text-slate-500 text-xs block">Adresse</span><span class="text-white">{{ dossier.profil.adresse || '—' }}</span></div>
                  <div><span class="text-slate-500 text-xs block">Assurance</span><span class="text-white">{{ dossier.profil.assurance_nom || '—' }}</span></div>
                </div>
              </div>
            </div>

            <!-- Ordonnances -->
            <div v-show="activeTab === 'ordonnances'">
              <h3 class="text-lg font-semibold text-white mb-5">💊 Mes ordonnances</h3>
              <div v-if="!dossier.ordonnances.length" class="text-slate-500 text-sm py-8 text-center">Aucune ordonnance enregistrée.</div>
              <div v-else class="space-y-4">
                <article v-for="o in dossier.ordonnances" :key="o.id" class="p-5 rounded-xl bg-white/5 border border-white/5">
                  <div class="flex flex-wrap justify-between gap-2 mb-3">
                    <div>
                      <p class="text-white font-medium">{{ formatDateTime(o.date_ordonnance) }}</p>
                      <p v-if="o.medecin_nom" class="text-xs text-teal-400 mt-0.5">Dr. {{ o.medecin_nom }}</p>
                    </div>
                    <div class="flex gap-2">
                      <button type="button" @click="exportPdfOrdonnance(o)" class="text-xs px-3 py-1 rounded-lg bg-red-500/15 text-red-300 border border-red-500/25">PDF</button>
                      <button type="button" @click="exportExcelOrdonnance(o)" class="text-xs px-3 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/25">Excel</button>
                    </div>
                  </div>
                  <pre class="text-sm text-slate-300 whitespace-pre-line font-sans leading-relaxed">{{ o.medicaments }}</pre>
                  <p v-if="o.instructions" class="text-xs text-teal-400 mt-3 pt-3 border-t border-white/5">{{ o.instructions }}</p>
                </article>
              </div>
            </div>

            <!-- Laboratoire -->
            <div v-show="activeTab === 'analyses'">
              <h3 class="text-lg font-semibold text-white mb-5">🔬 Mon laboratoire</h3>
              <div v-if="!dossier.analyses.length" class="text-slate-500 text-sm py-8 text-center">Aucun résultat d'analyse.</div>
              <div v-else class="space-y-4">
                <article v-for="a in dossier.analyses" :key="a.id" class="p-5 rounded-xl bg-white/5 border border-white/5">
                  <div class="flex justify-between items-start gap-3">
                    <p class="text-white font-medium">{{ a.examen_nom }}</p>
                    <span class="text-xs px-2 py-0.5 rounded-full shrink-0" :class="a.statut === 'VALIDE' ? 'bg-green-500/20 text-green-300' : 'bg-amber-500/20 text-amber-300'">
                      {{ a.statut }}
                    </span>
                  </div>
                  <pre v-if="a.resultat" class="text-sm text-slate-300 mt-3 whitespace-pre-line font-sans">{{ a.resultat }}</pre>
                  <p class="text-xs text-slate-500 mt-2">{{ formatDateTime(a.date_commande) }}</p>
                </article>
              </div>
            </div>

            <!-- Infos médicales -->
            <div v-show="activeTab === 'medical'">
              <h3 class="text-lg font-semibold text-white mb-5">🩺 Informations médicales</h3>
              <div v-if="dossier.profil.informations_medicales" class="p-4 rounded-xl bg-white/5 whitespace-pre-line text-slate-300 text-sm leading-relaxed">
                {{ dossier.profil.informations_medicales }}
              </div>
              <p v-else class="text-slate-500 text-sm">Aucune information médicale.</p>
            </div>

            <!-- RDV -->
            <div v-show="activeTab === 'rdv'">
              <h3 class="text-lg font-semibold text-white mb-5">📅 Rendez-vous</h3>
              <div v-if="!dossier.rendez_vous.length" class="text-slate-500 text-sm py-8 text-center">Aucun rendez-vous.</div>
              <div v-else class="space-y-3">
                <div v-for="r in dossier.rendez_vous" :key="r.id" class="p-4 rounded-xl bg-white/5 flex justify-between gap-4">
                  <div>
                    <p class="text-white font-medium">{{ r.motif }}</p>
                    <p class="text-sm text-slate-400 mt-1">{{ formatDateTime(r.date_rdv) }}</p>
                    <p v-if="r.medecin_nom" class="text-xs text-slate-500 mt-1">Dr. {{ r.medecin_nom }}</p>
                  </div>
                  <span class="text-xs px-2 py-1 rounded-full h-fit shrink-0" :class="r.statut === 'CONFIRME' ? 'bg-green-500/20 text-green-300' : 'bg-amber-500/20 text-amber-300'">
                    {{ r.statut_label }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Consultations -->
            <div v-show="activeTab === 'consultations'">
              <h3 class="text-lg font-semibold text-white mb-5">🩺 Consultations</h3>
              <div v-if="!dossier.consultations.length" class="text-slate-500 text-sm py-8 text-center">Aucune consultation.</div>
              <div v-else class="space-y-3">
                <div v-for="c in dossier.consultations" :key="c.id" class="p-4 rounded-xl bg-white/5">
                  <p class="text-white font-medium">{{ c.motif_consultation }}</p>
                  <p v-if="c.diagnostic" class="text-teal-300 text-sm mt-1">{{ c.diagnostic }}</p>
                  <p class="text-xs text-slate-500 mt-2">{{ formatDateTime(c.date_consultation) }}</p>
                </div>
              </div>
            </div>

            <!-- Hospitalisations -->
            <div v-show="activeTab === 'hospitalisations'">
              <h3 class="text-lg font-semibold text-white mb-5">🏥 Hospitalisations</h3>
              <div v-if="!dossier.hospitalisations.length" class="text-slate-500 text-sm py-8 text-center">Aucune hospitalisation.</div>
              <div v-else class="space-y-3">
                <div v-for="h in dossier.hospitalisations" :key="h.id" class="p-4 rounded-xl bg-white/5">
                  <p class="text-white font-medium">{{ h.motif_hospitalisation }}</p>
                  <p v-if="h.chambre" class="text-sm text-teal-400 mt-1">{{ h.chambre }}</p>
                  <p class="text-xs text-slate-500 mt-2">{{ formatDateTime(h.date_entree) }}</p>
                </div>
              </div>
            </div>

            <!-- Factures -->
            <div v-show="activeTab === 'factures'">
              <h3 class="text-lg font-semibold text-white mb-5">💳 Factures</h3>
              <div v-if="!dossier.factures.length" class="text-slate-500 text-sm py-8 text-center">Aucune facture.</div>
              <div v-else class="space-y-3">
                <div v-for="f in dossier.factures" :key="f.id" class="p-4 rounded-xl bg-white/5 flex justify-between items-center">
                  <div>
                    <p class="text-white font-medium">Facture #{{ f.id }}</p>
                    <p class="text-xs text-slate-500">{{ formatDateTime(f.date_facture) }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-lg font-bold text-white">{{ formatMoney(f.montant_patient_net) }}</p>
                    <span class="text-xs px-2 py-0.5 rounded-full" :class="f.statut === 'PAYE' ? 'bg-green-500/20 text-green-300' : 'bg-amber-500/20 text-amber-300'">
                      {{ f.statut === 'PAYE' ? 'Payé' : 'En attente' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

          </section>
        </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QRCode from 'qrcode'
import { getPatientSession, getUser, patientService } from '../services/api.js'
import { exportOrdonnanceExcel, exportOrdonnancePdf } from '../utils/exportExcel.js'
import { HOSPITAL_CENTER } from '../constants/geo.js'
import HospitalMap from '../components/HospitalMap.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const loadError = ref('')
const dossier = ref(null)
const activeTab = ref(route.query.section?.toString() || 'statut')
const qrDataUrl = ref('')

const primaryTabs = computed(() => [
  { id: 'statut', label: 'Statut', icon: '📊' },
  { id: 'ordonnances', label: 'Ordonnances', icon: '💊', count: dossier.value?.ordonnances?.length ?? 0 },
  { id: 'analyses', label: 'Laboratoire', icon: '🔬', count: dossier.value?.analyses?.length ?? 0 },
])

const secondaryTabs = [
  { id: 'medical', label: 'Médical', icon: '🩺' },
  { id: 'rdv', label: 'RDV', icon: '📅' },
  { id: 'consultations', label: 'Consult.', icon: '📋' },
  { id: 'hospitalisations', label: 'Hosp.', icon: '🏥' },
  { id: 'factures', label: 'Factures', icon: '💳' },
]

const mapCenter = computed(() => {
  const loc = dossier.value?.localisation
  if (loc?.latitude && loc?.longitude) return [loc.latitude, loc.longitude]
  return HOSPITAL_CENTER
})

const mapMarker = computed(() => {
  const loc = dossier.value?.localisation
  const profil = dossier.value?.profil
  if (!loc) return {}
  return {
    id: profil?.id,
    patient_nom: `${profil?.nom} ${profil?.prenom}`,
    patient_sgl_id: profil?.sgl_id,
    latitude: loc.latitude,
    longitude: loc.longitude,
    batiment: loc.batiment,
    etage: loc.etage,
    salle: loc.salle,
    statut_label: loc.statut_label,
  }
})

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatDateTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatMoney(n) {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'CDF', maximumFractionDigits: 0 }).format(n || 0)
}

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

function ordonnanceExportPayload(o) {
  const p = dossier.value?.profil
  return { ...o, patient_nom: p ? `${p.nom} ${p.prenom}` : '', patient_qr_code: p?.qr_code || '' }
}

function exportPdfOrdonnance(o) { exportOrdonnancePdf(ordonnanceExportPayload(o)) }
function exportExcelOrdonnance(o) { exportOrdonnanceExcel(ordonnanceExportPayload(o)) }

onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    const user = getUser()
    const ps = getPatientSession()
    if (user?.role === 'PATIENT' && user.email) {
      dossier.value = await patientService.monDossier()
    } else if (ps?.patient_id) {
      dossier.value = await patientService.monDossierSession()
    } else {
      router.replace('/login')
      return
    }
    if (dossier.value?.profil?.qr_code) {
      qrDataUrl.value = await QRCode.toDataURL(`SGHL-PATIENT:${dossier.value.profil.qr_code}`, { width: 160 })
    }
    if (route.query.section) activeTab.value = route.query.section.toString()
  } catch (e) {
    loadError.value = e.message || 'Impossible de charger votre dossier.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
</style>
