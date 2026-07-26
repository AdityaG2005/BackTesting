from app.core.nlp_strategy import generate_strategy_code, validate_syntax, compile_strategy_class

description = "Buy when the closing price is higher than the previous day's close, sell when it's lower."

print("Generating strategy code...")
code = generate_strategy_code(description)
print("\n--- Generated Code ---")
print(code)

print("\n--- Syntax Check ---")
is_valid, error = validate_syntax(code)
print(f"Valid: {is_valid}")
if not is_valid:
    print(f"Error: {error}")

if is_valid:
    print("\n--- Compiling Strategy Class ---")
    try:
        strategy_class = compile_strategy_class(code)
        print(f"Successfully compiled: {strategy_class}")
        instance = strategy_class()
        print(f"Successfully instantiated: {instance}")
    except Exception as e:
        print(f"Compilation failed: {e}")

        