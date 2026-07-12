<template>
  <div class="space-y-6">
    <div class="page-heading">
      <div>
        <h2 class="text-xl font-bold text-white">💰 Facturation</h2>
        <p class="text-slate-400 text-sm">Clinic / Facturation — caisse et paiements</p>
      </div>
    </div>

    <!-- Formulaire nouvelle facture -->
    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">Nouvelle facture</h3>
      <form @submit.prevent="validerFacture" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <label class="form-field sm:col-span-2">
            <span>Patient (email portail ou nom) *</span>
            <div class="flex gap-2">
              <input
                v-model="patientEmail"
                type="text"
                required
                placeholder="Mukendi Joseph ou patient@sghl.com"
                class="modal-input flex-1"
                @keydown.enter.prevent="chercherPatient"
              />
              <button type="button" @click="chercherPatient" class="btn-save text-sm whitespace-nowrap" :disabled="searchingPatient">
                {{ searchingPatient ? '…' : 'Chercher' }}
              </button>
            </div>
            <p class="text-slate-500 text-xs mt-1">
              Email portail, alias (Joseph@sghl.com) ou nom complet — la recherche se lance aussi à la validation.
            </p>
            <p v-if="patientSelectionne" class="text-teal-400 text-xs mt-1">
              ✓ {{ patientSelectionne.nom }} {{ patientSelectionne.prenom }} ({{ patientSelectionne.sgl_id }})
              <span v-if="patientSelectionne.email" class="text-slate-400"> — {{ patientSelectionne.email }}</span>
            </p>
            <p v-if="patientSearchError" class="text-red-400 text-xs mt-1 whitespace-pre-line">{{ patientSearchError }}</p>
          </label>
          <label class="form-field">
            <span>Société</span>
            <input v-model="form.societe" placeholder="Nom société" class="modal-input" />
          </label>
          <label class="form-field">
            <span>Référence</span>
            <input :value="refAuto" class="modal-input bg-white/5" readonly placeholder="Auto-générée" />
          </label>
          <label class="form-field">
            <span>Date *</span>
            <input v-model="form.date" type="date" class="modal-input" required />
          </label>
        </div>

        <div v-if="patientPrivilegie" class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-sm">
          ⭐ Client privilégié — Carte {{ patientPrivilegie.type_carte_label }} ({{ patientPrivilegie.numero_carte }})
          — Réduction <strong class="text-amber-300">{{ patientPrivilegie.taux_reduction }}%</strong>
        </div>

        <!-- Lignes services -->
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-slate-500 text-xs uppercase">
                <th class="p-2 text-left w-12">N°</th>
                <th class="p-2 text-left">Service</th>
                <th class="p-2 text-left w-36">Frais (FC)</th>
                <th class="p-2 w-10"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(l, i) in form.lignes" :key="i" class="border-t border-white/5">
                <td class="p-2 text-slate-400">{{ i + 1 }}</td>
                <td class="p-2">
                  <input v-model="l.service" placeholder="Description du service" class="modal-input w-full" />
                </td>
                <td class="p-2">
                  <input v-model.number="l.montant" type="number" min="0" step="100" class="modal-input w-full" />
                </td>
                <td class="p-2">
                  <button v-if="form.lignes.length > 1" type="button" @click="form.lignes.splice(i, 1)" class="text-red-400 text-xs">✕</button>
                </td>
              </tr>
            </tbody>
          </table>
          <button type="button" @click="form.lignes.push({ service: '', montant: 0 })" class="mt-2 text-xs text-teal-400 hover:text-teal-300">+ Ajouter une ligne</button>
        </div>

        <!-- Totaux -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-lg ml-auto">
          <label class="form-field">
            <span>TOTAL</span>
            <input :value="formatMoney(totalLignes)" class="modal-input bg-white/5 font-bold text-white" readonly />
          </label>
          <label class="form-field">
            <span>PAYÉ</span>
            <input v-model.number="form.montant_paye" type="number" min="0" step="100" class="modal-input" />
          </label>
          <label class="form-field">
            <span>LE RESTE</span>
            <input :value="formatMoney(reste)" class="modal-input bg-white/5" readonly />
          </label>
        </div>

        <!-- Mode de paiement -->
        <div>
          <p class="text-xs text-slate-500 uppercase tracking-wider mb-3">Mode de paiement *</p>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <button v-for="m in modesPaiement" :key="m.value" type="button"
              @click="form.mode_paiement = m.value"
              class="p-4 rounded-xl border text-center transition"
              :class="form.mode_paiement === m.value
                ? 'bg-teal-500/20 border-teal-500/40 text-teal-300'
                : 'bg-white/5 border-white/10 text-slate-400 hover:border-white/20'">
              <span class="text-2xl block mb-1">{{ m.icon }}</span>
              <span class="text-xs font-medium">{{ m.label }}</span>
            </button>
          </div>
          <input v-if="form.mode_paiement !== 'ESPECES'" v-model="form.reference_transaction"
            placeholder="Référence transaction (optionnel)" class="modal-input mt-3 max-w-md" />
        </div>

        <div class="flex gap-3">
          <button type="submit" class="btn-save px-8" :disabled="saving">
            {{ saving ? 'Validation...' : 'Valider' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Liste factures -->
    <div class="page-card p-6">
      <h3 class="text-white font-semibold mb-4">Les factures</h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <input v-model="filtre.nom" placeholder="Nom et prénom" class="modal-input text-sm" />
        <input v-model="filtre.reference" placeholder="Référence" class="modal-input text-sm" />
        <button @click="load" class="btn-cancel text-sm">Filtrer</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-slate-500 text-xs uppercase">
              <th class="p-3 text-left">Référence</th>
              <th class="p-3 text-left">Patient</th>
              <th class="p-3 text-left">Total</th>
              <th class="p-3 text-left">Payé</th>
              <th class="p-3 text-left">Reste</th>
              <th class="p-3 text-left">Statut</th>
              <th class="p-3 text-left">Paiements</th>
              <th class="p-3 text-left">Reçu</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in facturesFiltrees" :key="f.id" class="border-t border-white/5 hover:bg-white/3">
              <td class="p-3 text-teal-400 font-mono text-xs">{{ f.reference }}</td>
              <td class="p-3 text-white">{{ f.patient_nom }}</td>
              <td class="p-3 text-slate-300">{{ formatMoney(f.montant_total_brut) }}</td>
              <td class="p-3 text-green-400">{{ formatMoney(f.montant_paye) }}</td>
              <td class="p-3 text-amber-300">{{ formatMoney(f.montant_reste) }}</td>
              <td class="p-3">
                <span class="text-xs px-2 py-0.5 rounded-full"
                  :class="f.statut === 'PAYE' ? 'bg-green-500/20 text-green-300' : f.statut === 'PARTIEL' ? 'bg-blue-500/20 text-blue-300' : 'bg-amber-500/20 text-amber-300'">
                  {{ f.statut }}
                </span>
              </td>
              <td class="p-3 text-xs text-slate-400">
                <span v-for="p in f.paiements" :key="p.id" class="block">{{ p.mode_label }}: {{ formatMoney(p.montant) }}</span>
              </td>
              <td class="p-3">
                <div class="flex gap-2">
                  <button @click="exportRecuPdf(f)" class="text-xs text-red-400 hover:text-red-300 font-medium">📄 PDF</button>
                  <button @click="exportRecuExcel(f)" class="text-xs text-emerald-400 hover:text-emerald-300 font-medium">📊 Excel</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { billingService, patientService, privilegeService, bankService } from '../services/api.js'
import { exportFactureExcel, exportFacturePdf } from '../utils/exportExcel.js'
import { usePageFlow } from '../composables/usePageFlow.js'

const { goNextIfAuto } = usePageFlow()

const clientsPrivilegies = ref([])
const factures = ref([])
const comptesBanque = ref([])
const saving = ref(false)
const refAuto = ref('Auto FAC-YYYY-XXXX')
const filtre = ref({ nom: '', reference: '' })
const patientEmail = ref('')
const patientSelectionne = ref(null)
const patientSearchError = ref('')
const searchingPatient = ref(false)

const modesPaiement = [
  { value: 'CARTE', label: 'Par carte', icon: '💳' },
  { value: 'MOMO', label: 'Par MoMo', icon: '📱' },
  { value: 'AIRTEL', label: 'Par Airtel', icon: '📲' },
  { value: 'MTN', label: 'Par MTN', icon: '🟡' },
]

const form = ref({
  patient_id: '',
  societe: '',
  date: new Date().toISOString().slice(0, 10),
  lignes: [{ service: '', montant: 0 }],
  montant_paye: 0,
  mode_paiement: 'CARTE',
  reference_transaction: '',
})

const totalLignes = computed(() =>
  form.value.lignes.reduce((s, l) => s + (Number(l.montant) || 0), 0)
)

const reste = computed(() => Math.max(0, totalLignes.value - (Number(form.value.montant_paye) || 0)))

const patientPrivilegie = computed(() =>
  patientSelectionne.value
    ? clientsPrivilegies.value.find(c => c.patient_id === patientSelectionne.value.id && c.est_actif)
    : null
)

const facturesFiltrees = computed(() => {
  let list = factures.value
  if (filtre.value.nom) {
    const q = filtre.value.nom.toLowerCase()
    list = list.filter(f => f.patient_nom?.toLowerCase().includes(q))
  }
  if (filtre.value.reference) {
    list = list.filter(f => f.reference?.includes(filtre.value.reference))
  }
  return list
})

function formatMoney(n) {
  return new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 }).format(n || 0) + ' FC'
}

