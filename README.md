 ```
 ╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔════╗╔══╗
 ║╔══╝║╔═╗║║╔═╗║║╔═╗║║╔══╝║╔╗╔╗║╚╣╠╝
 ║╚══╗║║ ║║║╚═╝║║╚══╗║╚══╗╚╝║║╚╝ ║║ 
 ║╔══╝║║ ║║║╔╗╔╝╚══╗║║╔══╝  ║║   ║║ 
╔╝╚╗  ║╚═╝║║║║╚╗║╚═╝║║╚══╗ ╔╝╚╗ ╔╣╠╗
╚══╝  ╚═══╝╚╝╚═╝╚═══╝╚═══╝ ╚══╝ ╚══╝
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v2.0.0
```

This project deploys a multi-canister application on the Internet Computer. The application consists of a Rust backend, a Vue-based frontend, and a custom `llama_cpp_canister` for language model inference.

## Prerequisites

Before deploying in a development environment, ensure you have the following installed and configured:
- [DFX (Internet Computer SDK)](https://internetcomputer.org/docs/current/developer-docs/quickstart)
- [Node.js (>= 16.0.0)](https://nodejs.org/)
- [npm (>= 7.0.0)](https://www.npmjs.com/)
- [Python 3](https://www.python.org/) (for running the model loader script)
- A local network setup via DFX (typically started with `dfx start`)

## Deployment in a Development Environment

Follow these steps to deploy the application locally:

1. **Deploy the Canisters**

   Run the following command from the project root directory to deploy all canisters:

   ```bash
   dfx deploy
   ```

   When prompted during the initialization of the **forsetidotfun_backend** canister, supply the **llama_cpp_canister** principal ID as the argument.

2. **Update Canister Settings**

   After deployment, add the **forsetidotfun_backend** canister as a controller to the **llama_cpp_canister**. Replace `<forsetidotfun_backend principal ID>` with the actual principal ID of your backend canister:

   ```bash
   dfx canister update-settings --add-controller <forsetidotfun_backend principal ID> llama_cpp_canister --local
   ```

3. **Upload and Initialize the Model**

   Use the provided Python script to upload and initialize your model. Execute the following command while pointing to your model file:

   ```bash
   python3 scripts/model_loader.py --model-file models/Llama-3.2-1B-Instruct-Q4_K_M.gguf --network local
   ```

   This script chunks the model file, uploads it to the `llama_cpp_canister`, and performs initialization of the model.

## Additional Information

- **Development Workflow:**  
  For local development, you can run the frontend with Vite using:
  ```bash
  npm run start
  ```
  and monitor updates to your Rust backend with `dfx deploy` as needed.

- **Configuration Files:**  
  - The `dfx.json` contains configurations for all canisters.
  - The Rust canister interface is defined in `src/forsetidotfun_backend/forsetidotfun_backend.did`.
  - The frontend uses the `Agent.js` file to interact with the deployed backend canister.

- **Troubleshooting:**  
  - Ensure that your local DFX network is running (`dfx start`).
  - If deployment fails, check the logs and verify that all required environment variables are correctly set.
  - Confirm that the correct principal IDs are used when prompted, especially for the `llama_cpp_canister`.

## Re-enabling the Public Interface

If you need to re-enable the public interface in the future:
- Uncomment the service block in `src/forsetidotfun_backend/forsetidotfun_backend.did`.
- Update the frontend placeholder text as necessary.

Happy coding and enjoy building with Forseti!
