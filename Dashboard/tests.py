import itertools

# Define character sets
numbers = "0123456789"
alphabets = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
special_symbols = "!@#$%^&*()-_=+[]{};:,.<>?/"

# Define categories as (Category Name, Character Set)
categories = [
    ("Numbers Only", numbers),
    ("Alphabets Only", alphabets),
    ("Alphabets + Special Symbols", alphabets + special_symbols),
    ("Alphabets + Numbers", alphabets + numbers),
    ("Alphabets + Numbers + Special Symbols", alphabets + numbers + special_symbols)
]

output_file = "combination.txt"

with open(output_file, "w") as file:
    for category_name, char_set in categories:
        file.write(f"\n--- Combinations for Category: {category_name} ---\n")
        # Loop for lengths 8 through 18
        for length in range(8, 19):
            file.write(f"\n--- Combinations of Length: {length} ---\n")
            # Generate all combinations (order does not matter)
            for combo in itertools.combinations(char_set, length):
                file.write("".join(combo) + "\n")

print(f"All combinations have been saved to '{output_file}'.")
