from tests.integration.pure_cairo_vm.library import get_three

func test_simple_passing() {
    assert 1=1;
    return ();
}

func test_simple_failing() {
    assert 1=3;
    return ();
}


func test_simple_import_function() {
    let three = get_three();

    assert three = 3;
    return ();
}