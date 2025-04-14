<template>
  <footer class="footer">
    <div class="footer-container">
      <!-- Left: ICP logo and text -->
      <div class="footer-left">
        <a href="https://internetcomputer.org/" class="icp-link">
          100% on-chain
          <img src="/icp.png" alt="ICP Logo" class="icp-logo" />
        </a>
      </div>
      <!-- Center: Social buttons -->
      <div class="footer-center">
        <a href="https://x.com/forsetidotfun" class="social-button social-x"></a>
        <a href="https://t.me/forsetidotfun" class="social-button social-telegram"></a>
        <a href="https://github.com/forria64/forseti.fun" class="social-button social-github"></a>
        <a href="https://odin.fun/token/2dld" class="social-button social-odin"></a>
      </div>
      <!-- Right: Copyright text -->
      <div class="footer-right">
        © 2025 Onchain Graphics
      </div>
    </div>
  </footer>
</template>

<script setup>
// No additional script logic required.
</script>

<style scoped>
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px; /* Adjust height as needed */
  background-color: #141313;
  z-index: 1000;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding-left: 2rem;
  padding-right: 2rem;
}

.footer-container {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
}

/* Left side: ICP logo and text; using color 3f3f3f */
.footer-left {
  display: flex;
  align-items: center;
}
.icp-link {
  display: flex;
  align-items: center;
  color: #3f3f3f;  /* New color for ICP text */
  text-decoration: none;
  font-size: 1rem;
}
.icp-logo {
  height: 15px; /* Adjust size as needed */
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* Center: Social buttons */
.footer-center {
  text-align: center;
}
.social-button {
  display: inline-block;
  width: 3rem;
  height: 3rem;
  background-size: contain;
  background-repeat: no-repeat;
  margin: 0 0.5rem;
}
/* Social button images and hover effects */
.social-x {
  background-image: url('/x.png');
}
.social-x:hover {
  background-image: url('/x-hover.png');
}
.social-telegram {
  background-image: url('/telegram.png');
}
.social-telegram:hover {
  background-image: url('/telegram-hover.png');
}
.social-github {
  background-image: url('/github.png');
}
.social-github:hover {
  background-image: url('/github-hover.png');
}
.social-odin {
  background-image: url('/odin.png');
}
.social-odin:hover {
  background-image: url('/odin-hover.png');
}

/* Right side: Copyright text, using color 3f3f3f */
.footer-right {
  text-align: right;
  font-size: 1rem;
  color: #3f3f3f;
}

@media (max-width: 675px) {
.social-button {
  width: 1.25rem;
  height: 1.25rem;
  margin: 0 0.25rem;
  padding-bottom: 0.25rem;
}
.footer-right {
  font-size: 0.60rem;
}
.icp-link {
  font-size: 0.60rem;
}
.icp-logo {
  height: 10px; /* Adjust size as needed */
  margin-left: 0.25rem;
}
.footer {
  height: 50px; /* Adjust height as needed */
  padding-left: 2rem;
  padding-right: 2rem;
}
}
</style>

