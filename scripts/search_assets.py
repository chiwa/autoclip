#!/usr/bin/env python3
"""AutoClip Reusable Asset Search CLI.

Performs fast, deterministic, bilingual (Thai and English) local text search
over `assets/reusable-library/assets-index.jsonl`.
Ranks assets using token matching, exact phrase bonuses, and field-weighted relevance.
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Try to import pythainlp for high accuracy Thai word segmentation
try:
    from pythainlp.tokenize import word_tokenize as thai_word_tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False


def is_thai_char(ch: str) -> bool:
    """Check if character is in Thai Unicode block (U+0E00 - U+0E7F)."""
    return "\u0e00" <= ch <= "\u0e7f"


def tokenize_query(text: str) -> List[str]:
    """Tokenize query string supporting both Thai and Latin words."""
    text = text.strip()
    if not text:
        return []

    tokens: List[str] = []
    has_thai = any(is_thai_char(c) for c in text)

    if has_thai and HAS_PYTHAINLP:
        try:
            thai_tokens = thai_word_tokenize(text, engine="newmm", keep_whitespace=False)
            for t in thai_tokens:
                t_clean = t.strip().lower()
                if len(t_clean) > 1 or (len(t_clean) == 1 and not t_clean.isspace()):
                    tokens.append(t_clean)
        except Exception:
            pass

    # Extract Latin words/numbers and Thai substrings via regex
    latin_words = re.findall(r"[a-zA-Z0-9_\-]+", text.lower())
    for w in latin_words:
        if len(w) > 1 and w not in tokens:
            tokens.append(w)

    # Fallback for Thai if pythainlp wasn't available or missed
    if has_thai and not HAS_PYTHAINLP:
        # 2-gram and 3-gram character shingles for Thai text
        thai_only = "".join(c for c in text if is_thai_char(c))
        for n in (2, 3):
            for i in range(len(thai_only) - n + 1):
                shingle = thai_only[i : i + n]
                if shingle not in tokens:
                    tokens.append(shingle)

    return list(dict.fromkeys(tokens))  # preserve order, deduplicate


def score_record(query: str, query_tokens: List[str], record: Dict[str, Any]) -> float:
    """Calculate relevance score for a record based on field weights and exact matches."""
    query_lower = query.lower().strip()
    score = 0.0

    field_weights = {
        "topic": 3.0,
        "title": 3.0,
        "visual_prompt": 2.5,
        "narration": 2.0,
        "description": 2.0,
        "tags": 2.0,
        "source_project": 1.5,
        "source_scene": 1.0,
        "brand": 1.0,
        "role": 0.8,
    }

    # Exact full query match bonus
    for field, weight in field_weights.items():
        val = record.get(field, "")
        if isinstance(val, list):
            val_str = " ".join(str(v) for v in val).lower()
        else:
            val_str = str(val).lower()

        if not val_str:
            continue

        # Exact phrase match
        if query_lower in val_str:
            score += 5.0 * weight

        # Substring / token matching
        for token in query_tokens:
            if token in val_str:
                # Count occurrences (log-scaled)
                count = val_str.count(token)
                score += weight * (1.0 + math.log1p(count))

    return round(score, 3)


def search_assets(
    index_path: Path,
    query: str,
    limit: int = 10,
    role_filter: Optional[str] = None,
    reuse_filter: Optional[str] = None,
    brand_filter: Optional[str] = None,
    min_score: float = 0.1,
) -> List[Tuple[float, Dict[str, Any]]]:
    """Search catalog index and return scored records."""
    if not index_path.is_file():
        return []

    query_tokens = tokenize_query(query)
    results: List[Tuple[float, Dict[str, Any]]] = []

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)

            # Apply filters
            if role_filter and rec.get("role") != role_filter:
                continue
            if reuse_filter and rec.get("reuse") != reuse_filter:
                continue
            if brand_filter and rec.get("brand") != brand_filter:
                continue

            score = score_record(query, query_tokens, rec)
            if score >= min_score:
                results.append((score, rec))

    # Sort descending by score, then asset_id for determinism
    results.sort(key=lambda x: (-x[0], x[1]["asset_id"]))
    return results[:limit]


def format_search_results(results: List[Tuple[float, Dict[str, Any]]], as_json: bool = False) -> str:
    """Format search results for terminal output."""
    if as_json:
        output_list = []
        for score, rec in results:
            item = dict(rec)
            item["score"] = score
            output_list.append(item)
        return json.dumps(output_list, ensure_ascii=False, indent=2)

    if not results:
        return "No matching assets found in catalog."

    lines: List[str] = [
        f"Found {len(results)} matching asset(s):\n",
        f"{'Score':<7} | {'Project':<25} | {'Scene':<10} | {'Role':<10} | {'Reuse':<18} | {'Description / Topic'}",
        "-" * 110,
    ]

    for score, rec in results:
        proj = rec.get("source_project", "")[:24]
        scene = str(rec.get("source_scene", ""))[:9]
        role = rec.get("role", "")[:9]
        reuse = rec.get("reuse", "")[:17]
        desc = (rec.get("visual_prompt") or rec.get("narration") or rec.get("topic") or rec.get("description") or "")[:40]

        lines.append(f"{score:<7.1f} | {proj:<25} | {scene:<10} | {role:<10} | {reuse:<18} | {desc}")
        lines.append(f"        -> Library Path:   {rec.get('library_path')}")
        lines.append(f"        -> Thumbnail Path: {rec.get('thumbnail_path')}")
        if rec.get("tags"):
            lines.append(f"        -> Tags: {', '.join(rec['tags'][:6])}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search AutoClip Reusable Asset Catalog")
    parser.add_argument("query", type=str, help="Search query (Thai or English)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of results (default: 10)")
    parser.add_argument("--role", type=str, default=None, help="Filter by role (hook, content, outro, branding, etc.)")
    parser.add_argument("--reuse", type=str, default=None, help="Filter by reuse recommendation (reuse_direct, reuse_as_reference)")
    parser.add_argument("--brand", type=str, default=None, help="Filter by brand (mamase, 12-zodiac, thai-java-zone)")
    parser.add_argument("--min-score", type=float, default=0.1, help="Minimum score threshold (default: 0.1)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--catalog-dir", type=str, default=None, help="Explicit reusable-library directory")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    library_dir = Path(args.catalog_dir) if args.catalog_dir else repo_root / "assets" / "reusable-library"
    index_path = library_dir / "assets-index.jsonl"

    if not index_path.is_file():
        # Check fallback to assets/catalog if migrated
        alt_path = repo_root / "assets" / "catalog" / "assets-index.jsonl"
        if alt_path.is_file():
            index_path = alt_path
        else:
            print(f"Error: Asset index not found at {index_path}.", file=sys.stderr)
            print("Run 'python scripts/build_asset_catalog.py' first to build the catalog.", file=sys.stderr)
            sys.exit(1)

    results = search_assets(
        index_path=index_path,
        query=args.query,
        limit=args.limit,
        role_filter=args.role,
        reuse_filter=args.reuse,
        brand_filter=args.brand,
        min_score=args.min_score,
    )

    print(format_search_results(results, as_json=args.json))


if __name__ == "__main__":
    main()
