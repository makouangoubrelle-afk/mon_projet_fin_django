<template>
  <div class="space-y-8">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <button v-for="section in sections" :key="section.key" @click="selectedSection = section.key"
        :class="['rounded-3xl p-4 text-center transition-all border', 
        selectedSection === section.key ? 'nav-pill-active border-cyan-400' : 'nav-pill border-white/10']">
        <div class="text-xl font-bold">{{ section.label }}</div>
        <div class="text-xs text-slate-400 mt-1">{{ countItems(section.key) }} élé</div>
      </button>
    </div>
    <div v-if="selectedSection === 'enregistrements'" class="space-y-6">
      <div class="page-card p-6">
        <h3 class="text-lg font-semibold mb-4">Enregistrer patient</h3>
        <form @submit.prevent="addRegistration" class="grid md:grid-cols-5 gap-4">
          <input v-model="newReg.nom" placeholder="Nom" class="input-field" required />
          <input v-model="newReg.tel" placeholder="Téléphone" class="input-field" required />
          <input v-model="newReg.motif" placeholder="Motif" class="input-field" required />
          <select v-model="newReg.statut" class="input-field">
            <option value="En attente">En attente</option>
            <option value="En cours">En cours</option>
            <option value="Complété">Complété</option>
          </select>
          <button type="submit" class="action-button">Enregistrer</button>
        </form>
      </div>
      <div class="space-y-2">
        <div v-for="reg in registrations" :key="reg.id" class="page-card p-3 flex justify-between items-center">
          <div>
            <p class="font-semibold text-white">{{ reg.nom }}</p>
          </div>
          <button @click="removeRegistration(reg.id)" class="text-red-400 text-xs">✕</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue';
const selectedSection = ref('enregistrements');
const sections = [
  { key: 'enregistrements', label: 'Enregistrements' },
  { key: 'rendezv', label: 'Rendez-vous' },
  { key: 'files', label: 'Files' },
];
const registrations = ref([
  { id: 1, nom: 'Amina Doumbia', tel: '+242 06 123 456', motif: 'Consultation', statut: 'En attente' },
]);
const newReg = ref({ nom: '', tel: '', motif: '', statut: 'En attente' });
const addRegistration = () => {
  if (newReg.value.nom && newReg.value.tel) {
    registrations.value.push({
      id: Math.max(...registrations.value.map(r => r.id), 0) + 1,
      ...newReg.value,
    });
    newReg.value = { nom: '', tel: '', motif: '', statut: 'En attente' };
  }
};
const removeRegistration = (id) => {
  registrations.value = registrations.value.filter(r => r.id !== id);
};
const countItems = (key) => {
  const counts = {
    enregistrements: registrations.value.length,
    rendezv: 1,
    files: registrations.value.length,
  };
  return counts[key] || 0;
};
</script>
<style scoped>
.input-field {
  @apply rounded-xl bg-white/5 border border-white/10 px-4 py-2 text-white;
}
</style>