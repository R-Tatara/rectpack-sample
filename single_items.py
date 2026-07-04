from rectpack import (
    newPacker, PackingMode, PackingBin,
    SORT_NONE, SORT_AREA, SORT_PERI, SORT_DIFF, SORT_SSIDE, SORT_LSIDE, SORT_RATIO
)
from rectpack.maxrects import MaxRectsBl, MaxRectsBssf, MaxRectsBaf, MaxRectsBlsf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

# Bin dimensions (cm)
BIN_WIDTH, BIN_HEIGHT = 69, 51

# Workpiece dimensions (cm)
WORKPIECE_WIDTH, WORKPIECE_HEIGHT = 14, 11

# Number of layers per bin
NUM_LAYERS = 3

# Number of workpieces to pack
NUM_WORKPIECES = 200


def calculate_required_bins() -> int:
    # Calculate required number of bins based on total area with safety factor
    # Takes into account NUM_LAYERS to calculate effective capacity per bin
    total_workpiece_area = WORKPIECE_WIDTH * WORKPIECE_HEIGHT * NUM_WORKPIECES
    bin_area = BIN_WIDTH * BIN_HEIGHT
    effective_bin_area = bin_area * NUM_LAYERS
    theoretical_bins = math.ceil(total_workpiece_area / effective_bin_area)
    # Apply safety factor (1.5x) to account for packing inefficiency
    safety_bins = math.ceil(theoretical_bins * 1.5)
    return safety_bins


def convert_virtual_to_physical(virtual_bin_idx: int) -> tuple[int, int]:
    # Convert virtual bin index to (physical box index, layer index)
    # Example: virtual_bin=0 -> (box=0, layer=0), virtual_bin=1 -> (box=0, layer=1)
    box_idx = virtual_bin_idx // NUM_LAYERS
    layer_idx = virtual_bin_idx % NUM_LAYERS
    return box_idx, layer_idx


def setup_packer():
    # Create packer with explicit default arguments
    # Options:
    #   mode: Offline batch calculation (1) or Online sequential calculation (0)
    #   bin_algo: BNF (Bin next fit) (0), BFF (Bin first fit) (1), 
    #             BBF (Bin best fit) (2), Global (3)
    #   pack_algo: ○MaxRectsBl (Bottom-Left), ✕MaxRectsBssf (Best Short Side Fit),
    #              ◎MaxRectsBaf (Best Area Fit), ✕MaxRectsBlsf (Best Long Side Fit)
    #   sort_algo: SORT_NONE, SORT_AREA (w * h), SORT_PERI(w + h), SORT_DIFF (abs(w - h)),
    #              SORT_SSIDE (short side), SORT_LSIDE (long side), SORT_RATIO (w / h)
    #   rotation: True (allow rotation) or False (no rotation)
    packer = newPacker(
        mode=PackingMode.Offline,
        bin_algo=PackingBin.BBF,
        pack_algo=MaxRectsBl,
        sort_algo=SORT_AREA,
        rotation=True
    )

    for i in range(NUM_WORKPIECES):
        packer.add_rect(WORKPIECE_WIDTH, WORKPIECE_HEIGHT, rid=i)

    # Add virtual bins: physical bins × NUM_LAYERS
    # Each layer is treated as a separate virtual bin
    required_bins = calculate_required_bins()
    num_virtual_bins = required_bins * NUM_LAYERS
    for _ in range(num_virtual_bins):
        packer.add_bin(BIN_WIDTH, BIN_HEIGHT)

    return packer


def display_results(packer):
    # Show packing results grouped by box and layer
    all_rects = packer.rect_list()
    
    # Group rectangles by (box_idx, layer_idx)
    bins_dict = {}
    for rect in all_rects:
        virtual_bin_idx, x, y, w, h, workpiece_id = rect
        box_idx, layer_idx = convert_virtual_to_physical(virtual_bin_idx)
        key = (box_idx, layer_idx)
        if key not in bins_dict:
            bins_dict[key] = []
        bins_dict[key].append(rect)
    
    # Display results sorted by box number then layer number
    for key in sorted(bins_dict.keys()):
        box_idx, layer_idx = key
        rects_in_bin = bins_dict[key]
        print(f"\nBox {box_idx}, Layer {layer_idx}: {len(rects_in_bin)} items")
        for rect in rects_in_bin:
            _, x, y, w, h, workpiece_id = rect
            print(f"  ID:{workpiece_id} position: ({x},{y}) size: {w}x{h}")


