import math
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

class bing:
    TILE_SIZE = 256

    def _stitch_four(face):
        """
        Stitches four consecutive individual tiles.
        """
        sub_tile = Image.new('RGB', (bing.TILE_SIZE * 2, bing.TILE_SIZE * 2))
        for idx, tile in enumerate(face[0:4]):
            tile_img = Image.open(tile)
            x = idx % 2
            y = idx // 2
            sub_tile.paste(im=tile_img, box=(x * bing.TILE_SIZE, y * bing.TILE_SIZE))
        return sub_tile

    split_list = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    def stitch(face):
        """
        Stitches one face of a panorama.
        """
        if len(face) <= 4:
            return bing._stitch_four(face)
        else:
            grid_size = int(math.sqrt(len(face)))
            stitched_tile_size = (grid_size // 2) * bing.TILE_SIZE
            tile = Image.new('RGB', (stitched_tile_size * 2, stitched_tile_size * 2))
            split = bing.split_list(face, len(face) // 4)
            tile.paste(im=bing.stitch(split[0]), box=(0, 0))
            tile.paste(im=bing.stitch(split[1]), box=(stitched_tile_size, 0))
            tile.paste(im=bing.stitch(split[2]), box=(0, stitched_tile_size))
            tile.paste(im=bing.stitch(split[3]), box=(stitched_tile_size, stitched_tile_size))
            return tile
    
    def merge(faces, pbar):
        """
        Stitches downloaded tiles into a full image.
        """
        full_tile_size = int(math.sqrt(len(faces[1]))) * bing.TILE_SIZE
        pano_width = 4 * full_tile_size
        pano_height = 3 * full_tile_size
        panorama = Image.new('RGB', (pano_width, pano_height))
        stitched_faces = []
        if len(faces[1]) == 1:
            for i in range(0, 6):
                stitched_faces.append(Image.open(faces[i][0]))
        else:
            for i in range(0, 6):
                stitched_faces.append(bing.stitch(faces[i]))
        panorama.paste(im=stitched_faces[0], box=(1 * full_tile_size, 1 * full_tile_size))
        pbar.update(1)
        panorama.paste(im=stitched_faces[1], box=(2 * full_tile_size, 1 * full_tile_size))
        pbar.update(1)
        panorama.paste(im=stitched_faces[2], box=(3 * full_tile_size, 1 * full_tile_size))
        pbar.update(1)
        panorama.paste(im=stitched_faces[3], box=(0, 1 * full_tile_size))
        pbar.update(1)
        panorama.paste(im=stitched_faces[4], box=(1 * full_tile_size, 0))
        pbar.update(1)
        panorama.paste(im=stitched_faces[5], box=(1 * full_tile_size, 2 * full_tile_size))
        pbar.update(1)
        return panorama