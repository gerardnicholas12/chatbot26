from agents.router import route_query

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    response = route_query(user_input)

    print("\nBot:", response)
    print()
    