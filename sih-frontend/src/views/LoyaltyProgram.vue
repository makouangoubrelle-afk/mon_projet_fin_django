<template>
  <div class="page"><div class="header"><h1><i class="fas fa-gift"></i> Programme Fidélité</h1></div><div class="card"><div class="header-bar"><h5>Membres Programme</h5></div><div class="table-responsive"><table class="table"><thead><tr><th>Patient</th><th>Niveau</th><th>Points</th><th>Dépenses</th><th>Depuis</th></tr></thead><tbody><tr v-for="member in members" :key="member.id"><td>{{ member.patient }}</td><td><span :class="'badge tier-'+member.tier">{{ member.tier }}</span></td><td>{{ member.points }}</td><td>${{ member.spent }}</td><td>{{ member.since }}</td></tr></tbody></table></div></div></div>
</template>

<script setup>
import { ref } from 'vue'
const members = ref([
  { id: 1, patient: 'Pierre Martin', tier: 'gold', points: 2500, spent: '5000.00', since: '2023-01-15' },
  { id: 2, patient: 'Sophie Bernard', tier: 'silver', points: 1200, spent: '2400.00', since: '2023-06-20' },
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
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-size: 11px; }
.tier-gold { background: #f39c12; }
.tier-silver { background: #95a5a6; }
.tier-bronze { background: #a0522d; }
</style>