<template>
  <div class="community-view">
    <article>
      <Article />
    </article>
  </div>
</template>

<script setup lang="ts">
import Article from '@/components/Community/Article.vue'
</script>

<style scoped lang="scss">
.community-view {
  padding-top: 80px;
}

article {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;

  h1 {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 2rem;
  }
}
</style>