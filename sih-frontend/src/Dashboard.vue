<template>
  <div class="dashboard">
    <div class="page-header">
      <h1><i class="fas fa-tachometer-alt"></i> Tableau de Bord</h1>
      <p>Bienvenue dans le système de gestion hospitalière</p>
    </div>

    <!-- Statistics Row -->
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-icon" style="color: #3498db;">
          <i class="fas fa-users"></i>
        </div>
        <div class="stat-number">245</div>
        <div class="stat-label">Patients Actifs</div>
      </div>
      <div class="stat-box">
        <div class="stat-icon" style="color: #e74c3c;">
          <i class="fas fa-hospital-user"></i>
        </div>
        <div class="stat-number">38</div>
        <div class="stat-label">Hospitalisés</div>
      </div>
      <div class="stat-box">
        <div class="stat-icon" style="color: #27ae60;">
          <i class="fas fa-stethoscope"></i>
        </div>
        <div class="stat-number">12</div>
        <div class="stat-label">Docteurs</div>
      </div>
      <div class="stat-box">
        <div class="stat-icon" style="color: #f39c12;">
          <i class="fas fa-money-bill"></i>
        </div>
        <div class="stat-number">$45,230</div>
        <div class="stat-label">Revenus du Mois</div>
      </div>
    </div>

    <!-- Main Content Sections -->
    <div class="content-grid">
      <!-- Gestion Médicale -->
      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-hospital"></i> Gestion Médicale</h5>
        </div>
        <div class="card-body">
          <div class="list-group">
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-stethoscope"></i> Consultations Programmées</h6>
                <span class="badge">12</span>
              </div>
              <small>Consultations prévues aujourd'hui</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-prescription-bottle"></i> Ordonnances en Attente</h6>
                <span class="badge warning">8</span>
              </div>
              <small>Ordonnances à valider</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-flask"></i> Tests Laboratoire</h6>
                <span class="badge info">15</span>
              </div>
              <small>Résultats en attente</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-hospital-user"></i> Hospitalisations</h6>
                <span class="badge danger">38</span>
              </div>
              <small>Patients actuellement hospitalisés</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Réception -->
      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-door-open"></i> Réception</h5>
        </div>
        <div class="card-body">
          <div class="list-group">
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-list"></i> File d'Attente</h6>
                <span class="badge warning">5</span>
              </div>
              <small>Patients en attente</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-calendar-check"></i> Rendez-vous Aujourd'hui</h6>
                <span class="badge info">18</span>
              </div>
              <small>Rendez-vous programmés</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-sign-in-alt"></i> Enregistrements</h6>
                <span class="badge success">34</span>
              </div>
              <small>Patients enregistrés</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Finances -->
      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-money-bill"></i> Finances</h5>
        </div>
        <div class="card-body">
          <div class="list-group">
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-file-invoice"></i> Factures Impayées</h6>
                <span class="badge danger">24</span>
              </div>
              <small>Total: $15,450</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-check-circle"></i> Paiements Aujourd'hui</h6>
                <span class="badge success">12</span>
              </div>
              <small>Total: $8,230</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Clients VIP -->
      <div class="card">
        <div class="card-header">
          <h5><i class="fas fa-crown"></i> Clients VIP</h5>
        </div>
        <div class="card-body">
          <div class="list-group">
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-crown"></i> Platinum</h6>
                <span class="badge danger">8</span>
              </div>
              <small>Réduction: 15%</small>
            </div>
            <div class="list-item">
              <div class="d-flex justify-content-between align-items-center">
                <h6><i class="fas fa-crown"></i> Gold</h6>
                <span class="badge warning">24</span>
              </div>
              <small>Réduction: 10%</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activities -->
    <div class="card mt-4">
      <div class="card-header">
        <h5><i class="fas fa-history"></i> Activités Récentes</h5>
      </div>
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Heure</th>
              <th>Action</th>
              <th>Utilisateur</th>
              <th>Détail</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>14:35</td>
              <td><i class="fas fa-check-circle" style="color: #27ae60;"></i> Consultation</td>
              <td>Dr. Jean Dupont</td>
              <td>Pierre Martin</td>
              <td><span class="badge success">Complété</span></td>
            </tr>
            <tr>
              <td>14:20</td>
              <td><i class="fas fa-file-invoice" style="color: #3498db;"></i> Facture</td>
              <td>Marie Leclerc</td>
              <td>Sophie Bernard</td>
              <td><span class="badge warning">En Attente</span></td>
            </tr>
            <tr>
              <td>14:05</td>
              <td><i class="fas fa-prescription-bottle" style="color: #3498db;"></i> Ordonnance</td>
              <td>Dr. Marie Rousseau</td>
              <td>Luc Fontaine</td>
              <td><span class="badge success">Validé</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
// Dashboard component logic here
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.page-header h1 {
  color: #2c3e50;
  margin: 0 0 5px 0;
  font-size: 28px;
}

.page-header p {
  color: #7f8c8d;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-box {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  padding: 15px 20px;
  border-bottom: 1px solid #ecf0f1;
}

.card-header h5 {
  margin: 0;
  font-size: 16px;
}

.card-body {
  padding: 20px;
}

.list-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.list-item {
  padding: 12px 0;
  border-bottom: 1px solid #ecf0f1;
}

.list-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.list-item h6 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #2c3e50;
}

.list-item small {
  color: #7f8c8d;
  display: block;
}

.d-flex {
  display: flex;
}

.justify-content-between {
  justify-content: space-between;
}

.align-items-center {
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #3498db;
  color: white;
  font-size: 11px;
  font-weight: bold;
}

.badge.success {
  background-color: #27ae60;
}

.badge.warning {
  background-color: #f39c12;
}

.badge.danger {
  background-color: #e74c3c;
}

.badge.info {
  background-color: #3498db;
}

.mt-4 {
  margin-top: 30px;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

.table thead th {
  background-color: #2c3e50;
  color: white;
  padding: 12px;
  text-align: left;
  font-weight: bold;
}

.table tbody td {
  padding: 12px;
  border-bottom: 1px solid #ecf0f1;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 24px;
  }
}
</style>
