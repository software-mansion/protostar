from array_sum_test import array_sum
from starkware.cairo.common.alloc import alloc

func test_array_sum_external() {
    const ARRAY_SIZE = 3;

    // Allocate an array.
    let (ptr) = alloc();

    // Populate some values in the array.
    assert [ptr] = 9;
    assert [ptr + 1] = 16;
    assert [ptr + 2] = 25;

    // Call array_sum to compute the sum of the elements.
    let sum = array_sum(arr=ptr, size=ARRAY_SIZE);

    assert sum = 6 + 25 + 9; // Assert the result

    return ();
}
