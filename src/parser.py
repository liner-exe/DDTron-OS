def parse(input_str: str):
    if not input_str.strip():
        return None, []
    
    index = input_str.find(" ")

    if index == -1:
        return input_str, []
    
    cmd = input_str[:index]
    args = input_str[index+1:]

    tokens = []
    current_token = ""
    is_in_quotes = False
    
    for char in args:
        if char == '"':
            if not is_in_quotes:
                is_in_quotes = True
            else:
                is_in_quotes = False
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
        elif char == ' ' and is_in_quotes is False:
            if current_token:
                tokens.append(current_token)
                current_token = ""
        else:
            current_token += char
    
    if current_token:
        tokens.append(current_token)

    if is_in_quotes:
        print("Error: Unclosed Quotes")
        return None, []
    
    return cmd, tokens