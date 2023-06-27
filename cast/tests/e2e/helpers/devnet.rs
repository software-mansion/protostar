use ctor::{ctor, dtor};
use url::Url;
use std::process::{Command, Stdio};
use std::string::ToString;
use std::thread;
use std::time::Duration;

pub const URL: &str = "http://127.0.0.1:5055/rpc";
pub const NETWORK: &str = "testnet";
const SEED: u32 = 1_053_545_548;

#[cfg(test)]
#[ctor]
fn start_devnet() {
    let port = Url::parse(URL).unwrap().port().unwrap_or(80).to_string();
    Command::new("starknet-devnet")
        .args([
            "--port",
            &port,
            "--seed",
            &SEED.to_string(),
            "--sierra-compiler-path",
            "tests/utils/cairo/bin/starknet-sierra-compile",
        ])
        .stdout(Stdio::null())
        .spawn()
        .expect("Failed to start devnet!");

    thread::sleep(Duration::from_secs(10));
}

#[cfg(test)]
#[dtor]
fn stop_devnet() {
    let port = Url::parse(URL).unwrap().port().unwrap_or(80).to_string();
    Command::new("pkill")
        .args([
            "-f",
            &format!(
                "starknet-devnet.*{}.*{}",
                &port,
                &SEED.to_string()
            )[..],
        ])
        .spawn()
        .expect("Failed to kill devnet processes");
}
