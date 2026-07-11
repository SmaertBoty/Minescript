from system.lib.minescript import get_block_region, BlockRegion
from concurrent.futures import ThreadPoolExecutor

def get_large_block_region(corner1:tuple[int,int,int], corner2:tuple[int,int,int], chunksize:int=32) -> BlockRegion:
    """
    Grabs a massive region of blocks, in a very short amount of time
    
    Adjust `chunksize` to tweak performance:
    - Lower `chunksize` -> slower, higher framerate
    - Higher `chunksize` -> faster, lower framerate
    """
    min_corner = (min(corner1[0], corner2[0]), min(corner1[1], corner2[1]), min(corner1[2], corner2[2]))
    max_corner = (max(corner1[0], corner2[0]), max(corner1[1], corner2[1]), max(corner1[2], corner2[2]))
    max_corner = [c-1 for c in max_corner]
    axes = []
    for i in range(3):
        axis_chunks = []
        pos = min_corner[i]
        mx = max_corner[i]
        while pos <= mx:
            end = pos + chunksize - 1
            if end > mx:
                end = mx
            axis_chunks.append((pos, end))
            pos = end + 1
        axes.append(axis_chunks)
    futures = []
    with ThreadPoolExecutor(max_workers=None) as executor:
        for y in axes[1]:
            for z in axes[2]:
                for x in axes[0]:
                    chunk_min = (x[0], y[0], z[0])
                    chunk_max = (x[1], y[1], z[1])
                    future = executor.submit(get_block_region, chunk_min, chunk_max, False)
                    futures.append(future)
    all_blocks = []
    for future in futures:
        r = future.result()
        all_blocks.extend(r.blocks)
    return BlockRegion(min_corner, max_corner, tuple(all_blocks))
