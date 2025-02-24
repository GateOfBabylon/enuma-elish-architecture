import random

def main():
    possible_statuses = ["ready", "pending", "error"]
    status = random.choice(possible_statuses)

    print("Doing some important job!")
    print(f"export status={status}")

if __name__ == "__main__":
    main()
