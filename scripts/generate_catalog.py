#!/usr/bin/env python3
"""Generate the initial 10-product KoriKatha catalogue and import files."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SUPABASE_DIR = ROOT / "supabase"
PROMPT_DIR = DATA_DIR
SEED = 260819


SAREE_TYPES = [
    ("Jamdani", "fine handwoven cotton with airy supplementary motifs", 3890, 8490),
    ("Baluchari", "silk weave with narrative pallav detailing", 7490, 15900),
    ("Bengal Tant", "crisp breathable cotton with a light everyday drape", 1490, 3990),
    ("Garad", "ivory silk with a traditional Bengali border", 5990, 12900),
    ("Korial", "refined ivory weave with a ceremonial red border", 6490, 13900),
    ("Dhakai", "lightweight heritage weave with intricate all-over work", 4290, 9990),
    ("Murshidabad Silk", "fluid Bengal silk with a soft natural sheen", 4490, 10900),
    ("Begumpuri", "textured cotton with bold borders and a relaxed drape", 1890, 4490),
    ("Kantha", "hand-embroidered textile inspired by Bengal's running stitch", 5490, 14900),
    ("Bengal Tussar", "textured wild silk in an earthy artisanal finish", 5790, 13900),
]

SAREE_COLOURS = [
    ("Vermilion", "deep vermilion red"),
    ("Shiuli Ivory", "warm shiuli-flower ivory"),
    ("Monsoon Indigo", "deep monsoon indigo"),
    ("Turmeric Gold", "muted turmeric gold"),
    ("Aparajita Blue", "rich aparajita blue"),
    ("Terracotta", "earthy Bengal terracotta"),
    ("Lotus Pink", "soft lotus pink"),
    ("Jamun", "dark jamun purple"),
    ("Kadam Green", "muted kadam-leaf green"),
    ("Charcoal", "smoky charcoal black"),
]

SAREE_MOTIFS = [
    ("Lotus Buti", "small lotus buti motifs"),
    ("Shankha Border", "conch-shell inspired border geometry"),
    ("Alpana Vine", "flowing alpana vine motifs"),
    ("Fish & River", "abstract fish and river motifs"),
    ("Temple Rekha", "traditional temple-line border details"),
]

JEWELLERY_TYPES = [
    ("Dokra Pendant", "lost-wax folk-metal pendant", 1290, 5990),
    ("Filigree Jhumka", "delicate wirework drop earrings", 990, 4490),
    ("Terracotta Necklace", "hand-shaped clay statement necklace", 690, 2790),
    ("Kori Choker", "cowrie-inspired sculptural choker", 1490, 6490),
    ("Bengal Bangle Set", "textured handcrafted bangle pair", 1090, 4990),
    ("Hansuli Necklace", "crescent-shaped folk necklace", 1990, 7990),
    ("Naksha Earrings", "ornamental Bengali motif earrings", 790, 3890),
    ("Temple Hairpin", "decorative heritage hair ornament", 590, 2490),
    ("Shankha Brooch", "conch-inspired artisanal brooch", 690, 2990),
    ("Gramin Long Haar", "long rural Bengal-inspired statement necklace", 2290, 8990),
]

JEWELLERY_FINISHES = [
    ("Antique Gold", "warm antique-gold finish"),
    ("Burnished Brass", "deep burnished brass finish"),
    ("Oxidised Silver", "matte oxidised-silver finish"),
    ("Terracotta Red", "hand-painted terracotta red accents"),
    ("Indigo Enamel", "subtle indigo enamel accents"),
    ("Ivory Patina", "soft ivory patina details"),
    ("Copper Glow", "warm hand-burnished copper finish"),
    ("Charcoal Gold", "charcoal-black and antique-gold finish"),
    ("Vermilion Lac", "vermilion lac accents with folk-metal details"),
    ("Forest Green", "muted forest-green enamel accents"),
]

JEWELLERY_MOTIFS = [
    ("Lotus", "lotus petals"),
    ("Owl", "stylised Bengal owl"),
    ("Fish", "paired fish"),
    ("Alpana", "alpana curves"),
    ("Paddy", "rice-grain and paddy forms"),
]


def round_price(value: int) -> int:
    return max(490, int(round(value / 100.0) * 100 - 10))


def stock_for(index: int, rng: random.Random) -> int:
    if index % 19 == 0:
        return 0
    if index % 11 == 0:
        return rng.randint(1, 4)
    return rng.randint(5, 32)


def make_sarees(rng: random.Random) -> list[dict]:
    products = []
    index = 0
    for saree_type, type_desc, low, high in SAREE_TYPES:
        for colour_name, colour_desc in SAREE_COLOURS:
            for motif_name, motif_desc in SAREE_MOTIFS:
                index += 1
                sku = f"SAR-{index:04d}"
                price = round_price(rng.randint(low, high))
                quantity = stock_for(index, rng)
                products.append(
                    {
                        "sku": sku,
                        "name": f"{colour_name} {saree_type} — {motif_name}",
                        "category": "saree",
                        "subcategory": saree_type,
                        "description": f"A {type_desc}, finished in {colour_desc} with {motif_desc}. Curated as a contemporary expression of Bengal's textile heritage.",
                        "price": price,
                        "compare_at_price": round_price(int(price * rng.choice([1.15, 1.2, 1.25]))),
                        "quantity": quantity,
                        "reorder_level": 5,
                        "colour": colour_name,
                        "motif": motif_name,
                        "material": type_desc.split(" with ")[0],
                        "image": f"assets/products/{sku.lower()}-web.webp",
                        "featured": index % 37 == 0,
                        "active": True,
                    }
                )
    return products


def make_jewellery(rng: random.Random) -> list[dict]:
    products = []
    index = 0
    for item_type, type_desc, low, high in JEWELLERY_TYPES:
        for finish_name, finish_desc in JEWELLERY_FINISHES:
            for motif_name, motif_desc in JEWELLERY_MOTIFS:
                index += 1
                sku = f"JWL-{index:04d}"
                price = round_price(rng.randint(low, high))
                quantity = stock_for(index + 500, rng)
                products.append(
                    {
                        "sku": sku,
                        "name": f"{finish_name} {item_type} — {motif_name}",
                        "category": "jewellery",
                        "subcategory": item_type,
                        "description": f"A {type_desc} with a {finish_desc}, shaped around {motif_desc}. Inspired by rural Bengal and made for expressive modern styling.",
                        "price": price,
                        "compare_at_price": round_price(int(price * rng.choice([1.15, 1.2, 1.25]))),
                        "quantity": quantity,
                        "reorder_level": 5,
                        "colour": finish_name,
                        "motif": motif_name,
                        "material": finish_desc,
                        "image": f"assets/products/{sku.lower()}-web.webp",
                        "featured": index % 41 == 0,
                        "active": True,
                    }
                )
    return products


def make_curated_catalogue() -> list[dict]:
    """The initial collection: five sarees and five jewellery pieces."""
    rows = [
        ("SAR-0001", "Indigo Bishnupur Baluchari", "saree", "Baluchari", "An indigo Baluchari-inspired silk with narrative woven panels and an ornate heritage border.", 8490, 9990, 8, "Indigo", "Narrative panels", "Silk"),
        ("SAR-0002", "Royal Blue Baluchari Story Weave", "saree", "Baluchari", "A royal-blue Bengal story weave featuring detailed figurative panels across the pallav.", 7990, 9490, 5, "Royal Blue", "Figurative pallav", "Silk"),
        ("SAR-0003", "Midnight Baluchari Heritage", "saree", "Baluchari", "A dramatic midnight weave with turquoise and crimson narrative detailing.", 7490, 8990, 3, "Midnight", "Heritage figures", "Silk"),
        ("SAR-0004", "Shiuli Jamdani Edit", "saree", "Jamdani", "A light Jamdani-inspired edit in soft ivory, rose and turmeric tones for effortless draping.", 4290, 5290, 12, "Shiuli Ivory", "Fine linear weave", "Cotton"),
        ("SAR-0005", "Turmeric Bengal Tant", "saree", "Bengal Tant", "A warm turmeric and terracotta Bengal Tant-inspired saree with a crisp everyday character.", 2190, 2790, 9, "Turmeric", "Contrast border", "Cotton"),
        ("JWL-0001", "Maharani Filigree Jhumka", "jewellery", "Jhumka", "An ornate gold-toned Bengal jhumka pair with airy filigree domes and traditional drops.", 1890, 2390, 7, "Antique Gold", "Filigree dome", "Gold-toned alloy"),
        ("JWL-0002", "Ranga Stone Jhumka", "jewellery", "Jhumka", "A compact gold-toned jhumka pair accented with red stones and floral tops.", 1290, 1690, 14, "Gold & Red", "Floral jhumka", "Gold-toned alloy"),
        ("JWL-0003", "Chandbali Bengal Earrings", "jewellery", "Chandbali", "Circular Bengal-inspired earrings with jewel-toned accents and delicate hanging beads.", 1490, 1890, 4, "Soft Gold", "Chandbali", "Gold-toned alloy"),
        ("JWL-0004", "Gramin Crescent Pendant", "jewellery", "Pendant", "A gold-toned crescent pendant with crystal details and tiny traditional bead drops.", 1690, 2190, 6, "Gold", "Crescent", "Gold-toned alloy"),
        ("JWL-0005", "Utsav Necklace Set", "jewellery", "Necklace Set", "A festive necklace and earring set with crystal drops in a warm rose-gold finish.", 2990, 3790, 2, "Rose Gold", "Crystal drops", "Gold-toned alloy"),
    ]
    products = []
    for sku, name, category, subcategory, description, price, compare_at, quantity, colour, motif, material in rows:
        products.append({
            "sku": sku, "name": name, "category": category, "subcategory": subcategory,
            "description": description, "price": price, "compare_at_price": compare_at,
            "quantity": quantity, "reorder_level": 3, "colour": colour, "motif": motif,
            "material": material, "image": f"assets/products/{sku.lower()}.jpg",
            "featured": sku in {"SAR-0001", "JWL-0001"}, "active": True,
        })
    return products


def image_prompt(product: dict) -> str:
    if product["category"] == "saree":
        subject = f"one {product['name']} Bengali saree, carefully folded with part of the pallav draped open so the weave, border and motif are clearly visible"
        materials = "authentic handloom fibres, woven borders, natural textile texture"
    else:
        subject = f"one complete {product['name']} jewellery design, arranged as a refined product set with every handcrafted detail visible"
        materials = "handcrafted folk-metal, enamel or clay texture appropriate to the named design"
    return (
        "Use case: product-mockup\n"
        "Asset type: KoriKatha ecommerce product catalogue image\n"
        f"Primary request: premium product photograph of {subject}.\n"
        "Scene/backdrop: warm matte ivory plaster surface with one very subtle Bengal-inspired shadow pattern, no props that obscure the product\n"
        "Style/medium: photorealistic premium Indian craft editorial product photography\n"
        "Composition/framing: centered square composition, generous clean margins, product fully visible and suitable for a 4:5 card crop\n"
        "Lighting/mood: soft directional studio daylight, restrained warm shadows, refined and authentic\n"
        f"Materials/textures: {materials}\n"
        "Constraints: exactly one product design; visually distinct from other catalogue items; culturally respectful; accurate craftsmanship; no people; no mannequin; no text; no price tag; no logo; no watermark\n"
        "Avoid: synthetic sheen, western bridal styling, excessive props, glitter effects, duplicate products, collage"
    )


def sql_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def write_outputs(products: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SUPABASE_DIR.mkdir(parents=True, exist_ok=True)
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)

    (DATA_DIR / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fields = list(products[0].keys())
    with (SUPABASE_DIR / "products.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(products)

    prompt_files = {
        "saree": PROMPT_DIR / "prompts-sarees.jsonl",
        "jewellery": PROMPT_DIR / "prompts-jewellery.jsonl",
    }
    for category, prompt_file in prompt_files.items():
        with prompt_file.open("w", encoding="utf-8") as handle:
            for product in (item for item in products if item["category"] == category):
                handle.write(
                    json.dumps(
                        {
                            "prompt": image_prompt(product),
                            "out": product["image"].split("/")[-1].replace("-web", ""),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    columns = fields
    statements = []
    for start in range(0, len(products), 100):
        values = []
        for product in products[start : start + 100]:
            values.append("(" + ", ".join(sql_value(product[col]) for col in columns) + ")")
        statements.append(
            "insert into public.products ("
            + ", ".join(columns)
            + ") values\n  "
            + ",\n  ".join(values)
            + "\non conflict (sku) do update set\n  "
            + ",\n  ".join(f"{col} = excluded.{col}" for col in columns if col != "sku")
            + ";"
        )
    (SUPABASE_DIR / "seed.sql").write_text("\n\n".join(statements) + "\n", encoding="utf-8")


def main() -> None:
    products = make_curated_catalogue()
    assert len(products) == 10
    assert len({p["sku"] for p in products}) == 10
    assert len({p["name"] for p in products}) == 10
    write_outputs(products)
    in_stock = sum(p["quantity"] > 0 for p in products)
    low_stock = sum(0 < p["quantity"] <= p["reorder_level"] for p in products)
    print(f"Generated {len(products)} products: {in_stock} in stock, {low_stock} low stock")


if __name__ == "__main__":
    main()
