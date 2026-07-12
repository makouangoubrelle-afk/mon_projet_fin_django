<template>
  <div class="page"><div class="header"><h1><i class="fas fa-history"></i> Historique Paiements</h1></div><div class="card"><div class="header-bar"><h5>Historique par Patient</h5></div><div class="table-responsive"><table class="table"><thead><tr><th>Patient</th><th>Total Payé</th><th>Solde Restant</th><th>Dernier Paiement</th></tr></thead><tbody><tr v-for="history in histories" :key="history.id"><td>{{ history.patient }}</td><td>${{ history.paid }}</td><td>${{ history.balance }}</td><td>{{ history.last }}</td></tr></tbody></table></div></div></div>
</template>

<script setup>
import { ref } from 'vue'
const histories = ref([
  { id: 1, patient: 'Pierre Martin', paid: '2500.00', balance: '0.00', last: '2024-06-10' },
  { id: 2, patient: 'Sophie Bernard', paid: '1800.50', balance: '500.00', last: '2024-06-08' },
])
</script>

<style scoped>
.page { padding: 20px; }
.header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db; }
.header h1 { margin: 0; color: #2c3e50; }
.card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header-bar { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 15px 20px; }
.header-bar h5 { margin: 0; }
.table { width: 100%; border-collapse: collapse; margin: 0; }
.table thead th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
.table tbody td { padding: 12px; border-bottom: 1px solid #ecf0f1; }
</style>