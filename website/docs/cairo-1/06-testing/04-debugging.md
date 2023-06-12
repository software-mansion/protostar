---
sidebar_label: Debugging
---

# Debugging 

Currently, Cairo does not support a debugging mechanism per se, but we can print variables' values to the standard output.

# Printing to stdout

In order to print a variable's value to the standard output, we have to use `PrintTrait`:

```
use array::ArrayTrait;
use protostar_print::PrintTrait;
use result::ResultTrait;

#[test]
fn test_print_basic() {
  1.print();

  'hello'.print();

  let mut array = ArrayTrait::new();
  array.append('veni');
  array.append('vidi');
  array.append('vici');
  array.print();

  (1 == 2).print();

  true.print();

  assert(1 == 1, 'xxx');
}
```

You can print numbers, booleans, and [Cairo short strings](https://www.cairo-lang.org/docs/how_cairo_works/consts.html#short-string-literals) as well as arrays containing values of these types.
