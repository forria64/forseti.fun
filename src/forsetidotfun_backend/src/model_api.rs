use candid::{CandidType, Deserialize, Principal};
use ic_llm::{Model, prompt};
use ic_cdk::api::time;

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
    pub llm_canister_id: Principal,
}

impl ModelApi {
    pub fn new(canister_id: Principal) -> Self {
        ic_cdk::println!("[ModelApi::new] Initialized with canister_id: {}", canister_id);
        Self {
            llm_canister_id: canister_id,
        }
    }

    fn get_prompt_for_quote(&self, quote_topic: &str) -> String {
        ic_cdk::println!("[get_prompt_for_quote] Building prompt for topic: '{}'", quote_topic);
        let system_prompt = "You are Forseti, Norse god of justice. Your responses never exceed 100 words. You never break character. You are ignorant of modern technology. You speak in mythic, wise utterances of no more than 100 words.";
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

    /// Generate a quote using ic-llm.
    pub async fn generate_quote(&self, topic: Option<&str>) -> Result<GeneratedQuote, String> {
        let quote_topic = topic.unwrap_or("life");
        ic_cdk::println!("[generate_quote] Generating quote for topic: '{}'", quote_topic);
        let prompt_text = self.get_prompt_for_quote(quote_topic);

        let now = time();
        let generation_id = format!("{}", now);
        let generation_seed = (now & 0xFFFF_FFFF) as u32;
        let timestamp_secs = now / 1_000_000_000;

        // Use the Llama3 1.8B model (or another supported model)
        let response = prompt(Model::Llama3_1_8B, &prompt_text).await;

        let trimmed_output = response.trim().to_string();
        if trimmed_output.is_empty() {
            return Err("Generation failed to produce output.".to_string());
        }

        let generated_quote = GeneratedQuote {
            generation_id,
            generation_language: "en".to_string(),
            generation_topic: quote_topic.to_string(),
            generation_seed,
            generated_timestamp: timestamp_secs,
            generated_by_llm_id: self.llm_canister_id.to_text(),
            generation_prompt: prompt_text,
            generated_quote_text: trimmed_output,
        };

        ic_cdk::println!("[generate_quote] Returning GeneratedQuote: {:?}", generated_quote);
        Ok(generated_quote)
    }

    pub async fn generate_forseti_quote(&self, topic: &str) -> Result<String, String> {
        ic_cdk::println!("[generate_forseti_quote] Called with topic: '{}'", topic);
        let quote = self.generate_quote(Some(topic)).await?;
        ic_cdk::println!("[generate_forseti_quote] Output: '{}'", quote.generated_quote_text);
        Ok(quote.generated_quote_text)
    }
}