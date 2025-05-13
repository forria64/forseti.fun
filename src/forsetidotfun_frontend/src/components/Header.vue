<template>
  <header class="header">
    <router-link to="/" class="home-link">
      forseti<font style="color: #00e8e8;">.</font>fun
    </router-link>
    <button class="menu-btn" aria-label="Menu">
      <img src="/about.png" alt="Forseti Logo" class="about-logo" />
    </button>
  </header>
</template>

<script setup>
// No script needed
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 3rem 3rem 1.5rem 3rem;
  width: 100%;
  position: relative;
  box-sizing: border-box;
  min-height: 56px;
}

.home-link {
  font-size: 1.98rem; /* 10% smaller than 2.2rem */
  font-family: "Norse", serif;
  color: #f3f4f7;
  text-decoration: none;
  letter-spacing: 0.05em;
  text-align: left;
  margin-top: 0.3rem;
  margin-left: 0;
  padding: 0;
  line-height: 1;
}

.menu-btn {
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  height: 48px;
}

.about-logo {
  height: 48px;
  width: auto;
  display: block;
}

@media (max-width: 675px) {
  .about-logo {
    height: 28.16px; /* 32px reduced by 12% */
  }
  .home-link {
    margin-top: 0.4rem;
    font-size: 0.90rem;
  }
  .header {
    padding-top: 1rem;
    padding-bottom: 0rem;
    padding-left: 3rem;
    padding-right: 3rem;
    min-height: 40px;
  }
  .menu-btn {
    height: 28.16px; /* Match icon height for better alignment */
  }
}
</style>