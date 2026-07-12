<template>
  <div class="page-container">
    <div class="page-header">
      <h1><i class="fas fa-calendar"></i> Rendez-vous</h1>
      <button class="btn btn-primary" @click="showModal = true"><i class="fas fa-plus"></i> Nouveau RDV</button>
    </div>
    <div class="card">
      <div class="card-header"><h5>Liste des Rendez-vous</h5></div>
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr><th>Patient</th><th>Docteur</th><th>Date/Heure</th><th>Statut</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.patient }}</td>
              <td>{{ item.doctor }}</td>
              <td>{{ item.datetime }}</td>
              <td><span class="badge">{{ item.status }}</span></td>
              <td><button class="btn btn-sm btn-info"><i class="fas fa-eye"></i></button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <Modal v-if="showModal" @close="showModal = false" title="Nouveau Rendez-vous" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Modal from '../components/Modal.vue'

const showModal = ref(false)
const items = ref([
  { id: 1, patient: 'Pierre Martin', doctor: 'Dr. Dupont', datetime: '2024-06-15 10:00', status: 'Confirmé' },
  { id: 2, patient: 'Sophie Bernard', doctor: 'Dr. Rousseau', datetime: '2024-06-15 14:30', status: 'Confirmé' },
])
</script>

<style scoped>
.page-container { animation: fadeIn 0.3s; }
.page-header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #3498db; }
.page-header h1 { color: #2c3e50; margin: 0; }
.card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.card-header { background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 15px 20px; }
.card-header h5 { margin: 0; }
.table { width: 100%; border-collapse: collapse; margin: 0; }
.table thead th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
.table tbody td { padding: 12px; border-bottom: 1px solid #ecf0f1; }
.btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; background: #3498db; color: white; }
.btn-sm { padding: 4px 8px; }
.btn-info { background: #3498db; }
.badge { display: inline-block; padding: 4px 8px; border-radius: 4px; background: #27ae60; color: white; font-size: 11px; }
</style>