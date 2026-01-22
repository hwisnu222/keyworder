import sys
import os
from google import genai
from google.genai.errors import APIError
from PIL import Image
from dotenv import load_dotenv
import inquirer
from pathlib import Path
from tqdm import tqdm
from exiftool import ExifToolHelper
import json

load_dotenv()


class Keyworder:
    api_key = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"
    SYSTEM_INSTRUCTION = (
        "You are an expert SEO image caption writer for a stock photo platform like Shutterstock. "
        "Your task is to analyze an image and generate a Title, Description, two Categories, and Tags "
        "in English. The output must be highly relevant, engaging, and optimized with keywords "
        "that are frequently searched on Google Trends or stock photo platforms. "
        """
        Available categories:
        - abstract
        - animals/Wildlife
        - arts
        - backgrounds/Textures
        - beauty/Fashion
        - buildings/Landmarks
        - business/Finance
        - celebrities
        - education
        - food and drink
        - healthcare/Medical
        - holidays
        - industrial
        - interiors
        - miscellaneous
        - nature
        - objects
        - parks/Outdoor
        - people
        - religion
        - science
        - signs/Symbols
        - sports/Recreation
        - technology
        - transportation
        - vintage
        """
        "The output must follow this exact format:"
        "\n\n"
        "Title: Your SEO Title Here\n"
        "Description: Your detailed, keyword-rich description here\n"
        "Categories: category with lower case\n"
        "OUTPUT FORMAT (MUST BE VALID JSON) dont add any character invalid json:\n"
        "{\n"
        '  "title": "string",\n'
        '  "description": "string",\n'
        '  "categories": ["string", "string"],\n'
        '  "keywords": ["string", "string", "string"]\n'
        "}"
    )

    def add_metadata_to_eps(self, file_path, title, description, keywords, categories):
        try:
            with ExifToolHelper() as et:
                et.set_tags(
                    [file_path],
                    tags={
                        "Headline": title,
                        "Description": description,
                        "Caption-Abstract": description,
                        "Keywords": keywords,
                        "Categories": categories,
                        "XMP:Title": title,
                        "XMP:Description": description,
                        "XMP:Subject": keywords,
                    },
                    params=["-overwrite_original"],  # disable file backup .eps_original
                )
            print(f"[SUCCESS] add metadata to: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"[ERROR] {file_path} file: {e}")

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
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    response_mime_type="application/json",
                ),
            )

            print(response.text)

            tqdm.write("\n" + "=" * 50)
            if not response.text is None:
                metadata = json.loads(response.text)

                self.add_metadata_to_eps(
                    image_path,
                    title=metadata.get("title"),
                    description=metadata.get("description"),
                    keywords=metadata.get("keywords"),
                    categories=metadata.get("categories"),
                )
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
