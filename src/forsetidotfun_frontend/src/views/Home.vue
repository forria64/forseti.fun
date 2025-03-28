<template>
  <main>
    <img src="/forseti.png" alt="FORSETI" class="main-image" />
  </main>
</template>

<script setup>
// No extra logic required for the Home view.
</script>

<style scoped>
main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 4rem); /* Adjust for header/footer height if needed */
}
.main-image {
  max-width: 100%;
  height: 71vh;
}

@media (max-width: 768px) {
.main-image {
  height: 38vh;
}
}
</style>

