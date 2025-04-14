<template>
  <div class="chat-page">
    <!-- The scrollable chat area -->
    <div class="chat-box" ref="chatLog">
      <div
        v-for="(msg, index) in chatMessages"
        :key="index"
        class="message-container"
        :class="messageAlignment(msg.sender)"
      >
        <!-- Username line above the bubble -->
        <div class="username" :class="usernameAlignment(msg.sender)">
          <span :style="{ color: msg.sender === 'Forseti' ? '#FFF019' : userColor(msg.sender) }">
            {{ msg.sender }}
          </span>
        </div>

        <!-- The message bubble -->
        <div class="bubble">
          <div class="bubble-text">
            {{ msg.text }}
          </div>
          <div class="bubble-footer">
            <span class="timestamp">{{ formatTimestamp(msg.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- "Forseti is pondering..." transitional text positioned above input -->
    <transition name="fade">
      <div v-if="showPondering" class="pondering-message">
        Forseti is pondering your question...
      </div>
    </transition>

    <!-- Bottom input row -->
    <div class="input-row">
      <input
        v-model="promptText"
        class="prompt-input"
        placeholder="Public interface temporarily disabled"
        @keyup.enter="sendPrompt"
      />
      <button @click="sendPrompt" class="send-button"></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, inject, nextTick, watch } from 'vue';

// Actor from main.js
const actor = inject('actor');
if (!actor) {
  throw new Error('Actor not provided!');
}

const promptText = ref('');
const chatMessages = ref([]);
const chatLog = ref(null);
const showPondering = ref(false);

/** Sends user prompt to the backend */
async function sendPrompt() {
  const text = promptText.value.trim();
  if (!text) return;
  try {
    showPondering.value = true;
    setTimeout(() => (showPondering.value = false), 2000);
    await actor.prompt(text);
    promptText.value = '';
  } catch (error) {
    console.error('Error sending prompt:', error);
  }
}

/** Poll runes every second */
async function pollRunes() {
  try {
    const runes = await actor.get_runes();
    const messages = [];
    runes.forEach((rune) => {
      messages.push({ 
        sender: rune.username, 
        text: rune.prompt, 
        timestamp: rune.timestamp 
      });
      messages.push({ 
        sender: 'Forseti', 
        text: rune.response, 
        timestamp: rune.timestamp 
      });
    });
    chatMessages.value = messages;
  } catch (error) {
    console.error('Error fetching runes:', error);
  }
}

/** Auto-scroll chat to bottom when new messages arrive */
watch(chatMessages, async (newVal, oldVal) => {
  if (newVal.length > oldVal.length) {
    await nextTick();
    if (chatLog.value) {
      chatLog.value.scrollTop = chatLog.value.scrollHeight;
    }
  }
});

let intervalId = null;
onMounted(() => {
  pollRunes();
  intervalId = setInterval(pollRunes, 1000);
});
onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId);
});

/** Alignment functions */
function messageAlignment(sender) {
  return sender === 'Forseti' ? 'left-container' : 'right-container';
}
function usernameAlignment(sender) {
  return sender === 'Forseti' ? 'username-left' : 'username-right';
}

/** Returns a diverse color for non-Forseti usernames */
function userColor(username) {
  const colors = [
    "#FF5733", "#33FF57", "#3357FF", "#F39C12", "#8E44AD",
    "#16A085", "#E74C3C", "#2ECC71", "#3498DB"
  ];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % colors.length;
  return colors[index];
}

function formatTimestamp(ts) {
  const date = new Date(Number(ts) * 1000); // Convert BigInt to Number then seconds to milliseconds
  return date.toLocaleString('en-US', {
    timeZone: 'UTC',
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  }) + ' UTC';
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 78vh;
  max-height: 78vh;
  max-width: 100%;
  margin-top: 3vh;
  box-sizing: border-box;
  padding: 0rem;
  position: relative;
}

.chat-box {
  flex: 1;
  background-color: #1a1818;
  border-radius: 8px 8px 0 0;
  padding: 1rem;
  overflow-y: auto;
  margin-bottom: 0;
}

/* Custom turquoise scrollbar */
.chat-box::-webkit-scrollbar {
  width: 8px;
}
.chat-box::-webkit-scrollbar-track {
  background: #2b2929;
  border-radius: 8px;
}
.chat-box::-webkit-scrollbar-thumb {
  background-color: #00e8e8;
  border-radius: 8px;
}

.message-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 1rem;
}
.left-container {
  align-items: flex-start;
}
.right-container {
  align-items: flex-end;
}

.username {
  font-size: 0.8rem;
  font-weight: bold;
  margin-bottom: 0.2rem;
}
.username-left {
  text-align: left;
}
.username-right {
  text-align: right;
}

.bubble {
  background-color: #2b2929;
  color: #f3f4f7;
  border-radius: 8px;
  padding: 0.8rem;
  position: relative;
  width: 60%;
}
.bubble-text {
  font-size: 1rem;
  line-height: 1.4rem;
  white-space: pre-wrap;
}
.bubble-footer {
  margin-top: -0.8rem;
  text-align: right;
}
.timestamp {
  font-size: 0.7rem;
  opacity: 0.6;
}

/* Pondering message positioned above the input row */
.pondering-message {
  position: absolute;
  bottom: 4rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.8rem;
  color: #00e8e8;
  pointer-events: none;
  font-family: "Norse", serif;
  z-index: 10;
}

/* Bottom input row */
.input-row {
  display: flex;
  align-items: center;
  background-color: #1a1818;
  border-radius: 0 0 8px 8px;
  padding: 0.5rem;
  flex-shrink: 0;
}

.prompt-input {
  flex: 1;
  background-color: #211f1f;
  color: #f3f4f7;
  border: none;
  font-size: 1rem;
  padding: 0.8rem;
  margin-right: 0.5rem;
  font-family: "Norse", serif;
  border-radius: 4px;
}
.prompt-input::placeholder {
  font-family: "Norse", serif;
  color: red;
}

.send-button {
  background-color: #00e8e8;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 2.5rem;
  height: 2.5rem;
  background-image: url('/arrow.png');
  background-size: 70%;
  background-repeat: no-repeat;
  background-position: center;
}
@media (max-width: 675px) {
.chat-page {
  height: 82vh;
  max-height: 82vh;
  max-width: 100%;
  padding: 0.5rem;
  margin-top: 2vh;
}

.chat-box {
  padding: 1rem;
  margin-bottom: 0;
}

/* Scrollbar dimensions */
.chat-box::-webkit-scrollbar {
  width: 6px;
}
.chat-box::-webkit-scrollbar-track {
  border-radius: 6px;
}
.chat-box::-webkit-scrollbar-thumb {
  border-radius: 6px;
}
.message-container {
  width: 100%;
  margin-bottom: 1rem;
}
.username {
  font-size: 0.6rem;
  margin-bottom: 0.2rem;
}
.bubble {
  border-radius: 8px;
  padding: 0.8rem;
  width: 60%;
}
.bubble-text {
  font-size: 0.6rem;
  line-height: 1rem;
}
.bubble-footer {
  margin-top: -1rem;
}
.timestamp {
  font-size: 0.5rem;
}
.pondering-message {
  bottom: 4rem;
  left: 50%;
  font-size: 0.6rem;
}
.input-row {
  border-radius: 0 0 8px 8px;
  padding: 0.5rem;
  flex-shrink: 0;
}
.prompt-input {
  font-size: 0.75rem;
  padding: 0.8rem;
  margin-right: 0.5rem;
}
.send-button {
  width: 2.2rem;
  height: 2.2rem;
  background-size: 70%;
}
}
</style>

