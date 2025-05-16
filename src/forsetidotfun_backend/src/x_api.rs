use crate::model_api::ModelApi;
use regex::Regex;

/// Generate a Forseti quote for a given topic and return it directly.
/// This does not store or queue the quote; it simply returns the generated text.
pub async fn get_quote(model_api: &ModelApi, topic: Option<String>) -> Result<String, String> {
    let topic_ref = topic.as_deref();
    let quote = model_api.generate_forseti_quote(topic_ref.unwrap_or("wisdom")).await?;
    let cleaned_quote = remove_special_tokens(&quote);
    Ok(cleaned_quote)
}

/// Removes special tokens and control characters from the LLM output.
fn remove_special_tokens(s: &str) -> String {
    // Remove <|im_start|>assistant<|im_end|>, <|im_start|>user<|im_end|>, and any <...> tag
    let re = Regex::new(r"<\|im_start\|>assistant<\|im_end\>|<\|im_start\|>user<\|im_end\>|<[^>]*>").unwrap();
    // Step 1: Remove special tokens
    let mut cleaned = re.replace_all(s, "").to_string();
    // Step 2: Remove control characters (non-printable)
    cleaned = Regex::new(r"[\x00-\x1F\x7F]").unwrap().replace_all(&cleaned, "").to_string();
    // Step 3: Remove HTML entities (e.g., &nbsp;, &amp;)
    cleaned = Regex::new(r"&[a-zA-Z]+;").unwrap().replace_all(&cleaned, "").to_string();
    // Optional: Trim and collapse whitespace
    cleaned = cleaned.trim().to_string();
    cleaned
}