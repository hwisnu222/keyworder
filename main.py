import sys
import os
from google import genai
from google.genai.errors import APIError
from PIL import Image
from dotenv import load_dotenv
import inquirer
from pathlib import Path
from tqdm import tqdm

load_dotenv()


class Keyworder:
    api_key = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"
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
            tqdm.write("[ERROR] 'GEMINI_API_KEY' not found")
            return

        try:
            client = genai.Client(api_key=self.api_key)

            img = Image.open(image_path)
            tqdm.write(
                f"[PROGRESS] Image is loaded: '{image_path}'. Send to Gemini server"
            )

            response = client.models.generate_content(
                model=self.MODEL_NAME,
                contents=img,
                config=genai.types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION
                ),
            )

            tqdm.write("\n" + "=" * 50)
            if not response.text is None:
                tqdm.write(response.text.strip())
                tqdm.write("=" * 50)
                return

            tqdm.write("[ERROR] failed get response server")

        except FileNotFoundError:
            tqdm.write(f"[ERROR] image not found: {image_path}")
        except APIError as e:
            tqdm.write(f"[ERROR] failed to connect Gemini API. Error: ({e})")
        except Exception as e:
            tqdm.write(f"[ERROR] : {e}")


if __name__ == "__main__":

    stock = Path("./stock/")
    paths = list(stock.glob("*.eps"))

    if not len(paths) > 0:
        print("[ERROR] please add file *.eps in stock folder")
        os.makedirs("stock", exist_ok=True)
        sys.exit(1)

    paths.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    path_choices = [(f.name, str(f)) for f in paths][:5]

    question = [
        inquirer.Checkbox("paths", message="Select filename", choices=path_choices)
    ]

    selected = inquirer.prompt(question)

    if not selected is None:
        if len(selected["paths"]) < 1:
            print("please select option")
            sys.exit(1)

        selected_paths = selected["paths"]
        for path in tqdm(selected_paths):
            keyworder = Keyworder()
            keyworder.analyze_image_for_shutterstock(path)
