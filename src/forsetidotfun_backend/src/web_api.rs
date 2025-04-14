use crate::model_api::ModelApi;
use candid::{CandidType, Deserialize};
use ic_cdk::api::time;
use ic_cdk::spawn;
use std::cell::RefCell;
use std::collections::VecDeque;
use regex::Regex;

#[derive(CandidType, Deserialize, Clone)]
pub struct RuneRecord {
    pub username: String,
    pub prompt: String,
    pub response: String,
    pub timestamp: u64,  // New field to record timestamp in seconds
}

#[derive(Clone)]
struct QueueJob {
    model_api: ModelApi,
    prompt_text: String,
    username: String,
}

// Global log of rune records.
thread_local! {
    static RUNES: RefCell<Vec<RuneRecord>> = RefCell::new(Vec::new());
    static JOB_QUEUE: RefCell<VecDeque<QueueJob>> = RefCell::new(VecDeque::new());
    static IS_PROCESSING: RefCell<bool> = RefCell::new(false);
}

/// Enqueues a job and starts processing if not already running.
fn enqueue_job(job: QueueJob) {
    JOB_QUEUE.with(|q| {
        q.borrow_mut().push_back(job);
    });
    IS_PROCESSING.with(|p| {
        if !*p.borrow() {
            *p.borrow_mut() = true;
            spawn(async {
                process_queue().await;
            });
        }
    });
}

/// Processes queued jobs sequentially.
async fn process_queue() {
    loop {
        let job_opt = JOB_QUEUE.with(|q| q.borrow_mut().pop_front());
        match job_opt {
            Some(job) => {
                if let Ok(response) = job.model_api.generate_forseti_quote(&job.prompt_text).await {
                    let cleaned_response = remove_special_tokens(&response);
                    // Record the current time in seconds.
                    let ts = time() / 1_000_000_000;
                    RUNES.with(|r| {
                        r.borrow_mut().push(RuneRecord {
                            username: job.username,
                            prompt: job.prompt_text,
                            response: cleaned_response,
                            timestamp: ts,
                        });
                    });
                }
            }
            None => break,
        }
    }
    IS_PROCESSING.with(|p| {
        *p.borrow_mut() = false;
    });
}

/// Initiates a prompt by enqueuing a job. Returns an immediate acknowledgement.
pub async fn prompt(model_api: &ModelApi, prompt_text: String) -> Result<(), String> {
    let username = generate_random_username();
    let job = QueueJob {
        model_api: model_api.clone(),
        prompt_text: prompt_text.clone(),
        username,
    };
    enqueue_job(job);
    Ok(())
}

/// Returns all rune records logged so far.
pub fn get_runes() -> Vec<RuneRecord> {
    RUNES.with(|r| r.borrow().clone())
}

/// Generates a random username based on a random Norse name and a random Roman numeral.
fn generate_random_username() -> String {
    let norse_names = [
        "Óðinn", "Þórr", "Loki", "Freyr", "Freyja", "Týr", "Baldur", 
        "Heimdallr", "Njörðr", "Frigg", "Sif", "Iðunn", "Bragi", 
        "Víðarr", "Skadi", "Úllr", "Mímir", "Ægir", "Rán", "Kvasir", "Eir", 
        "Nanna", "Sól", "Máni"
    ];
    let now = time(); // current time in nanoseconds
    let name_index = (now % (norse_names.len() as u64)) as usize;
    let name = norse_names[name_index];
    let num = (now % 10) + 1; // random number between 1 and 10
    let roman = int_to_roman(num as u32);
    format!("{} {}", name, roman)
}

/// Converts an integer to its Roman numeral representation.
fn int_to_roman(mut num: u32) -> String {
    let values = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ];
    let mut result = String::new();
    for &(value, symbol) in values.iter() {
        while num >= value {
            result.push_str(symbol);
            num -= value;
        }
    }
    result
}

fn remove_special_tokens(s: &str) -> String {
    let re = Regex::new(r"<[^>]*>|assistant\n").unwrap();
    re.replace_all(s, "").to_string()
}


