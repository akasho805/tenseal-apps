import ckks_demo as ts
from deepface import DeepFace
import base64
import math
import time

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

def client_server_model(img1_path, img2_path):
    print("===== Facial Recognition Using Homomorphic Encryption =====")

    # Client side
    print("\nClient: Initiating facial recognition process...")

    # Extract facial embeddings using DeepFace for image 1
    img1_embedding = DeepFace.represent(img1_path, model_name="Facenet")

    # Extract facial embeddings using DeepFace for image 2
    img2_embedding = DeepFace.represent(img2_path, model_name="Facenet")

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

    # Encryption for image 1
    img1_embedding_values_flat = [list(face.values())[0] for face in img1_embedding]
    img1_embedding_values_flat = [val for sublist in img1_embedding_values_flat for val in sublist]

    plain_tensor1 = ts.plain_tensor(img1_embedding_values_flat, dtype="float")

    # Load secret key context
    context = ts.context_from(read_data('secret.txt'))

    # Encrypt vector for image 1
    enc_vector1 = ts.ckks_vector(context, plain_tensor1)
    print("Client: Vector for image 1 encrypted.")

    # Serialize and save encrypted vector for image 1
    write_data(file_name="enc_vector1.txt", file_content=enc_vector1.serialize())
    print("Client: Encrypted vector for image 1 saved.")

    # Cleanup
    del context, enc_vector1

    # Encryption for image 2
    img2_embedding_values_flat = [list(face.values())[0] for face in img2_embedding]
    img2_embedding_values_flat = [val for sublist in img2_embedding_values_flat for val in sublist]

    plain_tensor2 = ts.plain_tensor(img2_embedding_values_flat, dtype="float")

    # Load secret key context
    context = ts.context_from(read_data('secret.txt'))

    # Encrypt vector for image 2
    enc_vector2 = ts.ckks_vector(context, plain_tensor2)
    print("Client: Vector for image 2 encrypted.")

    # Serialize and save encrypted vector for image 2
    write_data(file_name="enc_vector2.txt", file_content=enc_vector2.serialize())
    print("Client: Encrypted vector for image 2 saved.")

    # Cleanup
    del context, enc_vector2

    # Send the encrypted vectors to the server (you can use a network communication method here)

    # Server side (Cloudside Computations)

    # Load public key context
    context = ts.context_from(read_data('public.txt'))

    # Load encrypted vectors
    enc_vector1 = ts.lazy_ckks_vector_from(read_data(file_name="enc_vector1.txt"))
    enc_vector2 = ts.lazy_ckks_vector_from(read_data(file_name="enc_vector2.txt"))

    enc_vector1.link_context(context)
    enc_vector2.link_context(context)

    # Compute squared Euclidean distance between the encrypted vectors
    euclidean_squared = enc_vector1 - enc_vector2
    euclidean_squared = euclidean_squared.dot(euclidean_squared)

    # Serialize and save result
    write_data(file_name="euclidean_squared.txt", file_content=euclidean_squared.serialize())

    # Cleanup
    del context, enc_vector1, enc_vector2, euclidean_squared

    # Send the result back to the client (you can use a network communication method here)
    print("\nClient: Receiving result from server...")

    # Client side decryption and comparison
    print("Client: Decrypting and processing result...")

    # Load secret key context
    context = ts.context_from(read_data('secret.txt'))

    # Load encrypted result
    euclidean_squared = ts.lazy_ckks_vector_from(read_data(file_name="euclidean_squared.txt"))
    euclidean_squared.link_context(context)

    # Perform client-side computations (if needed)

    # Measure the time elapsed for decryption and processing
    start_time = time.time()

    # Decrypt and compute Euclidean distance
    euclidean_dist = math.sqrt(euclidean_squared.decrypt()[0])

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    # Output result
    if euclidean_dist < 10:
        print("Client: The images represent the same person.")
    else:
        print("Client: The images do not represent the same person.")

    # Display the elapsed time
    print(f"Client: Time elapsed for comparison: {elapsed_time:.5f} seconds.")

    print("===== End of Facial Recognition System =====")

if __name__ == "__main__":
    img1_path = "../downloads/alia3.jpg"
    img2_path = "../downloads/alia5.jpg"
    client_server_model(img1_path, img2_path)
