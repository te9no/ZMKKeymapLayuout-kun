import streamlit as st
import re
from collections import defaultdict

st.title("ZMK Keymap 整形ツール（インデント付き・テキスト入力版）")

layout_input = st.text_area("① physical layout ブロックを貼り付けてください", height=300)
keymap_input = st.text_area("② keymap layer ブロックを貼り付けてください", height=300)

# ユーザーが spacing 単位を調整できるように
spacing_unit = st.slider("インデント幅調整（1スペースあたりのX距離）", min_value=10, max_value=200, value=50, step=10)

if layout_input and keymap_input:
    # 物理レイアウトの座標抽出
    coords = re.findall(r"&key_physical_attrs\s+\d+\s+\d+\s+(-?\d+)\s+(-?\d+)", layout_input)
    coords = [(int(x), int(y)) for x, y in coords]

    # キーコード抽出（スペースを含む&～単位）
    keycodes = re.findall(r"&(?:\S+\s+)*?\S+(?=\s*&|$)", keymap_input)

    # 警告：数が合わない場合
    if len(coords) != len(keycodes):
        st.warning(f"⚠️ キー数が一致しません（coords: {len(coords)}, keycodes: {len(keycodes)}）")

    # 座標とキーコードの対応付け
    keys_with_coords = []
    for i, (x, y) in enumerate(coords):
        code = keycodes[i] if i < len(keycodes) else ""
        keys_with_coords.append((x, y, code))

    # Y座標を100単位で丸めて行に分類
    rows = defaultdict(list)
    for x, y, code in keys_with_coords:
        row_key = (y // 100) * 100
        rows[row_key].append((x, code))

    # ✅ x座標に応じたスペースインデント付き整形
    output_lines = []
    for y in sorted(rows):
        row = sorted(rows[y], key=lambda p: p[0])  # X昇順
        line = ""
        last_indent = 0
        for x, code in row:
            # キーコードの文字数を元にインデントを計算
            code_length = len(code)
            indent_spaces = max(0, int(x // spacing_unit) + code_length // 4)  # 文字数によるインデント調整（4文字ごとに1スペース）
            
            # 必要なスペースだけ追加（重複しないように）
            space_diff = indent_spaces - last_indent
            line += " " * max(space_diff, 0) + code + " "
            last_indent = indent_spaces + 1
        output_lines.append("    " + line.rstrip() + ",")

    # 出力
    result = "LAYOUT(\n" + "\n".join(output_lines) + "\n)"
    st.code(result, language="c")

    # 簡易ログ
    with st.expander("🔧 デバッグログ", expanded=True):
        st.write(f"抽出されたキー数: {len(keycodes)}")
        st.write(f"抽出された座標数: {len(coords)}")
        st.write(f"使用インデント単位 spacing_unit: {spacing_unit}")
        for y in sorted(rows):
            st.write(f"行 {y}: {len(rows[y])} キー")
