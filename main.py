import sys
import os
from google import genai
from google.genai.errors import APIError
from PIL import Image
from dotenv import load_dotenv  # Import library dotenv
import inquirer
from pathlib import Path

# Muat variabel lingkungan dari file .env
load_dotenv()


class Keyworder:
    # --- Konfigurasi ---
    MODEL_NAME = "gemini-2.5-flash"

    api_key = os.getenv("GEMINI_API_KEY")

    SYSTEM_INSTRUCTION = (
        "You are an expert SEO image caption writer for a stock photo platform like Shutterstock. "
        "Your task is to analyze an image and generate a Title, Description, two Categories, and Tags "
        "in English. The output must be highly relevant, engaging, and optimized with keywords "
        "that are frequently searched on Google Trends or stock photo platforms. "
        "The output must follow this exact format:"
        "\n\n"
        "Title: [Your SEO Title Here]\n"
        "Description: [Your detailed, keyword-rich description here]\n"
        "Category 1: [First category, e.g., Abstract]\n"
        "Category 2: [Second category, e.g., Technology]\n"
        "Tags: tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10 (Do NOT use a list or bullet points for tags, and use lowercase.)"
    )

    def analyze_image_for_shutterstock(self, image_path):
        if not self.api_key:
            print("❌ Error: Variabel lingkungan 'GEMINI_API_KEY' tidak ditemukan.")
            print(
                "Pastikan Anda memiliki file .env di direktori ini dengan kunci API yang benar."
            )
            return

        try:
            client = genai.Client(api_key=self.api_key)

            img = Image.open(image_path)
            print(f"[PROGRESS] Image is loaded '{image_path}'. Send to Gemini server")

            response = client.models.generate_content(
                model=self.MODEL_NAME,
                contents=img,
                config=genai.types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION
                ),
            )

            print("\n" + "=" * 50)
            print("Result: ")
            if not response.text is None:
                print(response.text.strip())
                print("=" * 50)
                return

            print("failed get response server")

        except FileNotFoundError:
            print(f"[ERROR] image not found: {image_path}")
        except APIError as e:
            print(f"[ERROR] failed to connect Gemini API. Error: ({e})")
        except Exception as e:
            print(f"[ERROR] : {e}")


if __name__ == "__main__":

    stock = Path("../stock/")
    paths = list(stock.glob("*.eps"))
    paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    path_choices = [(f.name, str(f)) for f in paths][:5]

    question = [inquirer.List("path", message="Select filename", choices=path_choices)]

    selected = inquirer.prompt(question)

    if not selected is None:
        keyworder = Keyworder()
        keyworder.analyze_image_for_shutterstock(selected["path"])
