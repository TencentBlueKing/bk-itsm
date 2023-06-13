<template>
  <div class="attention-iframe">
    <attentionList :is-iframe="true" :service-id="serviceId"> </attentionList>
  </div>
</template>

<script>
  import attentionList from '../AttentionList.vue';
  export default {
    name: 'TicketAttentionIframe',
    components: {
      attentionList,
    },
    data() {
      return {
        serviceId: '',
      };
    },
    mounted() {
      this.serviceId = this.$route.query.service_in;
    },
  };
</script>

<style lang="scss" scoped>
</style>
