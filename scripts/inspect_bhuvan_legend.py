from PIL import Image

path = r"data\processed\bhuvan_mh_latur_lulc_legend.png"

img = Image.open(path)

print("=" * 70)
print("BHUVAN LULC LEGEND")
print("=" * 70)

print("Format:", img.format)
print("Size:", img.size)
print("Mode:", img.mode)

print("\nOpening legend image...")

img.show()