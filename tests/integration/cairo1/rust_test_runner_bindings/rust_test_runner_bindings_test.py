from pathlib import Path

from protostar.cairo import protostar_rust_bindings


async def test_print(datadir: Path):
    test_path = datadir / "simple_test.cairo"
    result = protostar_rust_bindings.run_tests(str(test_path))
    assert result
    for name, single_result in result:
        if "success" in name:
            assert "success" in str(single_result).lower()
        elif "panic" in name:
            assert "panic" in str(single_result).lower()
        else:
            assert False, "test should either succeed or panic"
