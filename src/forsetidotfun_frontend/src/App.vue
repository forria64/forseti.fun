<template>
  <div class="page-container">
    <!-- Header remains at the top -->
    <Header />

    <!-- Main Content loaded via routing -->
    <div class="main-content">
      <router-view />
    </div>

    <!-- Footer is fixed to the bottom -->
    <Footer />
  </div>
</template>

<script setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
</script>

<style scoped>
.page-container {
  position: relative;
  min-height: 100%;
  min-width: 100%;
  background-color: #141313; /* New solid background */
  font-size: 2.5rem;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 0 2rem 80px;
}

@media (max-width: 675px) {
.main-content {
  padding: 0 1rem 80px;
}
}
</style>

