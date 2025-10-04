import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file with your experimental data
df = pd.read_csv('task_c_results_corrected.csv')

# Group by configuration and compute averages
grouped = df.groupby(['size', 'density', 'graph_type', 'mst_algo'])['runtime'].median().reset_index()

# Create figure with adjusted layout (3 rows, 3 columns)
fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

# Define colors for consistency
colors = {
    ('matrix', 'prims'): '#1f77b4',
    ('matrix', 'kruskals'): '#ff7f0e',
    ('list', 'prims'): '#2ca02c',
    ('list', 'kruskals'): '#d62728'
}

labels = {
    ('matrix', 'prims'): 'matrix+prims',
    ('matrix', 'kruskals'): 'matrix+kruskals',
    ('list', 'prims'): 'list+prims',
    ('list', 'kruskals'): 'list+kruskals'
}

markers = {
    ('matrix', 'prims'): 'o',
    ('matrix', 'kruskals'): 's',
    ('list', 'prims'): '^',
    ('list', 'kruskals'): 'd'
}

# ============================================
# ROW 1: Runtime vs Size for different densities
# ============================================

# Panel 1: Sparse (0%)
ax1 = fig.add_subplot(gs[0, 0])
sparse_data = grouped[grouped['density'] == 0]

for (graph_type, algo), color in colors.items():
    data = sparse_data[(sparse_data['graph_type'] == graph_type) &
                       (sparse_data['mst_algo'] == algo)]
    data = data.sort_values('size')
    ax1.plot(data['size'], data['runtime'] * 1000,
             marker=markers[(graph_type, algo)], linewidth=2.5, markersize=8,
             color=color, label=labels[(graph_type, algo)])

ax1.set_xlabel('n (maze size n×n)', fontsize=11)
ax1.set_ylabel('Runtime (milliseconds)', fontsize=11)
ax1.set_title('Runtime vs Size: Sparse (density = 0%)', fontsize=12, fontweight='bold')
ax1.set_yscale('log')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_facecolor('#fafafa')

# Panel 2: Medium (50%)
ax2 = fig.add_subplot(gs[0, 1])
medium_data = grouped[grouped['density'] == 50]

for (graph_type, algo), color in colors.items():
    data = medium_data[(medium_data['graph_type'] == graph_type) &
                       (medium_data['mst_algo'] == algo)]
    data = data.sort_values('size')
    ax2.plot(data['size'], data['runtime'] * 1000,
             marker=markers[(graph_type, algo)], linewidth=2.5, markersize=8,
             color=color, label=labels[(graph_type, algo)])

ax2.set_xlabel('n (maze size n×n)', fontsize=11)
ax2.set_ylabel('Runtime (milliseconds)', fontsize=11)
ax2.set_title('Runtime vs Size: Medium (density = 50%)', fontsize=12, fontweight='bold')
ax2.set_yscale('log')
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_facecolor('#fafafa')

# Panel 3: Dense (100%)
ax3 = fig.add_subplot(gs[0, 2])
dense_data = grouped[grouped['density'] == 100]

for (graph_type, algo), color in colors.items():
    data = dense_data[(dense_data['graph_type'] == graph_type) &
                      (dense_data['mst_algo'] == algo)]
    data = data.sort_values('size')
    ax3.plot(data['size'], data['runtime'] * 1000,
             marker=markers[(graph_type, algo)], linewidth=2.5, markersize=8,
             color=color, label=labels[(graph_type, algo)])

