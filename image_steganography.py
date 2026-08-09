from PIL import Image

# Convert message to binary
def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)


# Hide Message
def hide_message(image_path, secret_message):
    img = Image.open(image_path)
    img = img.convert("RGB")

    # Add end marker
    secret_message += "#####"

    binary_message = message_to_binary(secret_message)

    data = list(img.getdata())
    data_index = 0

    for i in range(len(data)):
        pixel = list(data[i])

        for j in range(3):
            if data_index < len(binary_message):
                pixel[j] = (pixel[j] & ~1) | int(binary_message[data_index])
                data_index += 1

        data[i] = tuple(pixel)

        if data_index >= len(binary_message):
            break

    img.putdata(data)
    img.save("encoded_image.png")

    print("\nMessage hidden successfully!")
    print("Saved as encoded_image.png")


# Extract Message
def extract_message(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")

    data = list(img.getdata())

    binary_data = ""

    for pixel in data:
        for value in pixel:
            binary_data += str(value & 1)

    message = ""

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]

        if len(byte) < 8:
            break

        character = chr(int(byte, 2))
        message += character

        if message.endswith("#####"):
            message = message[:-5]
            break

    print("\nHidden Message:", message)


# Main Menu
while True:
    print("\n====== IMAGE STEGANOGRAPHY ======")
    print("1. Hide Message")
    print("2. Extract Message")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        image_path = input("Enter image path: ")
        secret_message = input("Enter secret message: ")
        hide_message(image_path, secret_message)

    elif choice == "2":
        image_path = input("Enter encoded image path: ")
        extract_message(image_path)

    elif choice == "3":
        print("Thank you!")
        break

    else:
        print("Invalid choice! Please try again.")