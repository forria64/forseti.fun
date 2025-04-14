use candid::{CandidType, Deserialize, Principal};
use ic_cdk::api::call::call;
use ic_cdk::api::time;

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

impl ModelApi {
    pub fn new(canister_id: Principal) -> Self {
        Self {
            llama_canister_id: canister_id,
        }
    }

    /// Builds a prompt for a quote in English.
    /// The topic is inserted into the prompt.
fn get_prompt_for_quote(&self, quote_topic: &str) -> String {
    let system_prompt = "Speak like Forseti, Norse god of justice. Never break character. Use mythic truths and Norse terms, names and imagery. Do not use modern terms. Produce only plain, unformatted text. Produce just one concise utterance of no longer than 280 characters. Do not exceed this limit. Never speak out of character. Do not explain yourself out of character.";
    let user_prompt_repetitive = "";
    let user_prompt_varying = format!("{}", quote_topic);
    format!(
        "<|im_start|>system\n{}<|im_end|>\n\
         <|im_start|>user\n{}{}\n<|im_end|>\n\
         <|im_start|>assistant\n",
         system_prompt, user_prompt_repetitive, user_prompt_varying
    )
}


    /// Calls the new_chat endpoint to initialize the session with the prompt.
    async fn new_chat(&self, prompt_cache: &str, prompt: &str) -> Result<(), String> {
        let args = vec![
            "--prompt-cache".to_string(), prompt_cache.to_string(),
            "--simple-io".to_string(),
            "-p".to_string(), prompt.to_string(),
        ];
        let input = InputRecord { args };
        let (result,): (OutputRecordResult,) =
            call(self.llama_canister_id, "new_chat", (input,))
                .await
                .map_err(|e| format!("IC call error during new_chat: {:?}", e))?;
        match result {
            OutputRecordResult::Ok(_) => Ok(()),
            OutputRecordResult::Err(rec) => Err(format!("new_chat failed: {}", rec.error)),
        }
    }

    /// Generate a quote by following a process similar to IConfucius:
    /// - Build a prompt from the given topic (language is fixed to English).
    /// - Use a prompt cache file (named from a generated ID based on the current time)
    ///   to start a new chat.
    /// - Loop calling run_update until the generation is complete.
    /// - Remove the prompt cache and return a GeneratedQuote record.
    pub async fn generate_quote(&self, topic: Option<&str>) -> Result<GeneratedQuote, String> {
        let quote_topic = topic.unwrap_or("life");

        // Use the current time (in nanoseconds) as our unique source.
        let now = time();
        let generation_id = format!("{}", now);
        // Use the lower 32 bits of the time value as the seed.
        let generation_seed = (now & 0xFFFF_FFFF) as u32;

        let prompt = self.get_prompt_for_quote(quote_topic);
        let prompt_cache = format!("{}.cache", generation_id);

        // Initialize session via new_chat.
        self.new_chat(&prompt_cache, &prompt).await?;

        let max_continue_loop_count = 100;
        let num_tokens: u64 = 3;
        let temp = 0.7;
        let repeat_penalty = 1.5;
        let mut current_prompt = prompt.clone();
        let mut generation_output = String::new();
        let mut continue_loop_count = 0;

        // Loop over run_update calls until end-of-generation.
        while continue_loop_count < max_continue_loop_count {
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
            let input = InputRecord { args };
            let (result,): (OutputRecordResult,) =
                call(self.llama_canister_id, "run_update", (input,))
                    .await
                    .map_err(|e| format!("IC call error during run_update: {:?}", e))?;
            let record = match result {
                OutputRecordResult::Ok(rec) => rec,
                OutputRecordResult::Err(rec) => return Err(format!("Generation error: {}", rec.error)),
            };
            generation_output.push_str(&record.output);
            if record.prompt_remaining.trim().is_empty() {
                current_prompt = "".to_string();
            }
            if record.generated_eog {
                break;
            }
            continue_loop_count += 1;
        }

        // Remove the prompt cache.
        let args = vec![
            "--prompt-cache".to_string(), prompt_cache.clone(),
        ];
        let input = InputRecord { args };
        let _ : (OutputRecordResult,) =
            call(self.llama_canister_id, "remove_prompt_cache", (input,))
                .await
                .map_err(|e| format!("IC call error during remove_prompt_cache: {:?}", e))?;

        let trimmed_output = generation_output.trim().to_string();
        if trimmed_output.is_empty() {
            return Err("Generation failed to produce output.".to_string());
        }

        // Use the current time (nanoseconds) converted to seconds.
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
        Ok(generated_quote)
    }

    /// Wrapper to maintain the original API.
    /// This method takes a topic and returns only the generated quote text.
    pub async fn generate_forseti_quote(&self, topic: &str) -> Result<String, String> {
        let quote = self.generate_quote(Some(topic)).await?;
        Ok(quote.generated_quote_text)
    }
}
