from pathlib import Path
import pytest
from string import Template
header = """
%lang starknet
%builtins pedersen range_check

from starkware.cairo.common.cairo_builtins import HashBuiltin

@storage_var
func target() -> (res : felt):
end

"""

case = Template("""
@external
func test-$file-$case{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}():
    let (target_contract) = target.read()
    assert target_contract=0
    target.write(1)
    let (target_contract2) = target.read()
    assert target_contract2=1
    return ()
end

""")

@pytest.fixture
def test_contracts():
    for file in range(1):
        cases = "".join([case.substitute(file=str(file), case=str(i)) for i in range(5)])
        content = header + cases
        print(content)
        with open(Path() / "tests" / f"test_file_{file}.cairo", "w") as f:
            f.write(content)


@pytest.mark.skip(reason="performance_test")
@pytest.mark.usefixtures("test_contracts")
@pytest.mark.usefixtures("init")
def test_testing_performance(protostar):
    protostar(["test", "tests"])
