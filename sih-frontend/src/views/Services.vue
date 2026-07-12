<template>
  <div class="page-container services-page">
    <div class="page-header">
      <div>
        <h1><i class="fas fa-briefcase-medical"></i> Services Complémentaires</h1>
        <p>Tableau des services spéciaux : ambulances, urgences, banque de sang et stock médical.</p>
      </div>
    </div>

    <div class="card service-grid">
      <div class="service-card-summary" v-for="service in services" :key="service.id">
        <div class="service-icon" :class="service.color"><i :class="service.icon"></i></div>
        <div>
          <h4>{{ service.name }}</h4>
          <p>{{ service.description }}</p>
          <span class="badge" :class="service.statusClass">{{ service.status }}</span>
        </div>
      </div>
    </div>

    <div class="card mt-4">
      <div class="card-header"><h5>Inventaire Services</h5></div>
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Description</th>
              <th>Disponibilité</th>
              <th>Contact</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="service in services" :key="service.id">
              <td>{{ service.name }}</td>
              <td>{{ service.short }}</td>
              <td><span :class="'badge ' + service.statusClass">{{ service.status }}</span></td>
              <td>{{ service.contact }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
const services = [
  { id: 1, name: 'Ambulances', description: 'Interventions rapides 24/7.', short: 'Véhicules et équipes réactives.', status: 'Disponible', statusClass: 'success', contact: '+225 01 23 45 67', icon: 'fas fa-ambulance', color: 'blue' },
  { id: 2, name: 'Urgences', description: 'Salle d’urgences prête à recevoir.', short: 'Soins immédiats en cas critique.', status: 'Opérationnel', statusClass: 'info', contact: '+225 01 23 45 68', icon: 'fas fa-procedures', color: 'red' },
  { id: 3, name: 'Banque de Sang', description: 'Stocks de sang sécurisés.', short: 'Réserves et compatibilité rapide.', status: 'Suffisant', statusClass: 'warning', contact: '+225 01 23 45 69', icon: 'fas fa-tint', color: 'purple' },
  { id: 4, name: 'Stock Médical', description: 'Matériel et consommables disponibles.', short: 'Contrôle des inventaires médicaux.', status: 'Stable', statusClass: 'secondary', contact: '+225 01 23 45 70', icon: 'fas fa-boxes', color: 'green' }
]
</script>

<style scoped>
.page-container {
  animation: fadeIn 0.3s ease-in;
}

.page-header {
  background: linear-gradient(135deg, #13547a, #80d0c7);
  color: white;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 14px 35px rgba(8, 37, 64, 0.12);
}

.page-header h1 {
  margin: 0;
}

.page-header p {
  margin-top: 10px;
  color: rgba(255, 255, 255, 0.92);
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
  padding: 20px;
}

.service-card-summary {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #f8fbff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e4edf6;
}

.service-icon {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  color: white;
  font-size: 20px;
}

.service-icon.blue { background: #3498db; }
.service-icon.red { background: #e74c3c; }
.service-icon.purple { background: #8e44ad; }
.service-icon.green { background: #27ae60; }

.service-card-summary h4 {
  margin: 0 0 8px 0;
}

.service-card-summary p {
  margin: 0 0 10px 0;
  color: #5e6f85;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 16px 14px;
  border-bottom: 1px solid #eef2f7;
}

.table thead th {
  color: #2c3e50;
  background: #f7fbff;
  font-weight: 700;
}

.badge {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  color: white;
}

.badge.success { background: #27ae60; }
.badge.info { background: #3498db; }
.badge.warning { background: #f39c12; }
.badge.secondary { background: #7f8c8d; }

.mt-4 { margin-top: 24px; }
</style>