def visualize_packing(packer):
    # Visualize packing results with matplotlib
    all_rects = packer.rect_list()
    bins_dict = _group_rects_by_bin(all_rects)
    
    if len(bins_dict) == 0:
        print("No packing results available")
        return
    
    # Determine grid dimensions: rows = layers, cols = boxes
    box_indices = sorted(set(box_idx for box_idx, _ in bins_dict.keys()))
    num_boxes = len(box_indices)
    
    # Create subplots: NUM_LAYERS rows × num_boxes columns
    fig, axes = plt.subplots(NUM_LAYERS, num_boxes, figsize=(8 * num_boxes, 6 * NUM_LAYERS))
    
    # Ensure axes is 2D array
    if NUM_LAYERS == 1 and num_boxes == 1:
        axes = [[axes]]
    elif NUM_LAYERS == 1:
        axes = [axes]
    elif num_boxes == 1:
        axes = [[ax] for ax in axes]
    
    # Draw each box and layer
    for layer_idx in range(NUM_LAYERS):
        for col_idx, box_idx in enumerate(box_indices):
            key = (box_idx, layer_idx)
            if key in bins_dict:
                _draw_bin(axes[layer_idx][col_idx], box_idx, layer_idx, bins_dict[key])
            else:
                # Empty bin/layer
                _draw_bin(axes[layer_idx][col_idx], box_idx, layer_idx, [])
    
    plt.tight_layout(pad=5.0, w_pad=10.0, h_pad=10.0)
    plt.show()


def _group_rects_by_bin(all_rects: list) -> dict:
    # Group rectangles by (box_idx, layer_idx)
    bins_dict = {}
    for rect in all_rects:
        virtual_bin_idx, x, y, w, h, workpiece_id = rect
        box_idx, layer_idx = convert_virtual_to_physical(virtual_bin_idx)
        key = (box_idx, layer_idx)
        if key not in bins_dict:
            bins_dict[key] = []
        bins_dict[key].append(rect)
    return bins_dict


def _draw_bin(ax, box_idx: int, layer_idx: int, rects_in_bin: list) -> None:
    # Draw a single bin (box + layer) with all its packed rectangles
    # Draw bin boundary
    bin_rect = patches.Rectangle(
        (0, 0), BIN_WIDTH, BIN_HEIGHT,
        linewidth=6, edgecolor='darkblue', facecolor='lightblue', alpha=0.7
    )
    ax.add_patch(bin_rect)
    
    # Select color based on layer for better visibility
    layer_colors = ['lightcoral', 'lightsalmon', 'lightgreen', 'lightpink']
    workpiece_color = layer_colors[layer_idx % len(layer_colors)]
    
    # Draw each packed rectangle in this bin
    for rect in rects_in_bin:
        _, x, y, w, h, workpiece_id = rect
        
        # Draw rectangle with layer-specific color
        rect_patch = patches.Rectangle(
            (x, y), w, h,
            linewidth=1, edgecolor='black', facecolor=workpiece_color
        )
        ax.add_patch(rect_patch)
        
        # Add ID text at center
        ax.text(
            x + w / 2, y + h / 2, str(workpiece_id),
            ha='center', va='center', fontsize=10, weight='bold'
        )
    
    # Configure axes
    ax.set_title(f'Box {box_idx} - Layer {layer_idx}: {len(rects_in_bin)} items')
    ax.set_xlabel('Width [cm]')
    ax.set_ylabel('Height [cm]')
    ax.set_xlim(-10, BIN_WIDTH + 10)
    ax.set_ylim(-10, BIN_HEIGHT + 10)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)


def main():
    # Main entry point for rectangle packing
    packer = setup_packer()
    packer.pack()
    display_results(packer)
    visualize_packing(packer)


if __name__ == "__main__":
    main()
