<template>
  <div class="exchange-view">
    <ExchangeCalculator />
  </div>
</template>

<script setup>
import ExchangeCalculator from '@/components/Exchange/ExchangeCalculator.vue';
</script>

<style lang="scss" scoped>
.exchange-view {
  padding-top: 0px;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
</style>