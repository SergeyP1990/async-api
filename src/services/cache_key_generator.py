def generate_key(index: str, params: dict):
    final_key = f"{index}::"
    for key, value in params.items():
        final_key += f"{key}::{value}::"
    return final_key[:-2]
