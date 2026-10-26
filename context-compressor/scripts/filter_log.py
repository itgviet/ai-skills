#!/usr/bin/env python3
"""Shrink a long build/test/CI log to the lines around errors.

Keeps every line matching an error pattern plus N lines of context on each side,
strips ANSI colors, drops progress bars and consecutive duplicate lines, and caps
the output. Summary goes to stderr so stdout stays clean for the agent to read.

Stdlib only, Python 3.9+.
"""
import argparse
import re
import sys

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07")
ERROR = re.compile(
    r"\b(error|errors|exception|traceback|fatal|failed|failure|fail|panic|segfault|"
    r"cannot find|could not|undefined reference|unresolved reference|not found|denied|refused|timed? ?out)\b"
    r"|\b\w+(Error|Exception):|^e: |^\[ERROR\]"
    r"|\bE\d{3,}\b|^\s*at [\w.$<>]+\(|^\s+File \".*\", line \d+|FAILURE:|BUILD FAILED|npm ERR!|✗|✖",
    re.IGNORECASE,
)
# Lines that look like errors but are not (test summaries with zero failures, etc.)
FALSE_POSITIVE = re.compile(r"\b0 (errors?|failed|failures?)\b|\berrors?: 0\b|\bfailed: 0\b", re.IGNORECASE)
PROGRESS = re.compile(
    r"^\s*\d{1,3}%|[█▓▒░#=>-]{10,}|^\s*\[[=#>.\- ]+\]\s*\d{1,3}%|\[\s*\d+/\d+\]|^\s*(Downloading|Downloaded|Progress|Resolving|Fetching)\b"
    r"|^\s*[|/\\-]\s*$|\d+(\.\d+)?\s*[kKmMgG]i?B/s"
)


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="Lọc log dài: giữ dòng lỗi + ngữ cảnh, bỏ ANSI/progress bar/dòng lặp.",
        epilog="Ví dụ:\n  python scripts/filter_log.py build.log\n"
               "  gradlew assembleDebug 2>&1 | python scripts/filter_log.py -C 8\n"
               "Thoát 0 kể cả khi không thấy lỗi (khi đó in đuôi log).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("file", nargs="?", help="File log; bỏ trống hoặc '-' để đọc stdin")
    p.add_argument("-C", "--context", type=int, default=15, help="Số dòng ngữ cảnh mỗi phía (mặc định 15)")
    p.add_argument("--max-lines", type=int, default=200, help="Giới hạn số dòng in ra (mặc định 200)")
    p.add_argument("--tail", type=int, default=40, help="Số dòng cuối in ra khi không tìm thấy lỗi (mặc định 40)")
    p.add_argument("--pattern", help="Regex bổ sung coi là lỗi (ví dụ tên test cụ thể)")
    return p.parse_args(argv)


def read_lines(path):
    if not path or path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            data = f.read()
    # Windows PowerShell redirection may write UTF-16 or UTF-8 with BOM
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = data.decode("utf-16", errors="replace")
    else:
        text = data.decode("utf-8-sig", errors="replace")
    text = text.replace("\r\n", "\n")
    # Carriage-return progress updates: keep only the last state of each line
    return [line.rsplit("\r", 1)[-1] for line in text.split("\n")]


def clean(lines):
    """Strip ANSI, drop progress lines and consecutive duplicates; keep original line numbers."""
    out, prev = [], None
    for no, raw in enumerate(lines, 1):
        line = ANSI.sub("", raw).rstrip()
        if PROGRESS.search(line) and not ERROR.search(line):
            continue
        if line == prev:
            continue
        prev = line
        out.append((no, line))
    return out


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv)
    try:
        raw = read_lines(args.file)
    except OSError as e:
        print(f"Error: không đọc được '{args.file}': {e.strerror}", file=sys.stderr)
        return 1
    extra = re.compile(args.pattern) if args.pattern else None
    lines = clean(raw)

    hits = [i for i, (_, l) in enumerate(lines)
            if (ERROR.search(l) and not FALSE_POSITIVE.search(l)) or (extra and extra.search(l))]
    if hits:
        keep = set()
        for i in hits:
            keep.update(range(max(0, i - args.context), min(len(lines), i + args.context + 1)))
        selected = sorted(keep)
    else:
        selected = list(range(max(0, len(lines) - args.tail), len(lines)))

    output, last_no = [], None
    for i in selected:
        no, line = lines[i]
        if last_no is not None and no != last_no + 1:
            output.append("...")
        output.append(f"{no:>6}: {line}")
        last_no = no
    truncated = len(output) > args.max_lines
    if truncated:
        output = output[: args.max_lines] + [f"... [cắt bớt, còn {len(selected) - args.max_lines}+ dòng; tăng --max-lines hoặc giảm -C]"]

    first = lines[hits[0]][0] if hits else None
    print(f"[filter_log] tổng {len(raw)} dòng, sau lọc {len(lines)}, in {min(len(selected), args.max_lines)}; "
          f"{len(hits)} dòng khớp lỗi" + (f", lỗi đầu tiên ở dòng {first}" if first else ", không thấy lỗi — in đuôi log"),
          file=sys.stderr)
    print("\n".join(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
