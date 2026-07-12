<template>
  <div class="page"><div class="header"><h1><i class="fas fa-list"></i> File d'Attente</h1><button class="btn btn-primary"><i class="fas fa-plus"></i> Ajouter</button></div><div class="card"><div class="header-bar"><h5>Patients en Attente</h5></div><div class="queue-list"><div v-for="item in queue" :key="item.id" class="queue-item"><div class="num">{{ item.pos }}</div><div class="info"><h6>{{ item.patient }}</h6><p>Priorité: <span :class="'p-'+item.priority">{{ item.priority }}</span></p></div><div class="actions"><button class="btn sm success"><i class="fas fa-check"></i></button></div></div></div></div></div>
</template>

<script setup>
import { ref } from 'vue'
const queue = ref([
  { id: 1, pos: 1, patient: 'Pierre Martin', priority: 'normal' },
  { id: 2, pos: 2, patient: 'Sophie Bernard', priority: 'high' },
  { id: 3, pos: 3, patient: 'Luc Fontaine', priority: 'normal' },
])
</script>

<style scoped>
.page { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db; }
.header h1 { margin: 0; color: #2c3e50; }
.card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header-bar { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 15px 20px; }
.header-bar h5 { margin: 0; }
.queue-list { padding: 20px; }
.queue-item { display: flex; align-items: center; padding: 15px; border: 1px solid #ecf0f1; border-radius: 4px; margin-bottom: 10px; background: #f8f9fa; }
.num { width: 40px; height: 40px; background: #3498db; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 15px; }
.info { flex: 1; }
.info h6 { margin: 0; color: #2c3e50; }
.info p { margin: 5px 0 0; font-size: 12px; color: #7f8c8d; }
.p-normal { color: #3498db; }
.p-high { color: #e74c3c; }
.btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; background: #3498db; color: white; font-size: 12px; }
.btn-primary { background: #3498db; }
.success { background: #27ae60; }
.sm { padding: 4px 8px; }
</style>