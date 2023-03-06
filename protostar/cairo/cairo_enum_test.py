from .cairo_enum import CairoVersion


def test_cairo_enum_compatibility_with_template_paths():
    assert CairoVersion.cairo0.value == "cairo0"
    assert CairoVersion.cairo1.value == "cairo1"
