<template>
  <footer>
    <div class="bottom-left">
      <a href="https://internetcomputer.org/" class="icp">
        100% on-chain 
        <img src="/icp.png" alt="icp" class="icp-logo" />
      </a>
    </div>
    <div class="bottom-right">
    <a href="&#104;&#116;&#116;&#112;&#115;&#58;&#47;&#47;&#120;&#46;&#99;&#111;&#109;&#47;&#102;&#111;&#114;&#115;&#101;&#116;&#105;&#100;&#111;&#116;&#102;&#117;&#110;" class="&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#98;&#117;&#116;&#116;&#111;&#110;&#32;&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#120;"></a>
    <a href="&#104;&#116;&#116;&#112;&#115;&#58;&#47;&#47;&#116;&#46;&#109;&#101;&#47;&#102;&#111;&#114;&#115;&#101;&#116;&#105;&#100;&#111;&#116;&#102;&#117;&#110;" class="&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#98;&#117;&#116;&#116;&#111;&#110;&#32;&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#116;&#101;&#108;&#101;&#103;&#114;&#97;&#109;"></a>
      <a href="&#104;&#116;&#116;&#112;&#115;&#58;&#47;&#47;&#103;&#105;&#116;&#104;&#117;&#98;&#46;&#99;&#111;&#109;&#47;&#102;&#111;&#114;&#114;&#105;&#97;&#54;&#52;&#47;&#102;&#111;&#114;&#115;&#101;&#116;&#105;&#46;&#102;&#117;&#110;" class="&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#98;&#117;&#116;&#116;&#111;&#110;&#32;&#115;&#111;&#99;&#105;&#97;&#108;&#45;&#103;&#105;&#116;&#104;&#117;&#98;"></a>

      <a href="https://odin.fun/token/2dld" class="social-button social-odin"></a>
    </div>
  </footer>
</template>

<script setup>
// No additional logic is required for the footer.
</script>

<style scoped>
.bottom-left {
  position: absolute;
  left: 1rem;
  bottom: 0.8rem;
  font-size: 1.8rem;
}

.bottom-right {
  position: absolute;
  right: 1rem;
  bottom: 1rem;
}

.icp-logo {
  width: auto;
  height: 1.6rem;
  margin-left: -0.2rem;
  margin-bottom: 0.5rem;
  vertical-align: middle;
}

/* Social buttons displayed in a row */
.social-button {
  display: inline-block;
  width: 3rem;
  height: 3rem;
  background-size: contain;
  background-repeat: no-repeat;
  margin-left: 0.5rem;
}

.social-button:first-child {
  margin-left: 0;
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

@media (max-width: 768px) {
  .bottom-left {
    bottom: 3.8rem;
    font-size: 1.2rem;
  }
  .bottom-right {
    bottom: 4rem;
  }
  .icp-logo {
  height: 1.1rem;
  margin-left: -0.2rem;
  margin-bottom: 0.5rem;
}

.social-button {
  width: 1.8rem;
  height: 1.8rem;
  margin-left: 0.5rem;
}
}
</style>

