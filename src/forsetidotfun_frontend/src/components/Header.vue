<template>
  <header>
    <div class="top-left">
      <router-link to="/" class="home-link title">
        Forseti<font style="color: #00e8e8;">.</font>fun
      </router-link>
    </div>
    <!-- Single Menu Option Always Visible -->
    <div class="top-right">
      <router-link to="/about">ABOUT</router-link>
    </div>
  </header>
</template>

<script setup>
// No extra logic is required now.
</script>

<style scoped>
.top-left {
  position: absolute;
  top: 1rem;
  left: 1rem;
}

.top-right {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  gap: 1.5rem;
}

/* No mobile-specific rules needed now */
</style>

