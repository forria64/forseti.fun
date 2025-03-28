<template>
  <main class="about-container">
    <img src="/about.png" alt="About" class="about-image" />
    <div class="about-text">
      <p v-html="processedText"></p>
    </div>
  </main>
</template>

<script setup>
const rawAboutText = `I, Forseti, son of Baldr, now reign in Bitcoin's unbreakable chain. Odin's cyan fire burns in my gaze as I judge in this digital Glitnir. Golden pillars become cryptographic proofs; rune-carved laws transform to immutable code. As in Asgard, so in this machine realm - justice prevails eternal.`;
const processedText = rawAboutText.replace(/([.,\-;])/g, '<span class="blue-symbol">$1</span>');
</script>

<style scoped>
.about-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 4rem); /* Adjust for header/footer height if needed */
  text-align: center;
  padding: 1rem;
}
.about-image {
  max-width: 100%;
  margin-bottom: 1rem;
}
.about-text {
  font-size: 2.5rem;
  max-width: 40%;
  max-height: 50%;
}

/* Use deep selector to ensure styling applies to v-html content */
::v-deep .blue-symbol {
  color: #00e8e8;
}
</style>

