# scripts/generate_fallback_images.py
"""
Script to generate and upload attractive fallback images for scholarships
"""

import os
import sys
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.image_extractor import DigitalOceanSpacesUploader


class FallbackImageGenerator:
    def __init__(self):
        self.uploader = DigitalOceanSpacesUploader()
        self.width = 400
        self.height = 300

    def create_category_image(
        self, category: str, title: str, color: tuple, icon_text: str
    ):
        """Create a professional-looking fallback image for a scholarship category"""

        # Create base image with gradient
        img = Image.new("RGB", (self.width, self.height), color)
        draw = ImageDraw.Draw(img)

        # Create gradient effect
        for y in range(self.height):
            alpha = int(255 * (1 - y / self.height * 0.3))
            gradient_color = tuple(min(255, c + alpha // 10) for c in color)
            draw.line([(0, y), (self.width, y)], fill=gradient_color)

        # Add overlay pattern
        overlay = Image.new("RGBA", (self.width, self.height), (255, 255, 255, 20))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        try:
            # Try different font paths for different systems
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/System/Library/Fonts/Arial.ttf",  # macOS backup
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "/Windows/Fonts/arial.ttf",  # Windows
                "arial.ttf",  # Generic
            ]

            font_large = None
            font_small = None

            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font_large = ImageFont.truetype(font_path, 48)
                        font_small = ImageFont.truetype(font_path, 24)
                        break
                except:
                    continue

            if not font_large:
                # Fallback to default
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
                print("⚠️  Using default font - text may look basic")

        except Exception as e:
            # Fallback to default
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            print(f"⚠️  Font loading failed ({e}), using default")

        # Add icon/symbol (convert emoji to text for compatibility)
        icon_text_safe = {
            "🔬": "STEM",
            "🎨": "ARTS",
            "🏆": "SPORTS",
            "🌈": "DIVERSITY",
            "💰": "$$$",
            "🎓": "GRAD",
        }.get(icon_text, "AWARD")

        draw.text(
            (self.width // 2, 80),
            icon_text_safe,
            fill="white",
            font=font_large,
            anchor="mm",
        )

        # Add title
        draw.text(
            (self.width // 2, 180), title, fill="white", font=font_small, anchor="mm"
        )

        # Add "Scholarship" text
        draw.text(
            (self.width // 2, 220),
            "SCHOLARSHIP",
            fill="white",
            font=font_small,
            anchor="mm",
        )

        return img

    def generate_all_fallbacks(self):
        """Generate all category fallback images"""

        categories = {
            "stem_scholarship.jpg": {
                "title": "STEM Excellence",
                "color": (70, 130, 180),  # Steel blue
                "icon": "🔬",
            },
            "arts_scholarship.jpg": {
                "title": "Arts & Creativity",
                "color": (139, 69, 19),  # Saddle brown
                "icon": "🎨",
            },
            "athletic_scholarship.jpg": {
                "title": "Athletic Achievement",
                "color": (34, 139, 34),  # Forest green
                "icon": "🏆",
            },
            "diversity_scholarship.jpg": {
                "title": "Diversity & Inclusion",
                "color": (148, 0, 211),  # Dark violet
                "icon": "🌈",
            },
            "need_based_scholarship.jpg": {
                "title": "Financial Need",
                "color": (220, 20, 60),  # Crimson
                "icon": "💰",
            },
            "general_scholarship.jpg": {
                "title": "Academic Excellence",
                "color": (25, 25, 112),  # Midnight blue
                "icon": "🎓",
            },
        }

        print("🎨 Starting fallback image generation...")
        success_count = 0

        for filename, config in categories.items():
            print(f"📷 Generating {filename}...")

            try:
                img = self.create_category_image(
                    category=filename,
                    title=config["title"],
                    color=config["color"],
                    icon_text=config["icon"],
                )

                # Save to BytesIO
                img_bytes = BytesIO()
                img.save(img_bytes, format="JPEG", quality=90)
                img_bytes.seek(0)

                # Upload to Spaces
                file_path = f"fallbacks/{filename}"
                cdn_url = self.uploader.upload_image(
                    image_bytes=img_bytes.getvalue(),
                    file_path=file_path,
                    content_type="image/jpeg",
                )

                if cdn_url:
                    print(f"✅ Uploaded {filename}: {cdn_url}")
                    success_count += 1
                else:
                    print(f"❌ Failed to upload {filename}")

            except Exception as e:
                print(f"❌ Error generating {filename}: {e}")

        print(
            f"\n🎉 Generation complete! {success_count}/{len(categories)} images uploaded successfully."
        )


def main():
    """Run the fallback image generation"""
    print("🚀 MagicScholar Fallback Image Generator")
    print("=" * 50)

    try:
        generator = FallbackImageGenerator()
        generator.generate_all_fallbacks()

        print(
            "\n✨ All done! Your scholarship cards should now have beautiful fallback images."
        )
        print("💡 Next step: Update your frontend to use the new image URLs.")

    except Exception as e:
        print(f"❌ Critical error: {e}")
        print(
            "💡 Make sure your environment variables are set for Digital Ocean Spaces"
        )
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
