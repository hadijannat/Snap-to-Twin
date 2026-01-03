#!/usr/bin/env python3
"""
Snap-to-Twin AI Generator
--------------------------
Converts a photo of an industrial machine nameplate into an AAS-compliant JSON
configuration using GPT-4o Vision.

Usage:
    python generate.py <image_path> [--output twin_config.json]

Example:
    python generate.py motor_nameplate.jpg
    python generate.py examples/pump.png --output pump_config.json

Requirements:
    pip install openai

Environment:
    Set OPENAI_API_KEY environment variable or edit this file
"""

import base64
import json
import os
import sys
import argparse
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: OpenAI library not installed")
    print("Install it with: pip install openai")
    sys.exit(1)


def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_extension(image_path: str) -> str:
    """Get the MIME type for the image."""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')


def image_to_aas(image_path: str, api_key: str = None, output_path: str = "twin_config.json") -> dict:
    """
    Extract technical specifications from a machine nameplate photo
    and generate AAS-compliant JSON.

    Args:
        image_path: Path to the nameplate image
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        output_path: Where to save the generated JSON

    Returns:
        The generated AAS dictionary
    """

    # Initialize OpenAI client
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ Error: OpenAI API key not found")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("Or pass it as --api-key argument")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Validate image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        sys.exit(1)

    print(f"📸 Scanning {image_path}...")

    # Encode image
    b64_img = encode_image(image_path)
    mime_type = get_image_extension(image_path)

    # The "Expert" Prompt: Enforces AAS schema compliance
    prompt = """
You are an expert in industrial equipment and the Asset Administration Shell (AAS) standard.

Analyze this industrial nameplate or equipment photo. Extract ALL visible technical specifications into this EXACT JSON structure:

{
  "id": "SERIAL_NUMBER_OR_MODEL_CODE",
  "asset_type": "MANUFACTURER MODEL_NAME",
  "nameplate": [
     {"id_short": "Manufacturer", "value": "Company Name", "unit": null},
     {"id_short": "ModelNumber", "value": "...", "unit": null},
     {"id_short": "SerialNumber", "value": "...", "unit": null},
     {"id_short": "Voltage", "value": "...", "unit": "V"},
     {"id_short": "Current", "value": "...", "unit": "A"},
     {"id_short": "Power", "value": "...", "unit": "kW"},
     {"id_short": "Frequency", "value": "...", "unit": "Hz"},
     {"id_short": "RPM", "value": "...", "unit": "1/min"},
     {"id_short": "PowerFactor", "value": "...", "unit": null},
     {"id_short": "IPRating", "value": "...", "unit": null},
     {"id_short": "YearOfManufacture", "value": "...", "unit": null}
  ]
}

IMPORTANT RULES:
1. Return ONLY valid JSON - no markdown, no explanations, no code blocks
2. Include only properties that are VISIBLE on the nameplate
3. Use standard AAS property names (id_short values)
4. For the "id" field, use the serial number if visible, otherwise use model number
5. For "asset_type", combine manufacturer and model (e.g., "Siemens 1LE1001")
6. If a value is not visible, omit that property entirely (don't include null values)
7. Common units: V (volts), A (amperes), kW or HP (power), Hz (frequency), 1/min (RPM)
8. Preserve exact values as written (don't convert units)

Extract the data now:
"""

    try:
        # Call GPT-4o Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime_type};base64,{b64_img}",
                        "detail": "high"
                    }}
                ]}
            ],
            max_tokens=1000
        )

        # Extract JSON from response
        json_str = response.choices[0].message.content.strip()

        # Clean up any markdown artifacts
        json_str = json_str.replace("```json", "").replace("```", "").strip()

        # Parse to validate
        aas_data = json.loads(json_str)

        # Save to file
        with open(output_path, "w") as f:
            json.dump(aas_data, f, indent=2)

        print(f"✅ AAS configuration generated successfully!")
        print(f"📄 Saved to: {output_path}")
        print(f"\n📊 Extracted {len(aas_data.get('nameplate', []))} properties:")

        for prop in aas_data.get('nameplate', []):
            unit = f" {prop['unit']}" if prop.get('unit') else ""
            print(f"   • {prop['id_short']}: {prop['value']}{unit}")

        return aas_data

    except json.JSONDecodeError as e:
        print(f"❌ Error: AI returned invalid JSON")
        print(f"Raw response: {json_str}")
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert machine nameplate photos to AAS JSON using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py motor.jpg
  python generate.py nameplate.png --output my_twin.json
  python generate.py pump.jpg --api-key sk-...
        """
    )

    parser.add_argument("image", help="Path to the nameplate image")
    parser.add_argument("--output", "-o", default="twin_config.json",
                       help="Output JSON file path (default: twin_config.json)")
    parser.add_argument("--api-key", "-k", help="OpenAI API key (or set OPENAI_API_KEY env var)")

    args = parser.parse_args()

    image_to_aas(args.image, api_key=args.api_key, output_path=args.output)


if __name__ == "__main__":
    main()