function onPatientSelect() {}

async function chercherPatient() {
  if (!patientEmail.value.trim()) {
    patientSearchError.value = 'Entrez un email portail ou le nom du patient.'
    return
  }
  searchingPatient.value = true
  patientSearchError.value = ''
  patientSelectionne.value = null
  form.value.patient_id = ''
  try {
    patientSelectionne.value = await patientService.parEmail(patientEmail.value.trim())
    form.value.patient_id = patientSelectionne.value.id
    if (patientSelectionne.value.email) {
      patientEmail.value = patientSelectionne.value.email
    }
    if (!form.value.montant_paye && totalLignes.value > 0) {
      form.value.montant_paye = totalLignes.value
    }
  } catch (e) {
    patientSearchError.value = e.message || 'Patient introuvable.'
  } finally {
    searchingPatient.value = false
  }
}

watch(totalLignes, (total) => {
  if (patientSelectionne.value && (!form.value.montant_paye || form.value.montant_paye === 0)) {
    form.value.montant_paye = total
  }
})

function exportRecuExcel(f) { exportFactureExcel(f) }
function exportRecuPdf(f) { exportFacturePdf(f) }

async function load() {
  const [privs, facts, comptes] = await Promise.all([
    privilegeService.list(),
    billingService.factures(),
    bankService.comptes(),
  ])
  clientsPrivilegies.value = privs
  factures.value = facts
  comptesBanque.value = comptes
}

