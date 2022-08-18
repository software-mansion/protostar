IDENTITY_CONTRACT = """
                %lang starknet

                @view
                func identity(arg) -> (res : felt):
                    return (arg)
                end
            """
