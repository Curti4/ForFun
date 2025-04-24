while True:
    temp_type = input("Enter the temperature type (C/F/K) or 'exit' to quit: ").strip().lower()
    if temp_type == 'exit':
        break
    if temp_type not in ['c', 'f', 'k']:
        print("Invalid temperature type. Please enter 'C', 'F', or 'K'.")
        continue
    try:
        temp_value = float(input(f"Enter the temperature in {temp_type.upper()}: "))
    except ValueError:
        print("Invalid temperature value. Please enter a number.")
        continue
    if temp_type == 'c':
        f_temp = (temp_value * 9/5) + 32
        k_temp = temp_value + 273.15
        print(f"{temp_value}°C = {f_temp:.2f}°F = {k_temp:.2f}K")
        break
    elif temp_type == 'f':
        c_temp = (temp_value - 32) * 5/9
        k_temp = c_temp + 273.15
        print(f"{temp_value}°F = {c_temp:.2f}°C = {k_temp:.2f}K")
        break
    elif temp_type == 'k':
        c_temp = temp_value - 273.15
        f_temp = (c_temp * 9/5) + 32
        print(f"{temp_value}K = {c_temp:.2f}°C = {f_temp:.2f}°F")
        break