async function validerFacture() {
  if (!patientSelectionne.value?.id && patientEmail.value.trim()) {
    await chercherPatient()
  }
  if (!patientSelectionne.value?.id) {
    patientSearchError.value = patientSearchError.value || 'Patient introuvable — vérifiez le nom ou l\'email puis cliquez Chercher.'
    return
  }
  const lignes = form.value.lignes.filter(l => l.service && l.montant > 0)
  if (!lignes.length) {
    alert('Ajoutez au moins une ligne de service avec un montant.')
    return
  }
  if (!form.value.mode_paiement) {
    alert('Choisissez un mode de paiement.')
    return
  }
  saving.value = true
  try {
    const facture = await billingService.creerFacture({
      patient_id: patientSelectionne.value.id,
      societe: form.value.societe,
      lignes,
    })
    const montantPaye = Number(form.value.montant_paye) || totalLignes.value
    if (montantPaye > 0) {
      const payload = {
        montant: montantPaye,
        mode_paiement: form.value.mode_paiement,
        reference_transaction: form.value.reference_transaction,
      }
      if (comptesBanque.value.length) payload.compte_banque_id = comptesBanque.value[0].id
      await billingService.payer(facture.id, payload)
    }
    form.value = {
      patient_id: '', societe: '', date: new Date().toISOString().slice(0, 10),
      lignes: [{ service: '', montant: 0 }], montant_paye: 0,
      mode_paiement: 'CARTE', reference_transaction: '',
    }
    patientEmail.value = ''
    patientSelectionne.value = null
    await load()
    goNextIfAuto()
  } catch (e) {
    alert(e.message)
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.form-field { display: flex; flex-direction: column; gap: 0.35rem; }
.form-field span { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }
</style>
