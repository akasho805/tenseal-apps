import tenseal as ts
import os

# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40

candidates = ["Candidate1", "Candidate2", "Candidate3", "Candidate4", "Candidate5"]

def client_voting():
    global candidates  # Access the global candidates list
    votes = []

    # Get the total number of voters
    total_voters = int(input("Enter the total number of voters: "))
    print(f"\nClient: Total number of voters: {total_voters}\n")

    for _ in range(total_voters):
        # Print the list of candidates without revealing names
        print("Vote for:\n1. Candidate1 2. Candidate2 3. Candidate3 4. Candidate4 5. Candidate5")

        # Take vote as input
        vote = int(input("Enter your vote (1-5): "))

        # Validate the vote
        if 1 <= vote <= 5:
            # Encrypt the vote
            encrypted_vote = ts.ckks_vector(context, [vote])
            print("Vote encrypted:", encrypted_vote)

            # Wait for any key to proceed to the next voter
            input("Press Enter to proceed to the next voter...")

            # Clear the terminal
            os.system('cls' if os.name == 'nt' else 'clear')

            # Add the vote to the list
            votes.append(encrypted_vote)
        else:
            print("Invalid vote. Please enter a number between 1 and 5.")

    # Print the list of votes after all voters have voted
    print("Voting process completed. List of votes:", votes)

    # debug
    # decrypted_votes = [round(element.decrypt()[0]) for element in votes]
    # print("Decrypted and Rounded List of Votes:", decrypted_votes)

    return votes

def server_count_votes(encrypted_votes):
    global candidates  # Access the global candidates list
    # Define a threshold for comparison
    threshold = 1.0

    # Count occurrences using homomorphic comparison
    occurrences = {}
    visited = set()

    for i in range(len(encrypted_votes)):
        if i not in visited:
            
            occurrences[i] = 1  # Initialize occurrence count for the current index
            visited.add(i)  # Mark the current index as visited

            for j in range(i + 1, len(encrypted_votes)):
                if j not in visited:
                    # Homomorphic comparison
                    diff = encrypted_votes[i] - encrypted_votes[j]
                    comparison_result = (diff.square().sum().decrypt()[0]) < threshold

                    # Check if the numbers are equal
                    if comparison_result:
                        # Increment occurrence count
                        occurrences[i] += 1
                        visited.add(j)  # Mark the other index as visited

    # Display the encrypted vote count for each candidate
    print(f"\nServer: Total number of voters: {len(encrypted_votes)}")
    print(f"\nVote count for each candidate:")
    for idx, count in occurrences.items():
        print(f"Candidate{idx + 1}: {count} votes")

    # Encrypt the vote count for each candidate
    encrypted_counts = [ts.ckks_vector(context, [count]) for count in occurrences.values()]

    # Display the winning candidate
    print(f"\nServer: Sending encrypted counts to client...")
    return encrypted_counts

def client_display_results(encrypted_counts):
    # Display results
    print("\nClient: Receiving encrypted counts from server...")
    print("Encrypted Counts received:", encrypted_counts)

    # Decrypt the counts and round to the nearest integer
    decrypted_counts = [round(count.decrypt()[0]) for count in encrypted_counts]

    # Display the decrypted counts
    print("\nClient: Decrypted counts:")
    for idx, count in enumerate(decrypted_counts):
        print(f"Candidate{idx + 1}: {count} votes")

    # Find the winner index
    winner_index = decrypted_counts.index(max(decrypted_counts))
    print(f"\nClient: Announcing the winner...")
    print(f"The winner is Candidate{winner_index + 1} with {decrypted_counts[winner_index]} votes.")

if __name__ == "__main__":
    print("===== Voting System Using Homomorphic Encryption =====")

    # Client side: Voting
    print("\nClient: Initiating voting process...")
    encrypted_votes = client_voting()

    # Server side: Counting votes
    print("\nServer: Counting votes and determining the winner...")
    encrypted_counts = server_count_votes(encrypted_votes)

    # # Client side: Displaying results
    # print("\nClient: Displaying final results...")
    # client_display_results(encrypted_counts)

    # print("===== End of Voting System =====")
