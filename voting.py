import random
import os
import tenseal as ts

# Setup TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40

def client_voting(total_voters):
    # Get the number of candidates and their names
    num_candidates = int(input("Enter the number of candidates: "))
    candidates = [input(f"Enter name for candidate {i+1}: ") for i in range(num_candidates)]

    # Initialize encrypted votes for each candidate
    encrypted_votes = {candidate: [ts.ckks_vector(context, [0])] * total_voters for candidate in candidates}

    for voter_index in range(total_voters):
        # Print the list of candidates
        print("Vote for:")
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate}")

        # Take vote as input
        vote = int(input("Enter your vote (1-{}): ".format(num_candidates)))

        # Validate the vote
        if 1 <= vote <= num_candidates:
            # Encrypt the vote
            for i, candidate in enumerate(candidates):
                if i == vote - 1:
                    encrypted_votes[candidate][voter_index] = ts.ckks_vector(context, [1])  # Vote for the selected candidate
                else:
                    encrypted_votes[candidate][voter_index] = ts.ckks_vector(context, [0])  # Vote for other candidates as 0

            # Clear the terminal
            os.system('cls' if os.name == 'nt' else 'clear')
        else:
            print("Invalid vote. Please enter a number between 1 and {}.".format(num_candidates))

    # Print the list of votes after all voters have voted
    print("Voting process completed.")

    return encrypted_votes, candidates


def server_count_votes(encrypted_votes, candidates):
    if not encrypted_votes:
        print("No votes received. Exiting...")
        return {}

    # Decrypt the encrypted votes and count the votes for each candidate
    candidate_counts = {candidate: ts.ckks_vector(context, [0]) for candidate in candidates}

    for candidate, votes in encrypted_votes.items():
        candidate_sum = ts.ckks_vector(context, [0])  # Initialize the sum with encrypted value of zero
        for vote in votes:
            candidate_sum += vote  # Homomorphic addition
        # Update candidate_counts with the encrypted sum
        candidate_counts[candidate] = candidate_sum

    # Round the decrypted count for each candidate
    for candidate, count in candidate_counts.items():
        candidate_counts[candidate] = [round(value) for value in count.decrypt()]

    return candidate_counts


def client_display_results(encrypted_counts, candidates):
    # Decrypt the counts and round to the nearest integer
    decrypted_counts = {candidate: [round(value) for value in count] for candidate, count in encrypted_counts.items()}

    # Display the decrypted counts
    print("\nClient: Decrypted counts:")
    for candidate, count in decrypted_counts.items():
        print(f"{candidate}: {count} votes")

    # Find the winner index
    winner_index = max(decrypted_counts, key=lambda k: sum(decrypted_counts[k]))
    winner_votes = sum(decrypted_counts[winner_index])
    print(f"\nClient: Announcing the winner...")
    print(f"The winner is {winner_index} with {winner_votes} votes.")

if __name__ == "__main__":
    print("===== Voting System Using Homomorphic Encryption =====")

    # Client side: Voting
    print("\nClient: Initiating voting process...")

    # Get the total number of voters
    total_voters = int(input("Enter the total number of voters: "))
    print(f"\nClient: Total number of voters: {total_voters}\n")
    
    encrypted_votes, candidates = client_voting(total_voters)

    # Server side: Counting votes
    print("\nServer: Counting votes and determining the winner...")
    encrypted_counts = server_count_votes(encrypted_votes, candidates)

    # Client side: Displaying results
    print("\nClient: Displaying final results...")
    client_display_results(encrypted_counts, candidates)

    print("===== End of Voting System =====")