ax3.set_xlabel('n (maze size n×n)', fontsize=11)
ax3.set_ylabel('Runtime (milliseconds)', fontsize=11)
ax3.set_title('Runtime vs Size: Dense (density = 100%)', fontsize=12, fontweight='bold')
ax3.set_yscale('log')
ax3.legend(loc='upper left', fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.set_facecolor('#fafafa')

# ============================================
# ROW 2 & 3: Runtime vs Density for sizes 10, 50, 100
# ============================================

sizes_to_plot = [10, 50, 100]
positions = [(1, 0), (1, 1), (1, 2)]

for idx, size in enumerate(sizes_to_plot):
    row, col = positions[idx]
    ax = fig.add_subplot(gs[row, col])
    size_data = grouped[grouped['size'] == size]

    for (graph_type, algo), color in colors.items():
        data = size_data[(size_data['graph_type'] == graph_type) &
                       (size_data['mst_algo'] == algo)]
        data = data.sort_values('density')
        ax.plot(data['density'], data['runtime'] * 1000,
               marker=markers[(graph_type, algo)], linewidth=2.5, markersize=8,
               color=color, label=labels[(graph_type, algo)])

    ax.set_xlabel('Edge Density (% walls removed)', fontsize=11)
    ax.set_ylabel('Runtime (milliseconds)', fontsize=11)
    ax.set_title(f'Runtime vs Density: {size}×{size} maze', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#fafafa')
    ax.set_xticks([0, 25, 50, 75, 100])

# ============================================
# Panel for comparison bar chart at size 100
# ============================================
ax_bar = fig.add_subplot(gs[2, :])
size_100 = grouped[grouped['size'] == 100]

# Prepare data for bar chart
sparse_100 = size_100[size_100['density'] == 0]
dense_100 = size_100[size_100['density'] == 100]

bar_labels = []
bar_values = []
bar_colors = []

for graph_type in ['matrix', 'list']:
    for algo in ['prims', 'kruskals']:
        # Sparse
        vals = sparse_100[(sparse_100['graph_type'] == graph_type) &
                        (sparse_100['mst_algo'] == algo)]['runtime'].values
        if len(vals) > 0:
            val = vals[0] * 1000
            bar_labels.append(f'Sparse\n{graph_type[0].upper()}+{algo[0].upper()}')
            bar_values.append(val)
            bar_colors.append(colors[(graph_type, algo)])

for graph_type in ['matrix', 'list']:
    for algo in ['prims', 'kruskals']:
        # Dense
        vals = dense_100[(dense_100['graph_type'] == graph_type) &
                       (dense_100['mst_algo'] == algo)]['runtime'].values
        if len(vals) > 0:
            val = vals[0] * 1000
            bar_labels.append(f'Dense\n{graph_type[0].upper()}+{algo[0].upper()}')
            bar_values.append(val)
            bar_colors.append(colors[(graph_type, algo)])

x_pos = np.arange(len(bar_labels))
bars = ax_bar.bar(x_pos, bar_values, color=bar_colors, edgecolor='black', linewidth=1.5, width=0.7)

ax_bar.set_xlabel('Algorithm Configuration', fontsize=11)
ax_bar.set_ylabel('Runtime (milliseconds)', fontsize=11)
ax_bar.set_title('Performance Comparison at 100×100 maze', fontsize=12, fontweight='bold')
ax_bar.set_xticks(x_pos)
ax_bar.set_xticklabels(bar_labels, fontsize=9)
ax_bar.grid(True, alpha=0.3, axis='y')
ax_bar.set_facecolor('#fafafa')

# Add value labels on bars
for i, (bar, val) in enumerate(zip(bars, bar_values)):
    height = bar.get_height()
    ax_bar.text(bar.get_x() + bar.get_width()/2., height * 1.05,
               f'{val:.0f}ms',
               ha='center', va='bottom', fontsize=8)

# Overall title
fig.suptitle('Comprehensive MST Algorithm Performance Analysis',
             fontsize=16, fontweight='bold', y=0.995)

# Adjust layout to avoid warnings
plt.tight_layout(rect=[0, 0, 1, 0.99])

# Save the figure
plt.savefig('mst_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Comprehensive plot saved as 'mst_comprehensive_analysis.png'")

# Show the plot
plt.show()

# ============================================
# Print Summary Statistics
# ============================================
print("\n" + "="*80)
print("COMPREHENSIVE SUMMARY STATISTICS")
print("="*80)

print("\n" + "-"*80)
print("RUNTIME VS DENSITY ANALYSIS")
print("-"*80)

for size in [10, 20, 30, 50, 100]:
    print(f"\n{'='*40}")
    print(f"SIZE {size}×{size} MAZE")
    print(f"{'='*40}")
    print(f"{'Density':<10} | {'M+P':<10} | {'M+K':<10} | {'L+P':<10} | {'L+K':<10}")
    print("-" * 60)

    for density in [0, 25, 50, 75, 100]:
        size_dens_data = grouped[(grouped['size'] == size) & (grouped['density'] == density)]

        mp = size_dens_data[(size_dens_data['graph_type'] == 'matrix') &
                           (size_dens_data['mst_algo'] == 'prims')]['runtime'].values
        mk = size_dens_data[(size_dens_data['graph_type'] == 'matrix') &
                           (size_dens_data['mst_algo'] == 'kruskals')]['runtime'].values
        lp = size_dens_data[(size_dens_data['graph_type'] == 'list') &
                           (size_dens_data['mst_algo'] == 'prims')]['runtime'].values
        lk = size_dens_data[(size_dens_data['graph_type'] == 'list') &
                           (size_dens_data['mst_algo'] == 'kruskals')]['runtime'].values

        mp_val = f"{mp[0]*1000:.1f}ms" if len(mp) > 0 else "N/A"
        mk_val = f"{mk[0]*1000:.1f}ms" if len(mk) > 0 else "N/A"
        lp_val = f"{lp[0]*1000:.1f}ms" if len(lp) > 0 else "N/A"
        lk_val = f"{lk[0]*1000:.1f}ms" if len(lk) > 0 else "N/A"

        print(f"{density}%{' ':<7} | {mp_val:<10} | {mk_val:<10} | {lp_val:<10} | {lk_val:<10}")

print("\n" + "="*80)
print("KEY OBSERVATIONS")
print("="*80)

# Calculate speedups at size 100
sparse_100 = grouped[(grouped['size'] == 100) & (grouped['density'] == 0)]
dense_100 = grouped[(grouped['size'] == 100) & (grouped['density'] == 100)]

mp_sparse = sparse_100[(sparse_100['graph_type'] == 'matrix') &
                      (sparse_100['mst_algo'] == 'prims')]['runtime'].values
lk_sparse = sparse_100[(sparse_100['graph_type'] == 'list') &
                      (sparse_100['mst_algo'] == 'kruskals')]['runtime'].values

mp_dense = dense_100[(dense_100['graph_type'] == 'matrix') &
                    (dense_100['mst_algo'] == 'prims')]['runtime'].values
lk_dense = dense_100[(dense_100['graph_type'] == 'list') &
                    (dense_100['mst_algo'] == 'kruskals')]['runtime'].values

print(f"\nAt 100×100 maze:")
if len(mp_sparse) > 0 and len(lk_sparse) > 0:
    sparse_speedup = (mp_sparse[0] * 1000) / (lk_sparse[0] * 1000)
    print(f"  Sparse (0% density): Matrix+Prims is {sparse_speedup:.1f}× slower than List+Kruskals")
    print(f"    Matrix+Prims: {mp_sparse[0]*1000:.1f}ms")
    print(f"    List+Kruskals: {lk_sparse[0]*1000:.1f}ms")

if len(mp_dense) > 0 and len(lk_dense) > 0:
    dense_speedup = (mp_dense[0] * 1000) / (lk_dense[0] * 1000)
    print(f"  Dense (100% density): Matrix+Prims is {dense_speedup:.1f}× slower than List+Kruskals")
    print(f"    Matrix+Prims: {mp_dense[0]*1000:.1f}ms")
    print(f"    List+Kruskals: {lk_dense[0]*1000:.1f}ms")

print("\n" + "="*80)
