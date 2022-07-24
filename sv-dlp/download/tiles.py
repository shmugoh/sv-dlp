from PIL import Image

def stich(row_io_arr):
    images = [Image.open(x) for x in row_io_arr]
    widths, heights = zip(*(i.size for i in images))
    total_width, max_height = sum(widths), max(heights)
    row_img = Image.new('RGB', (total_width, max_height))

    x = 0
    for m in images:
        if m == images[0]:
            row_img.paste(m, (0, 0))
        else:
            row_img.paste(m, (last_image.width*x, 0))
        last_image = m
        x += 1

    # row_img.show()
    return row_img

def merge(rows_io_arr):
    images = [img for img in rows_io_arr]

    height = 0
    height_sum = 0
    for img in images: height += img.height
    merged_img = Image.new('RGB', (images[0].width, height))

    y = 0
    for row in images:
        if row == images[0]:
            merged_img.paste(row, (0, 0))
        else:
            height_sum += last_row.height
            merged_img.paste(row, (0, height_sum))
        last_row = row
        y += 1

    # merged_img.show()
    return merged_img