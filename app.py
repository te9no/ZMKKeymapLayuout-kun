import streamlit as st
import re
from collections import defaultdict

# Wider layout styling
st.markdown("""
    <style>
        .block-container {
            max-width: 90% !important;
            padding-left: 5%;
            padding-right: 5%;
        }
        textarea, pre {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("ZMK Keymap Formatter (Text Input + Aligned Output)")

layout_input = st.text_area("① Paste the `physical layout` block here:", height=300)
keymap_input = st.text_area("② Paste the `keymap layer` block here:", height=300)

spacing_unit = st.slider("Indent unit (X distance per space):", min_value=10, max_value=200, value=50, step=10)

if layout_input and keymap_input:
    coords = re.findall(r"&key_physical_attrs\s+\d+\s+\d+\s+(-?\d+)\s+(-?\d+)", layout_input)
    coords = [(int(x), int(y)) for x, y in coords]

    keycodes = re.findall(r"&(?:\S+\s+)*?\S+(?=\s*&|$)", keymap_input)

    if len(coords) != len(keycodes):
        st.warning(f"⚠️ Key count mismatch (coords: {len(coords)}, keycodes: {len(keycodes)})")

    # Match coordinates and keycodes
    keys_with_coords = []
    for i, (x, y) in enumerate(coords):
        code = keycodes[i] if i < len(keycodes) else ""
        keys_with_coords.append((x, y, code))

    # Group by row using Y coordinate
    rows = defaultdict(list)
    for x, y, code in keys_with_coords:
        row_key = (y // 100) * 100
        rows[row_key].append((x, code))

    # Build all rows sorted by Y, then X
    column_positions = defaultdict(dict)
    max_cols = 0

    # First pass: determine column indices and max width per column
    col_widths = defaultdict(int)
    row_lines = []
    for y in sorted(rows):
        row = sorted(rows[y], key=lambda p: p[0])
        row_line = []
        for x, code in row:
            col = x // spacing_unit
            row_line.append((col, code))
            col_widths[col] = max(col_widths[col], len(code))
            max_cols = max(max_cols, col)
        row_lines.append((y, row_line))

    # Second pass: build aligned lines
    output_lines = []
    for y, row in row_lines:
        line_parts = []
        col_map = dict(row)
        for col in range(max_cols + 1):
            code = col_map.get(col, "")
            if code:
                padded = code.ljust(col_widths[col])
            else:
                padded = " " * col_widths[col]
            line_parts.append(padded)
        output_lines.append("    " + " ".join(line_parts).rstrip())

    result = "\n".join(output_lines)
    st.code(result, language="c")

    # Debug log
    with st.expander("🔧 Debug Log", expanded=True):
        st.write(f"Extracted keycodes: {len(keycodes)}")
        st.write(f"Extracted coordinates: {len(coords)}")
        st.write(f"Indent unit: {spacing_unit}")
        for y in sorted(rows):
            st.write(f"Row {y}: {len(rows[y])} keys")
