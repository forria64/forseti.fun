<template>
  <header class="header">
    <div class="header-left">
      <img src="/about.png" alt="Forseti Logo" class="about-logo" />
    </div>
    <div class="header-title">
      <router-link to="/" class="home-link">
        forseti<font style="color: #00e8e8;">.</font>fun
      </router-link>
    </div>
  </header>
</template>

<script setup>
// No additional script logic required.
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  padding-top: 1rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.header-left {
  margin-right: 1rem;
}

.about-logo {
  height: 40px; /* Adjust as needed */
  width: auto;
}

.header-title {
  font-size: 1.6rem;
  font-family: "Norse", serif;
  padding-bottom: 0.8rem;
}

@media (max-width: 675px) {
.header {
  padding-top: 1rem;
  padding-left: 2rem;
  padding-right: 2rem;
}

.header-left {
  margin-right: 0.5rem;
}

.about-logo {
  height: 30px; /* Adjust as needed */
  width: auto;
}

.header-title {
  font-size: 1rem;
  padding-bottom: 0.3rem;
}
}
</style>

