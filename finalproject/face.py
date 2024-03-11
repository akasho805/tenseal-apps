import ckks_demo as ts
from deepface import DeepFace
import base64
import math

# Common functions for writing and reading data

def write_data(file_name, file_content):
    """
    Write data to a file.

    Parameters:
        file_name (str): The name of the file.
        file_content (bytes): The content to be written to the file.
    """
    if type(file_content) == bytes:
        # Convert bytes to base64
        file_content = base64.b64encode(file_content)

    with open(file_name, 'wb') as f:
        f.write(file_content)

def read_data(file_name):
    """
    Read data from a file.

    Parameters:
        file_name (str): The name of the file.

    Returns:
        bytes: The content read from the file.
    """
    with open(file_name, 'rb') as f:
        file_content = f.read()

    return base64.b64decode(file_content)

# Client side

img1 = "../downloads/IMG1.jpg"
img2 = "../downloads/alia3.jpg"

# Extract facial embeddings using DeepFace
img1_embedding = DeepFace.represent(img1, model_name="Facenet")
img2_embedding = DeepFace.represent(img2, model_name="Facenet")

# Initialize encryption context
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
context.generate_galois_keys()
context.global_scale = 2**40

# Serialize and save secret key
secret_context = context.serialize(save_secret_key=True)
write_data(file_name='secret.txt', file_content=secret_context)

# Make context public and serialize
context.make_context_public()
public_context = context.serialize()
write_data(file_name='public.txt', file_content=public_context)

# Cleanup
del context, secret_context, public_context

# Encryption

# Flatten the list of embedding values
img1_embedding_values_flat = [list(face.values())[0] for face in img1_embedding]
img2_embedding_values_flat = [list(face.values())[0] for face in img2_embedding]

# Flatten the nested list
img1_embedding_values_flat = [val for sublist in img1_embedding_values_flat for val in sublist]
img2_embedding_values_flat = [val for sublist in img2_embedding_values_flat for val in sublist]

# Create plain tensors
plain_tensor1 = ts.plain_tensor(img1_embedding_values_flat, dtype="float")
plain_tensor2 = ts.plain_tensor(img2_embedding_values_flat, dtype="float")

# Load secret key context
context = ts.context_from(read_data('secret.txt'))

# Encrypt vectors
enc_v1 = ts.ckks_vector(context, plain_tensor1)
enc_v2 = ts.ckks_vector(context, plain_tensor2)

# Serialize and save encrypted vectors
write_data(file_name="enc_v1.txt", file_content=enc_v1.serialize())
write_data(file_name="enc_v2.txt", file_content=enc_v2.serialize())

# Cleanup
del context, enc_v1, enc_v2

# Cloudside computations

# Load public key context
context = ts.context_from(read_data('public.txt'))

# Load encrypted vectors
enc_v1 = ts.lazy_ckks_vector_from(read_data(file_name="enc_v1.txt"))
enc_v2 = ts.lazy_ckks_vector_from(read_data(file_name="enc_v2.txt"))

# Link vectors to the public context
enc_v1.link_context(context)
enc_v2.link_context(context)

# Compute squared euclidean distance
euclidean_squared = enc_v1 - enc_v2
euclidean_squared = euclidean_squared.dot(euclidean_squared)

# Serialize and save result
write_data(file_name="euclidean_squared.txt", file_content=euclidean_squared.serialize())

# Cleanup
del context, enc_v1, enc_v2, euclidean_squared

# Client side decryption

# Load secret key context
context = ts.context_from(read_data('secret.txt'))

# Load encrypted result
euclidean_squared = ts.lazy_ckks_vector_from(read_data(file_name="euclidean_squared.txt"))
euclidean_squared.link_context(context)

# Decrypt and compute euclidean distance
euclidean_dist = math.sqrt(euclidean_squared.decrypt()[0])

# Output result
if euclidean_dist < 10:
    print("same person")
else:
    print("not same person")
