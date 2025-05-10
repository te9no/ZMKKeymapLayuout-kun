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

st.title("ZMK Keymap Formatter (Aligned Text Output)")

layout_input = st.text_area("① Paste the `physical layout` block here:", height=300)
keymap_input = st.text_area("② Paste the `keymap layer` block here:", height=300)

spacing_unit = st.slider("Indent unit (X distance per space):", min_value=10, max_value=200, value=50, step=10)

if layout_input and keymap_input:
    # Extract coordinates
    coords = re.findall(r"&key_physical_attrs\s+\d+\s+\d+\s+(-?\d+)\s+(-?\d+)", layout_input)
    coords = [(int(x), int(y)) for x, y in coords]

    # Extract keycodes
    keycodes = re.findall(r"&(?:\S+\s+)*?\S+(?=\s*&|$)", keymap_input)

    if len(coords) != len(keycodes):
        st.warning(f"⚠️ Key count mismatch (coords: {len(coords)}, keycodes: {len(keycodes)})")

    # Pair keys with coords
    keys_with_coords = []
    for i, (x, y) in enumerate(coords):
        code = keycodes[i] if i < len(keycodes) else ""
        keys_with_coords.append((x, y, code))

    # Group by approximate Y rows
    rows = defaultdict(list)
    for x, y, code in keys_with_coords:
        row_key = (y // 100) * 100
        rows[row_key].append((x, code))

    output_lines = []
    for y in sorted(rows):
        row = sorted(rows[y], key=lambda p: p[0])  # Sort by X
        line = ""
        cursor = 0  # visual space cursor
        for x, code in row:
            target_indent = int(x / spacing_unit)
            space_needed = target_indent - cursor
            line += " " * max(space_needed, 0) + code + " "
            cursor = target_indent + int((len(code) + 1) / spacing_unit)
        output_lines.append("    " + line.rstrip())

    # Output
    st.code("\n".join(output_lines), language="c")

    # Debug log
    with st.expander("🔧 Debug Log", expanded=False):
        st.write(f"Extracted keycodes: {len(keycodes)}")
        st.write(f"Extracted coordinates: {len(coords)}")
        st.write(f"Indent unit: {spacing_unit}")
        for y in sorted(rows):
            st.write(f"Row {y}: {len(rows[y])} keys")
