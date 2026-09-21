import wave


def hide_message(audio_path, secret_message, output_path):
    audio = wave.open(audio_path, "rb")

    frames = bytearray(audio.readframes(audio.getnframes()))
    audio.close()

    binary_message = ''.join(
        format(ord(char), '08b')
        for char in secret_message + "~"
    )

    if len(binary_message) > len(frames):
        return False

    for i in range(len(binary_message)):
        frames[i] = (frames[i] & 254) | int(binary_message[i])

    output = wave.open(output_path, "wb")
    output.setparams(
        wave.open(audio_path, "rb").getparams()
    )
    output.writeframes(frames)
    output.close()

    return True


def extract_message(audio_path):
    audio = wave.open(audio_path, "rb")
    frames = bytearray(audio.readframes(audio.getnframes()))
    audio.close()

    binary_data = ""

    for byte in frames:
        binary_data += str(byte & 1)

    message = ""

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]

        if len(byte) < 8:
            break

        character = chr(int(byte, 2))

        if character == "~":
            return message

        if ord(character) < 32 or ord(character) > 126:
            return "No hidden message found"

        message += character

    return "No hidden message found"