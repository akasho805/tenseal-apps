import tenseal as ts

# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40

# Encrypt two numbers
enc_num1 = ts.ckks_vector(context, [5])  # Replace with any number
enc_num2 = ts.ckks_vector(context, [3])  # Replace with any number

# Sum the two encrypted numbers
enc_sum = enc_num1 + enc_num2

# Decrypt the result
decrypted_result = enc_sum.decrypt()

# Round each element in the decrypted vector
rounded_decrypted_result = [round(element) for element in decrypted_result]

# Print the result
print("Rounded Decrypted Result (Sum):", rounded_decrypted_result)
