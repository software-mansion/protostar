use starknet::core::types::FieldElement;
use anyhow::Result;

pub fn parse_number(number_as_str: &str) -> Result<FieldElement> {
  let contract_address = match &number_as_str[..2] {
      "0x" => FieldElement::from_hex_be(number_as_str)?,
      _ => FieldElement::from_dec_str(number_as_str)?,
  };
  Ok(contract_address)
}
