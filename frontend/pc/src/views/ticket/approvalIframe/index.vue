<template>
  <div class="approval-iframe">
    <approveList
      :is-iframe="true"
      :service-id="serviceId">
    </approveList>
  </div>
</template>

<script>
  import approveList from '../ApprovalList.vue';
  export default {
    name: 'TicketApprovalIframe',
    components: {
      approveList,
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
