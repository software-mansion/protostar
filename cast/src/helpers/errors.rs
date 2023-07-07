// todo: move errors here
use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum MissingAccountError {
    AccountNotProvided,
    AccountNotAvailableInNetwork,
}

impl Error for MissingAccountError {}

impl fmt::Display for MissingAccountError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            MissingAccountError::AccountNotProvided => write!(f, "account not found in Scarb.toml, nor provided using CLI!"),
            MissingAccountError::AccountNotAvailableInNetwork => write!(f, "account is not deployed to requested network!"),
        }
    }
}

#[derive(Debug)]
pub enum MissingRpcUrlError {
    MissingRpcUrlError,
}

impl Error for MissingRpcUrlError {}

impl fmt::Display for MissingRpcUrlError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            MissingRpcUrlError::MissingRpcUrlError => write!(f, "rpc_url not found in Scarb.toml, nor provided using CLI!"),
        }
    }
}

#[derive(Debug)]
pub enum InvalidNetworkError {
    InvalidNetworkError,
}

impl Error for InvalidNetworkError {}

impl fmt::Display for InvalidNetworkError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            InvalidNetworkError::InvalidNetworkError => write!(f, "invalid network name provided, possible values are: testnet, testnet2, mainnet!"),
        }
    }
}