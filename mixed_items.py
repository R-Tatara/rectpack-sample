from rectpack import newPacker, PackingMode, PackingBin, SORT_AREA
from rectpack.maxrects import MaxRectsBl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

# Bin dimensions (cm)
BIN_WIDTH, BIN_HEIGHT = 69, 51

# Workpiece definitions (width, height in cm, number per bin, display color)
WORKPIECES = {
    "A": {"width": 14, "height": 11, "num_per_bin": 4, "color": "lightcoral"},
    "B": {"width": 20, "height": 15, "num_per_bin": 2, "color": "lightgreen"},
    "C": {"width": 16, "height": 10, "num_per_bin": 9, "color": "lightblue"},
}


def setup_packer():
    # Create packer with single bin configuration
    packer = newPacker(
        mode=PackingMode.Offline,
        bin_algo=PackingBin.BBF,
        pack_algo=MaxRectsBl,
        sort_algo=SORT_AREA,
        rotation=True
    )

    for workpiece_type, specs in WORKPIECES.items():
        for i in range(specs["num_per_bin"]):
            packer.add_rect(
                specs["width"], 
                specs["height"], 
                rid=f"{workpiece_type}-{i}"
            )

    # Add single bin
    packer.add_bin(BIN_WIDTH, BIN_HEIGHT)

    return packer


def display_results(packer):
    # Show packing results for single bin
    all_rects = packer.rect_list()
    
    if not all_rects:
        print("No packing results available")
        return
    
    print(f"\nBin 0: {len(all_rects)} items")
    
    # Group by workpiece type
    by_type = {}
    for rect in all_rects:
        bin_idx, x, y, w, h, workpiece_id = rect
        workpiece_type = workpiece_id.split("-")[0]
        if workpiece_type not in by_type:
            by_type[workpiece_type] = []
        by_type[workpiece_type].append(rect)
    
    # Display grouped by type
    for workpiece_type in sorted(by_type.keys()):
        print(f"  Type {workpiece_type}: {len(by_type[workpiece_type])} items")
        for rect in by_type[workpiece_type]:
            bin_idx, x, y, w, h, workpiece_id = rect
            print(f"    ID:{workpiece_id} position: ({x},{y}) size: {w}x{h}")


def visualize_packing(packer):
    # Visualize packing results with matplotlib
    all_rects = packer.rect_list()
    
    if not all_rects:
        print("No packing results available")
        return
    
    # Create single subplot
    fig, ax = plt.subplots(figsize=(8, 6))
    
    _draw_bin(ax, all_rects)
    
    plt.tight_layout()
    plt.show()


def _draw_bin(ax, rects_in_bin: list) -> None:
    # Draw a single bin with all its packed rectangles
    # Draw bin boundary
    bin_rect = patches.Rectangle(
        (0, 0), BIN_WIDTH, BIN_HEIGHT,
        linewidth=6, edgecolor='darkblue', facecolor='lightblue', alpha=0.7
    )
    ax.add_patch(bin_rect)
    
    # Track which types are drawn for legend
    drawn_types = set()
    
    # Draw each packed rectangle in this bin
    for rect in rects_in_bin:
        _, x, y, w, h, workpiece_id = rect
        
        # Extract workpiece type from ID (e.g., "A-0" -> "A")
        workpiece_type = workpiece_id.split("-")[0]
        color = WORKPIECES[workpiece_type]["color"]
        
        # Draw rectangle with type-specific color
        rect_patch = patches.Rectangle(
            (x, y), w, h,
            linewidth=1, edgecolor='black', facecolor=color,
            label=f'Type {workpiece_type}' if workpiece_type not in drawn_types else ''
        )
        ax.add_patch(rect_patch)
        drawn_types.add(workpiece_type)
        
        # Add ID text at center
        ax.text(
            x + w / 2, y + h / 2, str(workpiece_id),
            ha='center', va='center', fontsize=10, weight='bold'
        )
    
    # Configure axes
    ax.set_title(f'Bin 0: {len(rects_in_bin)} items')
    ax.set_xlabel('Width [cm]')
    ax.set_ylabel('Height [cm]')
    ax.set_xlim(-10, BIN_WIDTH + 10)
    ax.set_ylim(-10, BIN_HEIGHT + 10)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)


def verify_packing(packer) -> None:
    # Verify all workpieces were successfully packed
    expected_count = sum(specs["num_per_bin"] for specs in WORKPIECES.values())
    packed_count = len(packer.rect_list())
    
    if packed_count < expected_count:
        unpacked_count = expected_count - packed_count
        print(f"\nError: {unpacked_count} workpieces could not fit in the bin.")
        print(f"Expected count: {expected_count}")
        print(f"Packed count: {packed_count}")
        sys.exit(1)


def main():
    # Main entry point for rectangle packing
    packer = setup_packer()
    packer.pack()
    verify_packing(packer)
    display_results(packer)
    visualize_packing(packer)


if __name__ == "__main__":
    main()
