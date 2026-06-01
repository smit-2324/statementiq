import pdfplumber
import io
import re
from pathlib import Path


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract transaction-relevant text from a bank statement PDF.
    Deduplicates repeated page headers to cut token count significantly.
    """
    all_lines: list[str] = []
    line_counts: dict[str, int] = {}

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        cleaned = [cell.strip() if cell else "" for cell in row]
                        line = " | ".join(cleaned)
                        if line.strip():
                            line_counts[line] = line_counts.get(line, 0) + 1
                            all_lines.append(line)
            else:
                text = page.extract_text()
                if text:
                    for line in text.splitlines():
                        line = line.strip()
                        if line:
                            line_counts[line] = line_counts.get(line, 0) + 1
                            all_lines.append(line)

    # Drop lines that appear on nearly every page — those are headers/footers
    # (seen on >60% of pages means it's boilerplate, not transaction data)
    repeat_threshold = max(2, num_pages * 0.6)
    seen_boilerplate: set[str] = set()
    filtered: list[str] = []
    for line in all_lines:
        if line_counts.get(line, 0) >= repeat_threshold:
            if line not in seen_boilerplate:
                filtered.append(line)  # keep first occurrence only
                seen_boilerplate.add(line)
        else:
            filtered.append(line)

    # Collapse runs of blank-ish separators
    text = "\n".join(filtered)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_text_from_path(path: str | Path) -> str:
    with open(path, "rb") as f:
        return extract_text_from_pdf(f.read())


def truncate_for_analysis(text: str, max_chars: int = 40000) -> str:
    """
    40k chars ≈ 10k tokens — enough for any standard bank statement.
    Keeps header (account info) + all transactions.
    """
    if len(text) <= max_chars:
        return text
    keep_start = int(max_chars * 0.8)
    keep_end = int(max_chars * 0.15)
    return text[:keep_start] + "\n...[middle truncated]...\n" + text[-keep_end:]
