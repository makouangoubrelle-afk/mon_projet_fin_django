<template>
  <div class="p-6 bg-[#111827] rounded-xl border border-white/5">
    <h3 class="text-xl font-bold mb-4">Gestion Facturation</h3>
    <div class="flex gap-2 mb-6">
      <input v-model="facture.montant" placeholder="Montant" class="bg-[#070d1e] p-2 rounded" />
      <button @click="ajouterFacture" class="bg-violet-600 px-4 py-2 rounded">Ajouter</button>
    </div>
    <div v-for="(f, i) in factures" :key="i" class="flex justify-between p-2 border-b border-white/5">
      <span>{{ f.montant }} FCFA</span>
      <button @click="factures.splice(i, 1)" class="text-red-400 text-xs">Supprimer</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const factures = ref([]);
const facture = ref({ montant: '' });
const ajouterFacture = () => { factures.value.push({...facture.value}); facture.value.montant = ''; };
</script>