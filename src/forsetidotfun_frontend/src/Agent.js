// File: /src/Agent.js

// Import the generated actor creation function and canister ID from your declarations.
import { createActor, canisterId as backendCanisterId } from 'declarations/forsetidotfun_backend';

// Create the actor with the required agent options for local development.
const actor = createActor(backendCanisterId, {
  agentOptions: {
    host: 'https://ic0.app', // Adjust if needed.
  },
});

export default actor;

