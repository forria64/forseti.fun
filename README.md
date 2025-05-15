```
 ╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔════╗╔══╗
 ║╔══╝║╔═╗║║╔═╗║║╔═╗║║╔══╝║╔╗╔╗║╚╣╠╝
 ║╚══╗║║ ║║║╚═╝║║╚══╗║╚══╗╚╝║║╚╝ ║║ 
 ║╔══╝║║ ║║║╔╗╔╝╚══╗║║╔══╝  ║║   ║║ 
╔╝╚╗  ║╚═╝║║║║╚╗║╚═╝║║╚══╗ ╔╝╚╗ ╔╣╠╗
╚══╝  ╚═══╝╚╝╚═╝╚═══╝╚═══╝ ╚══╝ ╚══╝
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v3.0.0
```

This project deploys a multi-canister application on the Internet Computer. The application consists of a Rust backend, a Vue-based frontend, and a custom `llama_cpp_canister` for language model inference.

## Changelog

### v3.0.0


- Major frontend UI/UX improvements for mobile and desktop.
- Improved chat scroll logic:  
  - Chat now only auto-scrolls to bottom after the initial fetch and on new messages, not on every update.
- Send button now uses a turquoise arrow and hover background matches the input field.
- CSS fixes for mobile prompt input font size.
- Backend: Enhanced cycle usage debugging and prompt cache logic.
- Updated documentation and deployment instructions.

---

## Prerequisites

Before deploying in a development environment, ensure you have the following installed and configured:
- [DFX (Internet Computer SDK)](https://internetcomputer.org/docs/current/developer-docs/quickstart)
- [Node.js (>= 16.0.0)](https://nodejs.org/)
- [npm (>= 7.0.0)](https://www.npmjs.com/)
- [Python 3](https://www.python.org/) (for running the model loader script)
- A local network setup via DFX (typically started with `dfx start`)

Python 3 libraries for the model loader script (I'll package them properly at some point in the future):
- colorama
- pygame

Install with:
```bash
pip install colorama pygame
``` 
or just use system packages ¯\_(ツ)_/¯

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
   dfx canister update-settings --add-controller <forsetidotfun_backend principal ID> llama_cpp_canister
   ```

3. **Upload and Initialize the Model**

   Use the provided Python script to upload and initialize your model. Execute the following command while pointing to your model file:

   ```bash
   python3 scripts/model_loader.py
   ```

   This script chunks the model file, uploads it to the `llama_cpp_canister`, and performs initialization of the model.

## Additional Information

- **Configuration Files:**  
  - The `dfx.json` contains configurations for all canisters.
  - The Rust canister interface is defined in `src/forsetidotfun_backend/forsetidotfun_backend.did`.
  - The frontend uses the `Agent.js` file to interact with the deployed backend canister.

- **Troubleshooting:**  
  - Ensure that your local DFX network is running (`dfx start`).
  - If deployment fails, check the logs and verify that all required environment variables are correctly set.
  - Confirm that the correct principal IDs are used when prompted, especially for the `llama_cpp_canister`.


Happy coding and enjoy building with Forseti!
