<template>
  <div class="page"><div class="header"><h1><i class="fas fa-prescription-bottle"></i> Ordonnances</h1><button class="btn btn-primary"><i class="fas fa-plus"></i> Nouvelle</button></div><div class="card"><div class="header-bar"><h5>Liste des Ordonnances</h5></div><div class="table-responsive"><table class="table"><thead><tr><th>Patient</th><th>Docteur</th><th>Médicament</th><th>Dose</th><th>Quantité</th><th>Statut</th></tr></thead><tbody><tr v-for="pres in prescriptions" :key="pres.id"><td>{{ pres.patient }}</td><td>{{ pres.doctor }}</td><td>{{ pres.med }}</td><td>{{ pres.dose }}</td><td>{{ pres.qty }}</td><td><span class="badge">{{ pres.status }}</span></td></tr></tbody></table></div></div></div>
</template>

<script setup>
import { ref } from 'vue'
const prescriptions = ref([
  { id: 1, patient: 'Pierre Martin', doctor: 'Dr. Dupont', med: 'Aspirin', dose: '500mg', qty: 30, status: 'Validée' },
  { id: 2, patient: 'Sophie Bernard', doctor: 'Dr. Rousseau', med: 'Amoxicilline', dose: '250mg', qty: 20, status: 'En Attente' },
])
</script>

<style scoped>
.page { padding: 20px; }
.header { display: flex; justify-content: space-between; background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db; }
.header h1 { margin: 0; color: #2c3e50; }
.card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header-bar { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 15px 20px; }
.header-bar h5 { margin: 0; }
.table { width: 100%; border-collapse: collapse; margin: 0; }
.table thead th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
.table tbody td { padding: 12px; border-bottom: 1px solid #ecf0f1; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; background: #3498db; color: white; font-size: 11px; }
.btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; background: #3498db; color: white; font-size: 12px; }
.btn-primary { background: #3498db; }
</style>