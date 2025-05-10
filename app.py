import streamlit as st
import re
from collections import defaultdict

st.title("ZMK Keymap 整形ツール（インデント付き・テキスト入力版）")

layout_input = st.text_area("① physical layout ブロックを貼り付けてください", height=300)
keymap_input = st.text_area("② keymap layer ブロックを貼り付けてください", height=300)

spacing_unit = st.slider("インデント幅調整（1スペースあたりのX距離）", min_value=10, max_value=200, value=50, step=10)

if layout_input and keymap_input:
    coords = re.findall(r"&key_physical_attrs\s+\d+\s+\d+\s+(-?\d+)\s+(-?\d+)", layout_input)
    coords = [(int(x), int(y)) for x, y in coords]

    keycodes = re.findall(r"&(?:\S+\s+)*?\S+(?=\s*&|$)", keymap_input)

    if len(coords) != len(keycodes):
        st.warning(f"⚠️ キー数が一致しません（coords: {len(coords)}, keycodes: {len(keycodes)}）")

    # 座標とキーコードの対応付け
    keys_with_coords = []
    for i, (x, y) in enumerate(coords):
        code = keycodes[i] if i < len(keycodes) else ""
        keys_with_coords.append((x, y, code))

    # 列ごとのインデックスを計算し、Y軸ごとに行を分ける
    rows = defaultdict(list)
    for x, y, code in keys_with_coords:
        row_key = (y // 100) * 100
        col_index = x // spacing_unit
        rows[row_key].append((col_index, code))

    # 列ごとの最大文字長を計算
    column_widths = defaultdict(int)
    for row in rows.values():
        for col, code in row:
            column_widths[col] = max(column_widths[col], len(code))

    # 出力整形
    output_lines = []
    for y in sorted(rows):
        line = []
        current_row = rows[y]
        col_dict = {col: code for col, code in current_row}
        max_col = max(column_widths.keys())

        for col in range(max_col + 1):
            code = col_dict.get(col, "")
            if code:
                padded = code.ljust(column_widths[col])
            else:
                padded = " " * column_widths[col]
            line.append(padded)
        output_lines.append("    " + " ".join(line).rstrip())

    result = "\n".join(output_lines)
    st.code(result, language="c")

    with st.expander("🔧 デバッグログ", expanded=True):
        st.write(f"抽出されたキー数: {len(keycodes)}")
        st.write(f"抽出された座標数: {len(coords)}")
        st.write(f"使用インデント単位 spacing_unit: {spacing_unit}")
        for y in sorted(rows):
            st.write(f"行 {y}: {len(rows[y])} キー")
