mod model_api;
mod web_api;
mod x_api;

use candid::{CandidType, Deserialize, Principal};
use ic_cdk_macros::{init, pre_upgrade, post_upgrade, query, update};
use model_api::ModelApi;
use std::cell::RefCell;

thread_local! {
    static MODEL_API: RefCell<Option<ModelApi>> = RefCell::new(None);
}

#[derive(CandidType, Deserialize)]
struct Config {
    llm_canister_id: Principal,
}

// Hardcoded ic-llm canister principal
const IC_LLM_CANISTER_ID: &str = "w36hm-eqaaa-aaaal-qr76a-cai";

#[init]
fn init() {
    let principal = Principal::from_text(IC_LLM_CANISTER_ID)
        .expect("Invalid hardcoded ic-llm canister ID");
    MODEL_API.with(|api| {
        *api.borrow_mut() = Some(ModelApi::new(principal));
    });
}

/// Save necessary state before upgrade
#[pre_upgrade]
fn pre_upgrade() {
    let maybe_api = MODEL_API.with(|api| api.borrow().clone());
    if let Some(api) = maybe_api {
        ic_cdk::storage::stable_save((api.llm_canister_id.to_text(),))
            .expect("Stable save failed");
    }
}

/// Restore state after upgrade
#[post_upgrade]
fn post_upgrade() {
    let (llm_canister_id,): (String,) =
        ic_cdk::storage::stable_restore().expect("Stable restore failed");
    let principal = Principal::from_text(llm_canister_id)
        .expect("Invalid canister ID during post_upgrade");
    MODEL_API.with(|api| {
        *api.borrow_mut() = Some(ModelApi::new(principal));
    });
}

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

#[update]
async fn get_quote() -> Result<String, String> {
    let model_api = MODEL_API.with(|api| {
        api.borrow()
           .as_ref()
           .expect("ModelApi not initialized")
           .clone()
    });
    x_api::get_quote(&model_api, None).await
}

#[query]
fn health() -> String {
    "ok".to_string()
}

#[query]
fn get_runes() -> Vec<web_api::RuneRecord> {
    web_api::get_runes()
}

