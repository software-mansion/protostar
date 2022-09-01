func use_signed_int_hint() {
    %{
        def signed_int(felt: int) -> int:
            modulo = (PRIME // 2 - 1)
            if felt % modulo == felt:
                return felt
            else:
                return -(felt % modulo)
    %}
    return ();
}
