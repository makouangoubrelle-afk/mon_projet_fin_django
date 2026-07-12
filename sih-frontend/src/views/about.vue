<template>
  <div class="space-y-6">
    <!-- En-tête -->
    <div class="page-card p-8 bg-gradient-to-br from-teal-500/15 via-transparent to-cyan-500/10 border border-teal-500/20">
      <div class="flex flex-wrap items-start gap-6">
        <div class="w-20 h-20 rounded-2xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center text-4xl shrink-0">
          🏥
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl md:text-3xl font-bold text-white">SGHL</h2>
          <p class="text-teal-300 text-sm mt-1">Système de Gestion Hospitalière et de Laboratoire</p>
          <p class="text-slate-400 text-sm mt-3 max-w-2xl leading-relaxed">
            Plateforme intégrée pour la réception, le parcours clinique, la pharmacie, le laboratoire,
            la facturation et l'espace patient — conçue pour les établissements de santé en République du Congo.
          </p>
          <div class="flex flex-wrap gap-2 mt-4">
            <span class="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              ● Système opérationnel
            </span>
            <span class="text-xs px-3 py-1 rounded-full bg-white/5 text-slate-400 border border-white/10">
              Version 1.0.0
            </span>
            <span class="text-xs px-3 py-1 rounded-full bg-white/5 text-slate-400 border border-white/10">
              API Django · Vue 3
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chiffres clés -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="k in chiffres" :key="k.label" class="page-card p-5 text-center">
        <p class="text-2xl mb-1">{{ k.icon }}</p>
        <p class="text-2xl font-bold text-white">{{ k.value }}</p>
        <p class="text-xs text-slate-500 uppercase mt-1">{{ k.label }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Modules -->
      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4">📦 Modules de l'application</h3>
        <ul class="space-y-3">
          <li v-for="m in modules" :key="m.titre" class="flex gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
            <span class="text-xl shrink-0">{{ m.icon }}</span>
            <div>
              <p class="text-white text-sm font-medium">{{ m.titre }}</p>
              <p class="text-slate-500 text-xs mt-0.5">{{ m.desc }}</p>
            </div>
          </li>
        </ul>
      </div>

      <!-- Rôles & accès -->
      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4">👤 Profils utilisateurs</h3>
        <div class="space-y-2">
          <div v-for="r in roles" :key="r.nom" class="flex items-center justify-between p-3 rounded-xl bg-white/5">
            <div class="flex items-center gap-2">
              <span>{{ r.icon }}</span>
              <span class="text-white text-sm">{{ r.nom }}</span>
            </div>
            <span class="text-[10px] text-slate-500 max-w-[55%] text-right">{{ r.acces }}</span>
          </div>
        </div>

        <div class="mt-5 p-4 rounded-xl bg-teal-500/10 border border-teal-500/25">
          <p class="text-teal-200 text-sm font-medium">🧑 Espace patient</p>
          <p class="text-slate-400 text-xs mt-1">
            Connexion par email portail (<code class="text-teal-300">prenom.nom@patient.sghl.com</code>)
            + code OTP. Accès au statut, ordonnances, laboratoire et factures.
          </p>
        </div>
      </div>
    </div>

    <!-- Établissement & contact -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="page-card p-6 lg:col-span-2">
        <h3 class="text-white font-semibold mb-4">🏢 Établissement</h3>
        <div class="grid sm:grid-cols-2 gap-4 text-sm">
          <div class="p-4 rounded-xl bg-white/5">
            <p class="text-slate-500 text-xs uppercase mb-1">Nom</p>
            <p class="text-white">Centre Hospitalier SGHL</p>
          </div>
          <div class="p-4 rounded-xl bg-white/5">
            <p class="text-slate-500 text-xs uppercase mb-1">Localisation</p>
            <p class="text-white">Pointe-Noire, République du Congo</p>
          </div>
          <div class="p-4 rounded-xl bg-white/5">
            <p class="text-slate-500 text-xs uppercase mb-1">Réception</p>
            <p class="text-white">+242 06 000 00 00</p>
          </div>
          <div class="p-4 rounded-xl bg-white/5">
            <p class="text-slate-500 text-xs uppercase mb-1">Urgences</p>
            <p class="text-white">24h/24 — 7j/7</p>
          </div>
        </div>
        <p class="text-slate-500 text-xs mt-4 leading-relaxed">
          L'application couvre l'ensemble du parcours patient : enregistrement à la réception,
          consultation, hospitalisation, analyses de laboratoire, dispensation en pharmacie et règlement à la caisse.
        </p>
      </div>

      <div class="page-card p-6">
        <h3 class="text-white font-semibold mb-4">ℹ️ Aide rapide</h3>
        <ul class="space-y-2 text-sm">
          <li class="text-slate-400">
            <span class="text-teal-400">Connexion staff :</span> email professionnel + OTP
          </li>
          <li class="text-slate-400">
            <span class="text-teal-400">Nouveau patient :</span> Patients → + Ajouter → noter l'email portail
          </li>
          <li class="text-slate-400">
            <span class="text-teal-400">Facturation :</span> chercher par nom ou email portail
          </li>
          <li class="text-slate-400">
            <span class="text-teal-400">Admin :</span> redirections, design, sync portails
          </li>
        </ul>
        <p class="text-slate-600 text-[10px] mt-5">
          © {{ annee }} SGHL — Tous droits réservés.<br />
          Développé pour la gestion hospitalière intégrée.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { statsService } from '../services/api.js'

const stats = ref({})
const annee = new Date().getFullYear()

const modules = [
  { icon: '🏪', titre: 'Réception & Patients', desc: 'Enregistrement, dossier, QR code, portail patient' },
  { icon: '🩺', titre: 'Parcours clinique', desc: 'Salle d\'attente, urgences, consultations, ordonnances' },
  { icon: '🛏️', titre: 'Hospitalisation', desc: 'Admissions, chambres, lits, géolocalisation' },
  { icon: '🔬', titre: 'Laboratoire & Pharmacie', desc: 'Analyses, banque de sang, stock médicaments' },
  { icon: '💰', titre: 'Caisse & Finance', desc: 'Facturation, clients privilégiés, comptes banque' },
  { icon: '⚙️', titre: 'Administration', desc: 'Pilotage, redirections, structure, statistiques' },
]

const roles = [
  { icon: '⚙️', nom: 'Administrateur', acces: 'Accès total + configuration' },
  { icon: '📋', nom: 'Secrétaire générale', acces: 'Toutes les pages opérationnelles' },
  { icon: '👨‍⚕️', nom: 'Médecin', acces: 'Consultations, patients, ordonnances' },
  { icon: '💉', nom: 'Infirmier(ère)', acces: 'Soins, salle d\'attente, chambres' },
  { icon: '🏪', nom: 'Réceptionniste', acces: 'Accueil, patients, facturation' },
  { icon: '🧑', nom: 'Patient', acces: 'Mon espace personnel uniquement' },
]

const chiffres = computed(() => [
  { icon: '👥', label: 'Patients', value: stats.value.patients ?? '—' },
  { icon: '🛏️', label: 'Hospitalisés', value: stats.value.hospitalises ?? '—' },
  { icon: '🩺', label: 'Consultations', value: stats.value.consultations ?? '—' },
  { icon: '🩸', label: 'Poches de sang', value: stats.value.poches_sang ?? '—' },
])

onMounted(async () => {
  try {
    stats.value = await statsService.dashboard()
  } catch {
    stats.value = {}
  }
})
</script>
