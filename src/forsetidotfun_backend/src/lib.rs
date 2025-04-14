mod model_api;
mod web_api;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk_macros::{init, pre_upgrade, post_upgrade, query, update};
use model_api::ModelApi;
use std::cell::RefCell;

thread_local! {
    static MODEL_API: RefCell<Option<ModelApi>> = RefCell::new(None);
}

#[derive(CandidType, Deserialize)]
struct Config {
    llama_canister_id: Principal,
}

#[init]
fn init(llama_canister_id: String) {
    let principal = Principal::from_text(llama_canister_id)
        .expect("Invalid canister ID");
    MODEL_API.with(|api| {
        *api.borrow_mut() = Some(ModelApi::new(principal));
    });
}

/// Save necessary state before upgrade
#[pre_upgrade]
fn pre_upgrade() {
    // Save the current llama_canister_id as a String if available.
    let maybe_api = MODEL_API.with(|api| api.borrow().clone());
    if let Some(api) = maybe_api {
        ic_cdk::storage::stable_save((api.llama_canister_id.to_text(),))
            .expect("Stable save failed");
    }
}

/// Restore state after upgrade
#[post_upgrade]
fn post_upgrade() {
    // Retrieve the stored llama_canister_id from stable storage.
    let (llama_canister_id,): (String,) =
        ic_cdk::storage::stable_restore().expect("Stable restore failed");
    let principal = Principal::from_text(llama_canister_id)
        .expect("Invalid canister ID during post_upgrade");
    MODEL_API.with(|api| {
        *api.borrow_mut() = Some(ModelApi::new(principal));
    });
}

/// Exposed update endpoint that enqueues the prompt request.
/// It returns an immediate acknowledgement that execution has begun.
#[update]
async fn prompt(prompt_text: String) -> Result<String, String> {
    let model_api = MODEL_API.with(|api| {
        api.borrow()
           .as_ref()
           .expect("ModelApi not initialized")
           .clone()
    });
    web_api::prompt(&model_api, prompt_text)
        .await
        .map(|_| "Prompt execution started".to_string())
}

#[query]
fn health() -> String {
    "ok".to_string()
}

#[query]
fn get_config() -> Option<Config> {
    MODEL_API.with(|api| {
        api.borrow().as_ref().map(|model_api| Config {
            llama_canister_id: model_api.llama_canister_id,
        })
    })
}

/// Exposed query endpoint that returns all recorded rune entries.
#[query]
fn get_runes() -> Vec<web_api::RuneRecord> {
    web_api::get_runes()
}

