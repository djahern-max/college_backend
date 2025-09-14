from PIL import Image
import sys

def optimize_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            target_width, target_height = 400, 225
            width, height = img.size
            current_ratio = width / height
            target_ratio = target_width / target_height
            
            if abs(current_ratio - target_ratio) > 0.1:
                if current_ratio > target_ratio:
                    new_width = int(height * target_ratio)
                    left = (width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, height))
                else:
                    new_height = int(width / target_ratio)
                    top = int((height - new_height) * 0.3)
                    img = img.crop((0, top, width, top + new_height))
            
            img = img.resize((target_width, target_height), Image.LANCZOS)
            img.save(output_path, "JPEG", quality=90, optimize=True)
            
            print(f"Optimized: {input_path} -> {output_path}")
            print(f"Final size: {target_width}x{target_height}px")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python simple_optimize.py input_image.jpg output_image.jpg")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    optimize_image(input_file, output_file)
