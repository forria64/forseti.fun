<template>
  <footer class="footer">
    <div class="footer-container">
      <!-- Left: ICP logo and text -->
      <div class="footer-left">
        <a href="https://internetcomputer.org/" class="icp-link" target="_blank" rel="noopener noreferrer">
          100% on-chain
          <img src="/icp.png" alt="ICP Logo" class="icp-logo" />
        </a>
      </div>
      <!-- Right: Social buttons (moved from center, now right-aligned) -->
      <div class="footer-right">
        <a href="https://x.com/forsetidotfun" class="social-button social-x" target="_blank" rel="noopener noreferrer"></a>
        <a href="https://t.me/forsetidotfun" class="social-button social-telegram" target="_blank" rel="noopener noreferrer"></a>
        <a href="https://github.com/forria64/forseti.fun" class="social-button social-github" target="_blank" rel="noopener noreferrer"></a>
        <a href="https://odin.fun/token/2dld" class="social-button social-odin" target="_blank" rel="noopener noreferrer"></a>
      </div>
    </div>
    <!-- Preload hover icons for smooth transitions -->
    <link rel="preload" as="image" href="/x-hover.png" />
    <link rel="preload" as="image" href="/telegram-hover.png" />
    <link rel="preload" as="image" href="/github-hover.png" />
    <link rel="preload" as="image" href="/odin-hover.png" />
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
  height: 100px;
  background-color: #141313;
  z-index: 1000;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  padding: 3rem 3rem 3rem 3rem;
}

.footer-container {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
}

.footer-left {
  display: flex;
  align-items: center;
}
.icp-link {
  display: flex;
  align-items: center;
  color: #3f3f3f;
  text-decoration: none;
  font-size: 1rem;
}
.icp-logo {
  height: 15px;
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* Remove .footer-center */

.footer-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.social-button {
  display: inline-block;
  width: 3rem;
  height: 3rem;
  background-size: contain;
  background-repeat: no-repeat;
  margin: 0 0.25rem;
  transition: background-image 0.2s;
}
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

@media (max-width: 675px) {
  .social-button {
    width: 1.5rem;
    height: 1.5rem;
    margin: 0 0.15rem;
  }
  .icp-link {
    font-size: 0.60rem;
  }
  .icp-logo {
    height: 10px;
    margin-left: 0.25rem;
  }
  .footer {
    height: 50px;
    padding-left: 3rem;
    padding-right: 3rem;
  }
  .footer-right {
    gap: 0.15rem;
  }
}
</style>