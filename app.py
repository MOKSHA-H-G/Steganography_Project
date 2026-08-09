from flask import Flask, render_template, request, send_file
from PIL import Image
import os

app = Flask(__name__)

# Folder for uploaded and encoded images
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)


def hide_message(image_path, secret_message, output_path):
    img = Image.open(image_path).convert("RGB")

    binary_message = message_to_binary(secret_message + "~")

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

    if data_index < len(binary_message):
        return False

    img.putdata(data)
    img.save(output_path)

    return True


def extract_message(image_path):
    img = Image.open(image_path).convert("RGB")

    data = list(img.getdata())
    binary_data = ""

    for pixel in data:
        for value in pixel:
            binary_data += str(value & 1)

    message = ""

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]

        if len(byte) < 8:
            break

        character = chr(int(byte, 2))

        if character == "~":
            return message

        # Stop if we encounter invalid/non-readable data
        if ord(character) < 32 or ord(character) > 126:
            return "No hidden message found"

        message += character

    return "No hidden message found"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/hide", methods=["POST"])
def hide():
    image = request.files.get("image")
    message = request.form.get("message", "").strip()

    if not image or not message:
        return "Please select an image and enter a message."

    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    output_path = os.path.join(UPLOAD_FOLDER, "encoded_image.png")

    image.save(input_path)

    success = hide_message(input_path, message, output_path)

    if not success:
        return "Message is too large for this image."

    return send_file(
        output_path,
        as_attachment=True,
        download_name="encoded_image.png"
    )


@app.route("/extract", methods=["POST"])
def extract():
    image = request.files.get("encoded_image")

    if not image:
        return "Please select an encoded image."

    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(input_path)

    message = extract_message(input_path)

    return f"""
    <html>
    <head>
        <title>Hidden Message</title>
        <style>
            body {{
                font-family: Arial;
                background: #f5f0ff;
                text-align: center;
                padding-top: 100px;
            }}

            .box {{
                background: white;
                padding: 30px;
                margin: auto;
                width: 60%;
                border-radius: 12px;
                box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            }}

            h1 {{
                color: #6c4ab6;
            }}
        </style>
    </head>

    <body>
        <div class="box">
            <h1>🔓 Hidden Message</h1>
            <p>{message}</p>
            <br>
            <a href="/">← Back to Website</a>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)