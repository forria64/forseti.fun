<template>
  <div class="chat-page">
    <div class="chat-box" ref="chatLog">
      <!-- Tutorial/onboarding messages -->
      <div v-for="(msg, index) in tutorialMessages" :key="'tutorial-' + index" class="message-container left-container">
        <div class="username username-left">
          <span style="color: #FFF019;">Forseti</span>
        </div>
        <div class="bubble">
          <div class="bubble-text">{{ msg.text }}</div>
          <div class="bubble-footer">
            <span class="timestamp">{{ msg.timestamp }}</span>
          </div>
        </div>
      </div>
      <!-- Actual chat messages -->
      <div
        v-for="(msg, index) in chatMessages"
        :key="index"
        class="message-container"
        :class="messageAlignment(msg.sender)"
      >
        <div class="username" :class="usernameAlignment(msg.sender)">
          <span :style="{ color: msg.sender === 'Forseti' ? '#FFF019' : userColor(msg.sender) }">
            {{ msg.sender }}
          </span>
        </div>
        <div class="bubble">
          <div class="bubble-text">{{ msg.text }}</div>
          <div class="bubble-footer">
            <span class="timestamp">{{ formatTimestamp(msg.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showPondering" class="pondering-message">
        Forseti is pondering your question...
      </div>
    </transition>

    <div class="input-row" v-if="!showPondering">
      <input
        v-model="promptText"
        class="prompt-input"
        :placeholder="inputPlaceholder"
        @keyup.enter="sendPrompt"
        autocomplete="off"
        :disabled="showPondering"
      />
      <button @click="sendPrompt" class="send-button" aria-label="Send" :disabled="showPondering"></button>
    </div>
    <div class="input-row" v-else>
      <input
        class="prompt-input"
        :placeholder="ponderingPlaceholder"
        disabled
      />
      <button class="send-button" aria-label="Send" disabled></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, inject, nextTick, watch } from 'vue';

const actor = inject('actor');
if (!actor) throw new Error('Actor not provided!');

const promptText = ref('');
const chatMessages = ref([]);
const chatLog = ref(null);
const showPondering = ref(false);

const inputPlaceholder = "Speak with the norse god of justice...";
const ponderingPlaceholder = "Speak with the norse god of justice...";

const tutorialMessages = [
  {
    text: "Hey, I'm Forseti, the Norse God of Justice. The form in which you see me is a slightly altered version of my first known depiction (~1680, Edda Oblongata manuscript).",
    timestamp: "Tutorial"
  },
  {
    text: "This dapp and the large language model you are using are hosted fully on-chain, on the Internet Computer Protocol (ICP). Every response is generated without any off-chain server infrastructure.",
    timestamp: "Tutorial"
  },
  {
    text: "Your conversations are public and visible to all. Please be respectful and worthy the wisdom of Forseti.",
    timestamp: "Tutorial"
  }
];

async function sendPrompt() {
  const text = promptText.value.trim();
  if (!text || showPondering.value) return;
  try {
    showPondering.value = true;
    promptText.value = '';
    setTimeout(() => {
      showPondering.value = false;
    }, 2000);
    await actor.prompt(text);
  } catch (error) {
    showPondering.value = false;
    console.error('Error sending prompt:', error);
  }
}

let intervalId = null;
let initialRunesFetched = false;
let hasWatcherRun = false;

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

    // Set flag after first fetch, but do NOT scroll here!
    if (!initialRunesFetched) {
      initialRunesFetched = true;
    }
  } catch (error) {
    console.error('Error fetching runes:', error);
  }
}

onMounted(() => {
  pollRunes();
  intervalId = setInterval(pollRunes, 1000);
});
onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId);
});

// Watcher: auto-scroll to bottom on every new rune after initial fetch
watch(chatMessages, async (newVal, oldVal) => {
  if (!hasWatcherRun) {
    hasWatcherRun = true;
    return; // skip first watcher run after initial fetch
  }
  if (initialRunesFetched && newVal.length > oldVal.length) {
    await nextTick();
    if (chatLog.value) {
      chatLog.value.scrollTop = chatLog.value.scrollHeight;
    }
  }
});

function messageAlignment(sender) {
  return sender === 'Forseti' ? 'left-container' : 'right-container';
}
function usernameAlignment(sender) {
  return sender === 'Forseti' ? 'username-left' : 'username-right';
}
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
  if (ts === "Tutorial") return "";
  const date = new Date(Number(ts) * 1000);
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
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  height: 10vh;
  scrollbar-color: #00e8e8 #2b2929; /* thumb color, track color */
  scrollbar-width: thin;
}

.chat-box {
  flex: 1 1 auto;
  min-height: 0;
  background-color: #1a1818;
  border-radius: 8px 8px 0 0;
  padding: 1rem;
  overflow-y: scroll;
  margin-bottom: 0;
}

.input-row {
  display: flex;
  align-items: center;
  background-color: #1a1818;
  border-radius: 0 0 8px 8px;
  padding: 0.5rem;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
  position: relative;
  z-index: 2;
}

/* Custom turquoise scrollbar */
.chat-page::-webkit-scrollbar {
  width: 8px;
}
.chat-page::-webkit-scrollbar-track {
  background: #2b2929;
  border-radius: 8px;
}
.chat-page::-webkit-scrollbar-thumb {
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
  margin-top: 1rem;
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
  color: #00e8e8;
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
  transition: background 0.2s, filter 0.2s;
}
.send-button:hover {
  background-color: #211f1f; /* matches .prompt-input background */
  /* No filter needed, arrow is already turquoise */
  background-image: url('/turqoise-arrow.png');
  background-size: 70%;
  background-repeat: no-repeat;
  background-position: center;
}

@media (max-width: 675px) {
  .chat-page {
    min-height: 0;
    max-width: 100%;
    padding: 0.5rem;
    margin-top: 2vh;
  }
  .chat-box {
    padding: 1rem;
    margin-bottom: 0;
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
    margin-top: 1rem;
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
    width: 100%;
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