<!-- 💳 billing_module.vue — Module de facturation cockpitifié -->
<template>
  <div class="billing-container">
    <h2>Facturation</h2>
    <form @submit.prevent="submitInvoice">
      <input v-model="client" placeholder="Client" required />
      <input v-model.number="amount" type="number" placeholder="Montant" required />
      <button type="submit">Envoyer</button>
    </form>
    <p v-if="status">{{ status }}</p>
  </div>
</template>

<script>
export default {
  name: 'BillingModule',
  data() {
    return {
      client: '',
      amount: null,
      status: ''
    };
  },
  methods: {
    async submitInvoice() {
      try {
        const response = await fetch('/api/billing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ client: this.client, amount: this.amount })
        });
        const result = await response.json();
        this.status = result.message;
      } catch (error) {
        this.status = 'Erreur lors de l’envoi';
      }
    }
  }
};
</script>

<style scoped>
.billing-container {
  max-width: 400px;
  margin: auto;
}
</style>
