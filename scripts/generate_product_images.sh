#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LOCAL_ENV="$PROJECT_DIR/.env.local"
IMAGEGEN_CLI=${KORIKATHA_IMAGEGEN_CLI:-/Users/subhojitdas/.codex/skills/.system/imagegen/scripts/image_gen.py}
OUTPUT_DIR="$PROJECT_DIR/output/imagegen/products"
PRODUCT_DIR="$PROJECT_DIR/assets/products"

if [ -f "$LOCAL_ENV" ]; then
  set -a
  . "$LOCAL_ENV"
  set +a
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is missing. Add it to .env.local and run again." >&2
  exit 1
fi

if [ ! -f "$IMAGEGEN_CLI" ]; then
  echo "Image generation CLI not found: $IMAGEGEN_CLI" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR" "$PRODUCT_DIR"

for MANIFEST in prompts-sarees.jsonl prompts-jewellery.jsonl; do
  python3 "$IMAGEGEN_CLI" generate-batch \
    --input "$PROJECT_DIR/data/$MANIFEST" \
    --out-dir "$OUTPUT_DIR" \
    --model gpt-image-2 \
    --quality low \
    --size 1024x1024 \
    --output-format webp \
    --output-compression 82 \
    --downscale-max-dim 720 \
    --downscale-suffix=-web \
    --concurrency 5
done

find "$OUTPUT_DIR" -type f -name '*-web.webp' -exec cp {} "$PRODUCT_DIR" \;
echo "Product images copied to $PRODUCT_DIR"
