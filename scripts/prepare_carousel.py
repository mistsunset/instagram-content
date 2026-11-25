"""Prepare ordered JPEGs and build Windsor.ai carousel parameters."""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

RAW_ROOT = "https://raw.githubusercontent.com/mistsunset/instagram-content"
MAX_BYTES = 8_000_000
BATCH_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


def prepare(images, output, caption):
    if not 2 <= len(images) <= 10:
        raise ValueError("Provide 2 to 10 images in posting order.")
    if len(caption) > 2200:
        raise ValueError("Caption exceeds 2200 characters.")

    output.mkdir(parents=True, exist_ok=False)
    for number, source in enumerate(images, start=1):
        with Image.open(source) as opened:
            source_image = ImageOps.exif_transpose(opened).convert("RGBA")
            fitted = ImageOps.contain(source_image, (1080, 1350), Image.Resampling.LANCZOS)
            card = Image.new("RGB", (1080, 1350), "white")
            position = ((card.width - fitted.width) // 2, (card.height - fitted.height) // 2)
            card.paste(fitted, position, fitted.getchannel("A"))
            # Saving the new canvas omits source EXIF and other metadata.
            target = output / f"{number:02}.jpg"
            card.save(target, "JPEG", quality=92, optimize=True)
            if target.stat().st_size > MAX_BYTES:
                raise ValueError(f"{target.name} exceeds 8 MB.")

    (output / "caption.txt").write_text(caption, encoding="utf-8")


def payload(output, commit, batch_id):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Use a full GitHub commit SHA.")
    if not BATCH_ID.fullmatch(batch_id):
        raise ValueError("Use a lowercase batch ID with letters, numbers and hyphens.")
    cards = sorted(output.glob("*.jpg"))
    if not 2 <= len(cards) <= 10:
        raise ValueError("Expected 2 to 10 prepared JPEGs.")
    if [card.name for card in cards] != [f"{n:02}.jpg" for n in range(1, len(cards) + 1)]:
        raise ValueError("Prepared JPEGs must be numbered consecutively from 01.")
    caption = (output / "caption.txt").read_text(encoding="utf-8")
    if len(caption) > 2200:
        raise ValueError("Caption exceeds 2200 characters.")
    return {
        "image_urls": [
            f"{RAW_ROOT}/{commit}/media/{batch_id}/{card.name}" for card in cards
        ],
        "caption": caption,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    prepare_command = commands.add_parser("prepare")
    prepare_command.add_argument("--output", type=Path, required=True)
    prepare_command.add_argument("--caption-file", type=Path, required=True)
    prepare_command.add_argument("images", nargs="+", type=Path)

    payload_command = commands.add_parser("payload")
    payload_command.add_argument("--output", type=Path, required=True)
    payload_command.add_argument("--commit", required=True)
    payload_command.add_argument("--batch-id", required=True)

    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.images, args.output, args.caption_file.read_text(encoding="utf-8"))
    else:
        print(json.dumps(payload(args.output, args.commit, args.batch_id), ensure_ascii=False))


if __name__ == "__main__":
    main()
