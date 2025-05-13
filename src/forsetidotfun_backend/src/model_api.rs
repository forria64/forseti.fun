use candid::{CandidType, Deserialize, Principal};
use ic_cdk::api::call::call;
use ic_cdk::api::{time, canister_balance as cycles};
use std::collections::HashMap;
use std::cell::RefCell;

#[derive(CandidType, Deserialize, Debug)]
struct InputRecord {
    args: Vec<String>,
}

#[derive(CandidType, Deserialize, Debug)]
struct RunOutputRecord {
    status_code: u16,
    output: String,
    conversation: String,
    error: String,
    prompt_remaining: String,
    generated_eog: bool,
}

#[derive(CandidType, Deserialize, Debug)]
enum OutputRecordResult {
    Ok(RunOutputRecord),
    Err(RunOutputRecord),
}

/// Record returned from quote generation.
#[derive(CandidType, Deserialize, Debug)]
pub struct GeneratedQuote {
    pub generation_id: String,
    pub generation_language: String,
    pub generation_topic: String,
    pub generation_seed: u32,
    pub generated_timestamp: u64,
    pub generated_by_llm_id: String,
    pub generation_prompt: String,
    pub generated_quote_text: String,
}

#[derive(Clone)]
pub struct ModelApi {
    pub llama_canister_id: Principal,
}

// Simple in-memory cache map for demonstration (not persistent across canister upgrades).
thread_local! {
    static PROMPT_CACHE_MAP: RefCell<HashMap<String, String>> = RefCell::new(HashMap::new());
}

impl ModelApi {
    pub fn new(canister_id: Principal) -> Self {
        ic_cdk::println!("[ModelApi::new] Initialized with canister_id: {}", canister_id);
        Self {
            llama_canister_id: canister_id,
        }
    }

    /// Builds a prompt for a quote in English.
    fn get_prompt_for_quote(&self, quote_topic: &str) -> String {
        ic_cdk::println!("[get_prompt_for_quote] Building prompt for topic: '{}'", quote_topic);
        let system_prompt = "You are Forseti, Norse god of justice. Your responses do not exceed 300 words.";
        let user_prompt_repetitive = "";
        let user_prompt_varying = format!("{}", quote_topic);
        let prompt = format!(
            "<|im_start|>system\n{}<|im_end|>\n\
             <|im_start|>user\n{}{}\n<|im_end|>\n\
             <|im_start|>assistant\n",
             system_prompt, user_prompt_repetitive, user_prompt_varying
        );
        ic_cdk::println!("[get_prompt_for_quote] Prompt built:\n{}", prompt);
        prompt
    }

    /// Calls the new_chat endpoint to initialize the session with the prompt.
    async fn new_chat(&self, prompt_cache: &str, prompt: &str) -> Result<(), String> {
        ic_cdk::println!("[new_chat] Initializing new chat with cache: '{}'", prompt_cache);
        let args = vec![
            "--prompt-cache".to_string(), prompt_cache.to_string(),
            "--simple-io".to_string(),
            "-p".to_string(), prompt.to_string(),
        ];
        ic_cdk::println!("[new_chat] Args: {:?}", args);
        let input = InputRecord { args };
        let (result,): (OutputRecordResult,) =
            call(self.llama_canister_id, "new_chat", (input,))
                .await
                .map_err(|e| format!("IC call error during new_chat: {:?}", e))?;
        match &result {
            OutputRecordResult::Ok(_) => ic_cdk::println!("[new_chat] new_chat succeeded"),
            OutputRecordResult::Err(rec) => ic_cdk::println!("[new_chat] new_chat failed: {}", rec.error),
        }
        match result {
            OutputRecordResult::Ok(_) => Ok(()),
            OutputRecordResult::Err(rec) => Err(format!("new_chat failed: {}", rec.error)),
        }
    }

    /// Returns a cache key based on topic (or user/session if available).
    fn get_cache_key(&self, topic: &str) -> String {
        let key = format!("forseti_{}.cache", topic.replace(' ', "_").to_lowercase());
        ic_cdk::println!("[get_cache_key] Cache key for topic '{}': '{}'", topic, key);
        key
    }

