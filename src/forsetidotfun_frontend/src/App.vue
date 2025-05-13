<template>
  <div class="page-container">
    <Header />
    <div class="main-content">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Header from "./components/Header.vue";
import Footer from "./components/Footer.vue";
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #141313;
}

.main-content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  width: 100%;
  margin: 0 auto;
  padding: 0 3rem 100px; /* 100px = footer height */
  box-sizing: border-box;
}


@media (max-width: 675px) {
.main-content {
  padding: 0 2.6rem 150px; /* 100px = footer height */
}
}
</style>