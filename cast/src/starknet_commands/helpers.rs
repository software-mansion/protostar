use starknet::core::types::FieldElement;
use anyhow::Result;

pub fn parse_number(contract_address_arg: &str) -> Result<FieldElement> {
  let contract_address = match &contract_address_arg[..2] {
      "0x" => FieldElement::from_hex_be(contract_address_arg)?,
      _ => FieldElement::from_dec_str(contract_address_arg)?,
  };
  Ok(contract_address)
}
