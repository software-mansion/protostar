IDENTITY_CONTRACT = """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """

FORMATTED_CONTRACT = """%lang starknet

@view
func identity(arg) -> (res : felt):
    return (arg)
end
"""

UNFORMATTED_CONTRACT = """%lang starknet

@view
func identity(arg


) -> (res : felt):
    return (arg)
end
"""

BROKEN_CONTRACT = "I LOVE CAIRO"
