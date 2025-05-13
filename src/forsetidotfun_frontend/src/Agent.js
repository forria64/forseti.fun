// File: /src/Agent.js

// Import the generated actor creation function and canister ID from your declarations.
import { createActor, canisterId as backendCanisterId } from 'declarations/forsetidotfun_backend';

// To develop locally, replace the `host` with your local replica URL.
// For example, if you are using the DFX local environment, it might be 'http://localhost:4943'.
// Use 'https://ic0.app' in production.
const actor = createActor(backendCanisterId, {
  agentOptions: {
    host: 'https://ic0.app', // Adjust if needed.
  },
});

export default actor;

