<template>
  <div class="page-container">
    <!-- Header now includes mobile menu -->
    <Header />

    <!-- Main Content loaded via routing -->
    <router-view />

    <!-- Footer Component -->
    <Footer />
  </div>
</template>

<script setup>
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';
</script>

<style scoped>
.page-container {
  position: relative;
  min-height: 100vh;
  width: 100%;
  background-image: url("/background.png");
  background-repeat: no-repeat;
  background-size: cover;
  font-size: 3rem;
  overflow: hidden;
}
</style>

