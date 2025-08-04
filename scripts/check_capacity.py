from trustmark import TrustMark

# Initialize with the same settings we've been using
tm = TrustMark(verbose=False, model_type='Q', encoding_type=TrustMark.Encoding.BCH_SUPER)

# Get the capacity in bits
bit_capacity = tm.schemaCapacity()

# The library uses ASCII7 encoding, so 7 bits per character
char_capacity = bit_capacity // 7

print(f"Total payload with BCH_SUPER ECC: {bit_capacity} bits")
print(f"This allows for a message of up to {char_capacity} characters.") 