import sys


def read_lines(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None

    lines = data.split(b"\n")

    # A final newline does not create an extra empty line.
    if lines and lines[-1] == b"":
        lines.pop()

    return lines


def myers(a, b):
    """
    Myers shortest-edit-script algorithm.

    Returns:
        ('=', i, j)  -> keep a[i] == b[j]
        ('-', i)     -> delete a[i]
        ('+', j)     -> insert b[j]
    """

    result = []

    def diff_range(a0, a1, b0, b1):
        n = a1 - a0
        m = b1 - b0

        if n == 0:
            for j in range(b0, b1):
                result.append(("+", j))
            return

        if m == 0:
            for i in range(a0, a1):
                result.append(("-", i))
            return

        # Already identical.
        if n == m:
            same = True

            for k in range(n):
                if a[a0 + k] != b[b0 + k]:
                    same = False
                    break

            if same:
                for k in range(n):
                    result.append(("=", a0 + k, b0 + k))
                return

        # Smallest possible non-zero edit distance: one insertion.
        if m == n + 1:
            i = a0
            j = b0
            skipped = False

            while i < a1 and j < b1:
                if a[i] == b[j]:
                    i += 1
                    j += 1
                elif not skipped:
                    skipped = True
                    j += 1
                else:
                    break

            if i == a1:
                i = a0
                j = b0

                while i < a1 and j < b1 and a[i] == b[j]:
                    result.append(("=", i, j))
                    i += 1
                    j += 1

                result.append(("+", j))
                j += 1

                while i < a1:
                    result.append(("=", i, j))
                    i += 1
                    j += 1

                return

        # Smallest possible non-zero edit distance: one deletion.
        if n == m + 1:
            i = a0
            j = b0
            skipped = False

            while i < a1 and j < b1:
                if a[i] == b[j]:
                    i += 1
                    j += 1
                elif not skipped:
                    skipped = True
                    i += 1
                else:
                    break

            if j == b1:
                i = a0
                j = b0

                while i < a1 and j < b1 and a[i] == b[j]:
                    result.append(("=", i, j))
                    i += 1
                    j += 1

                result.append(("-", i))
                i += 1

                while j < b1:
                    result.append(("=", i, j))
                    i += 1
                    j += 1

                return

        # Small cases.
        if n == 1 or m == 1:
            if n == 1:
                i = a0

                for j in range(b0, b1):
                    if a[i] == b[j]:
                        for jj in range(b0, j):
                            result.append(("+", jj))

                        result.append(("=", i, j))

                        for jj in range(j + 1, b1):
                            result.append(("+", jj))

                        return

                result.append(("-", i))

                for j in range(b0, b1):
                    result.append(("+", j))

                return

            j = b0

            for i in range(a0, a1):
                if a[i] == b[j]:
                    for ii in range(a0, i):
                        result.append(("-", ii))

                    result.append(("=", i, j))

                    for ii in range(i + 1, a1):
                        result.append(("-", ii))

                    return

            for i in range(a0, a1):
                result.append(("-", i))

            result.append(("+", j))
            return

        # Myers middle-snake search.
        #
        # We keep only the forward and backward frontiers rather than
        # storing the complete N x M dynamic-programming table.

        w = n - m
        total = n + m

        size = 2 * min(n, m) + 2

        forward = [0] * size
        backward = [0] * size

        for h in range((total // 2) + (total % 2) + 1):

            for direction in (0, 1):

                if direction == 0:
                    current = forward
                    other = backward
                    reverse = False
                else:
                    current = backward
                    other = forward
                    reverse = True

                low = -(h - 2 * max(0, h - m))
                high = h - 2 * max(0, h - n)

                for k in range(low, high + 1, 2):
                    idx = k % size

                    left = current[(k - 1) % size]
                    right = current[(k + 1) % size]

                    if k == -h or (
                        k != h and left < right
                    ):
                        x = right
                    else:
                        x = left + 1

                    y = x - k

                    start_x = x
                    start_y = y

                    while 0 <= x < n and 0 <= y < m:

                        if reverse:
                            if (
                                a[a1 - x - 1]
                                != b[b1 - y - 1]
                            ):
                                break
                        else:
                            if (
                                a[a0 + x]
                                != b[b0 + y]
                            ):
                                break

                        x += 1
                        y += 1

                    current[idx] = x

                    opposite_k = -(k - w)

                    if (
                        total % 2
                        == (1 if not reverse else 0)
                        and -(
                            h - (1 if not reverse else 0)
                        ) <= opposite_k
                        <= h - (1 if not reverse else 0)
                        and current[idx]
                        + other[opposite_k % size]
                        >= n
                    ):

                        if not reverse:
                            split_x = start_x
                            split_y = start_y

                            end_x = x
                            end_y = y
                        else:
                            split_x = n - x
                            split_y = m - y

                            end_x = n - start_x
                            end_y = m - start_y

                        # Left side.
                        diff_range(
                            a0,
                            a0 + split_x,
                            b0,
                            b0 + split_y,
                        )

                        # Middle snake.
                        xx = split_x
                        yy = split_y

                        while xx < end_x and yy < end_y:
                            result.append(
                                (
                                    "=",
                                    a0 + xx,
                                    b0 + yy,
                                )
                            )

                            xx += 1
                            yy += 1

                        # Right side.
                        diff_range(
                            a0 + end_x,
                            a1,
                            b0 + end_y,
                            b1,
                        )

                        return

        # Defensive fallback.
        for i in range(a0, a1):
            result.append(("-", i))

        for j in range(b0, b1):
            result.append(("+", j))

    diff_range(0, len(a), 0, len(b))

    return result


def line_diff(a, b):
    """
    Convert Myers' edit script into the required format.

    Inside every change block:
        deletions come first
        insertions come second
    """

    raw = myers(a, b)
    result = []

    i = 0

    while i < len(raw):

        if raw[i][0] == "=":
            result.append(raw[i])
            i += 1
            continue

        block = []

        while i < len(raw) and raw[i][0] != "=":
            block.append(raw[i])
            i += 1

        # Assignment requires delete-first ordering.
        for item in block:
            if item[0] == "-":
                result.append(item)

        for item in block:
            if item[0] == "+":
                result.append(item)

    return result


def changed_ranges(old, new):
    """
    Find the minimum changed character ranges between two strings.

    Python indexes strings by Unicode code point, which matches
    the assignment requirement.
    """

    edits = myers(old, new)

    old_ranges = []
    new_ranges = []

    old_pos = 0
    new_pos = 0

    old_start = None
    old_end = None

    new_start = None
    new_end = None

    def flush_old():
        nonlocal old_start, old_end

        if old_start is not None:
            old_ranges.append(
                (old_start, old_end)
            )

            old_start = None
            old_end = None

    def flush_new():
        nonlocal new_start, new_end

        if new_start is not None:
            new_ranges.append(
                (new_start, new_end)
            )

            new_start = None
            new_end = None

    for edit in edits:

        if edit[0] == "=":
            flush_old()
            flush_new()

            old_pos += 1
            new_pos += 1

        elif edit[0] == "-":
            flush_new()

            if old_start is None:
                old_start = old_pos

            old_end = old_pos + 1
            old_pos += 1

        else:
            flush_old()

            if new_start is None:
                new_start = new_pos

            new_end = new_pos + 1
            new_pos += 1

    flush_old()
    flush_new()

    def format_ranges(ranges):
        if not ranges:
            return "."

        return ",".join(
            f"{start}-{end}"
            for start, end in ranges
        )

    return (
        format_ranges(old_ranges),
        format_ranges(new_ranges),
    )


def print_lines_diff(a, b):
    script = line_diff(a, b)

    output = sys.stdout.buffer

    for edit in script:

        if edit[0] == "=":
            output.write(
                b" " + a[edit[1]] + b"\n"
            )

        elif edit[0] == "-":
            output.write(
                b"-" + a[edit[1]] + b"\n"
            )

        else:
            output.write(
                b"+" + b[edit[1]] + b"\n"
            )


def print_highlight_diff(a, b):
    script = line_diff(a, b)

    output = sys.stdout.buffer

    i = 0

    while i < len(script):

        # Keep line.
        if script[i][0] == "=":
            output.write(
                b" " + a[script[i][1]] + b"\n"
            )

            i += 1
            continue

        # Collect one complete change block.
        block = []

        while (
            i < len(script)
            and script[i][0] != "="
        ):
            block.append(script[i])
            i += 1

        deletes = [
            item[1]
            for item in block
            if item[0] == "-"
        ]

        inserts = [
            item[1]
            for item in block
            if item[0] == "+"
        ]

        # Part A output.
        for index in deletes:
            output.write(
                b"-" + a[index] + b"\n"
            )

        for index in inserts:
            output.write(
                b"+" + b[index] + b"\n"
            )

        # Pair the first deletion with the first insertion,
        # second with second, etc.
        pairs = min(
            len(deletes),
            len(inserts),
        )

        for pair in range(pairs):

            old_line = a[deletes[pair]].decode(
                "utf-8"
            )

            new_line = b[inserts[pair]].decode(
                "utf-8"
            )

            old_ranges, new_ranges = changed_ranges(
                old_line,
                new_line,
            )

            highlight = (
                f"? {old_ranges} | {new_ranges}\n"
            )

            output.write(
                highlight.encode("utf-8")
            )


def main() -> int:
    if (
        len(sys.argv) != 4
        or sys.argv[1] not in ("lines", "highlight")
    ):
        print(
            "usage: main.py lines|highlight A_PATH B_PATH",
            file=sys.stderr,
        )
        return 2

    command, a_path, b_path = sys.argv[1:]

    a = read_lines(a_path)
    b = read_lines(b_path)

    if a is None or b is None:
        print(
            "cannot read input file",
            file=sys.stderr,
        )
        return 2

    if command == "lines":
        print_lines_diff(a, b)

    else:
        print_highlight_diff(a, b)

    return 0


raise SystemExit(main())