<template>
  <div class="flex flex-col items-center justify-center p-8">
    <h2 class="text-xl font-bold text-white mb-2">Vérification OTP</h2>
    <p class="text-slate-400 mb-6 text-sm">Entrez le code reçu par email</p>
    
    <input 
      v-model="otpCode" 
      type="text" 
      maxlength="6" 
      placeholder="000000"
      class="w-40 bg-[#070d1e] border border-slate-700 p-4 rounded-xl text-white text-center text-3xl tracking-[0.5em] mb-6 focus:border-violet-500 outline-none"
    />
    
    <button 
      @click="verifyCode" 
      class="w-full max-w-xs bg-gradient-to-r from-violet-600 to-blue-600 py-3 rounded-xl font-bold text-white hover:opacity-90 transition"
    >
      Vérifier mon accès
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps(['email']);
const emit = defineEmits(['login-success']);
const otpCode = ref('');

const verifyCode = () => {
  // 1. Simulation de vérification (remplace par ton appel Axios/Fetch vers Django)
  if (otpCode.value.length === 6) {
    console.log(`Vérification du code ${otpCode.value} pour l'email ${props.email}`);
    
    // Si le code est correct, on passe à l'étape suivante
    emit('login-success'); 
  } else {
    alert("Veuillez entrer un code valide à 6 chiffres.");
  }
};
</script>