    /// Generate a quote, reusing the prompt cache for the topic if available.
    pub async fn generate_quote(&self, topic: Option<&str>) -> Result<GeneratedQuote, String> {
        // --- CYCLE USAGE DEBUGGING START ---
        let cycles_before = cycles();
        ic_cdk::println!("[generate_quote] Cycles before prompt generation: {}", cycles_before);
        // --- CYCLE USAGE DEBUGGING END ---

        let quote_topic = topic.unwrap_or("life");
        ic_cdk::println!("[generate_quote] Generating quote for topic: '{}'", quote_topic);
        let prompt = self.get_prompt_for_quote(quote_topic);

        let prompt_cache = self.get_cache_key(quote_topic);

        let is_new_chat = PROMPT_CACHE_MAP.with(|map| !map.borrow().contains_key(&prompt_cache));
        ic_cdk::println!("[generate_quote] is_new_chat: {}", is_new_chat);

        if is_new_chat {
            ic_cdk::println!("[generate_quote] Calling new_chat...");
            self.new_chat(&prompt_cache, &prompt).await?;
            PROMPT_CACHE_MAP.with(|map| map.borrow_mut().insert(prompt_cache.clone(), quote_topic.to_string()));
            ic_cdk::println!("[generate_quote] Cache inserted for '{}'", prompt_cache);
        }

        let max_continue_loop_count = 300;
        let num_tokens: u64 = 1024;
        let temp = 0.7;
        let repeat_penalty = 1.1;

        let now = time();
        let generation_id = format!("{}", now);
        let generation_seed = (now & 0xFFFF_FFFF) as u32;

        let mut generation_output = String::new();
        let mut continue_loop_count = 0;
        let mut prompt_ingestion_done = false;
        let mut current_prompt = prompt.clone();

        ic_cdk::println!("[generate_quote] Starting sophisticated generation loop...");

        // Sophisticated loop: first ingest prompt (if needed), then generate
        while continue_loop_count < max_continue_loop_count {
            ic_cdk::println!(
                "[generate_quote] Loop {}: prompt_cache='{}', num_tokens={}, temp={}, repeat_penalty={}, seed={}, prompt_ingestion_done={}",
                continue_loop_count, prompt_cache, num_tokens, temp, repeat_penalty, generation_seed, prompt_ingestion_done
            );
            let args = vec![
                "--prompt-cache".to_string(), prompt_cache.clone(),
                "--prompt-cache-all".to_string(),
                "--simple-io".to_string(),
                "--no-display-prompt".to_string(),
                "-n".to_string(), num_tokens.to_string(),
                "--seed".to_string(), generation_seed.to_string(),
                "--temp".to_string(), temp.to_string(),
                "--repeat-penalty".to_string(), repeat_penalty.to_string(),
                "-p".to_string(), current_prompt.clone(),
            ];
            ic_cdk::println!("[generate_quote] run_update args: {:?}", args);
            let input = InputRecord { args };
            let (result,): (OutputRecordResult,) =
                call(self.llama_canister_id, "run_update", (input,))
                    .await
                    .map_err(|e| format!("IC call error during run_update: {:?}", e))?;
            match &result {
                OutputRecordResult::Ok(rec) => ic_cdk::println!(
                    "[generate_quote] run_update OK: output='{}', prompt_remaining='{}', generated_eog={}",
                    rec.output, rec.prompt_remaining, rec.generated_eog
                ),
                OutputRecordResult::Err(rec) => ic_cdk::println!(
                    "[generate_quote] run_update ERR: error='{}', output='{}'",
                    rec.error, rec.output
                ),
            }
            let record = match result {
                OutputRecordResult::Ok(rec) => rec,
                OutputRecordResult::Err(rec) => return Err(format!("Generation error: {}", rec.error)),
            };

            generation_output.push_str(&record.output);

            // Prompt ingestion phase: keep sending prompt until prompt_remaining is empty
            if !prompt_ingestion_done {
                if record.prompt_remaining.trim().is_empty() {
                    // Prompt ingestion done, switch to generation phase
                    prompt_ingestion_done = true;
                    current_prompt = "".to_string();
                } else {
                    // Still ingesting prompt, keep sending the full prompt
                    current_prompt = prompt.clone();
                }
            } else {
                // Generation phase: send empty prompt to continue generation
                current_prompt = "".to_string();
            }

            if record.generated_eog {
                ic_cdk::println!("[generate_quote] End of generation reached.");
                break;
            }
            continue_loop_count += 1;
        }

        PROMPT_CACHE_MAP.with(|map| map.borrow_mut().remove(&prompt_cache));
        let args = vec![
            "--prompt-cache".to_string(), prompt_cache.clone(),
        ];
        let input = InputRecord { args };
        let _ : (OutputRecordResult,) =
            call(self.llama_canister_id, "remove_prompt_cache", (input,))
                .await
                .map_err(|e| format!("IC call error during remove_prompt_cache: {:?}", e))?;

        let trimmed_output = generation_output.trim().to_string();
        ic_cdk::println!("[generate_quote] Final output: '{}'", trimmed_output);
        if trimmed_output.is_empty() {
            ic_cdk::println!("[generate_quote] Generation failed to produce output.");
            return Err("Generation failed to produce output.".to_string());
        }

        let timestamp_secs = time() / 1_000_000_000;

        let generated_quote = GeneratedQuote {
            generation_id,
            generation_language: "en".to_string(),
            generation_topic: quote_topic.to_string(),
            generation_seed,
            generated_timestamp: timestamp_secs,
            generated_by_llm_id: self.llama_canister_id.to_text(),
            generation_prompt: prompt,
            generated_quote_text: trimmed_output,
        };

        // --- CYCLE USAGE DEBUGGING END ---
        let cycles_after = cycles();
        let cycles_used = if cycles_before > cycles_after {
            cycles_before - cycles_after
        } else {
            0
        };
        ic_cdk::println!(
            "[generate_quote] Cycles after prompt generation: {}. Estimated cycles used: {}",
            cycles_after,
            cycles_used
        );
        // --- CYCLE USAGE DEBUGGING END ---

        ic_cdk::println!("[generate_quote] Returning GeneratedQuote: {:?}", generated_quote);
        Ok(generated_quote)
    }

    /// Wrapper to maintain the original API.
    pub async fn generate_forseti_quote(&self, topic: &str) -> Result<String, String> {
        ic_cdk::println!("[generate_forseti_quote] Called with topic: '{}'", topic);
        let quote = self.generate_quote(Some(topic)).await?;
        ic_cdk::println!("[generate_forseti_quote] Output: '{}'", quote.generated_quote_text);
        Ok(quote.generated_quote_text)
    }
}