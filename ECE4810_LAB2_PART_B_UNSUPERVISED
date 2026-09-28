import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (silhouette_score, davies_bouldin_score,
                              adjusted_rand_score, normalized_mutual_info_score)

np.random.seed(42)

OUT_DIR = "analysis_output"
import os
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------
# 1. Load data and REMOVE the labels (unsupervised setting)
# ---------------------------------------------------------------
# FIX: script previously hardcoded a Windows-only absolute path, which
# contradicted the handoff note ("run in same folder as the .xlsx, or
# pass its path as an argument"). It now actually accepts an argument.
data_path = sys.argv[1] if len(sys.argv) > 1 else "pedestrian_windows_despiked.xlsx"
df = pd.read_excel(data_path)
true_labels = df["NextWindowState"].copy()          # kept ONLY for post-hoc comparison
feat_cols = ["d1", "d2", "d3", "d4", "d5"]
X_raw = df[feat_cols].copy()                          # unlabeled, 5-feature window

print("Feature matrix shape:", X_raw.shape)
print("Features used:", feat_cols)

# ---------------------------------------------------------------
# 2. IMPROVEMENT: engineer two features that summarise the window
#    instead of feeding K-Means 5 noisy, highly-correlated raw readings.
#      - mean_dist   : overall distance level over the window
#      - trend_slope : linear-regression slope across d1..d5 (rate of
#                       approach/departure), the piece the raw features
#                       encode only implicitly and very noisily
# ---------------------------------------------------------------
x_idx = np.arange(len(feat_cols))

def window_slope(row):
    return np.polyfit(x_idx, row.values.astype(float), 1)[0]

df["mean_dist"] = X_raw.mean(axis=1)
df["trend_slope"] = X_raw.apply(window_slope, axis=1)

FEATURE_SETS = {
    "raw_5d":            feat_cols,
    "engineered_2d":      ["mean_dist", "trend_slope"],
    "raw_plus_engineered": feat_cols + ["mean_dist", "trend_slope"],
}

# ---------------------------------------------------------------
# 3. Vary K for every feature set: Elbow (inertia), Silhouette, DB
# ---------------------------------------------------------------
K_range = list(range(2, 11))
all_metrics = {}

for set_name, cols in FEATURE_SETS.items():
    X = StandardScaler().fit_transform(df[cols])

    inertias, sil_scores, db_scores = [], [], []
    for k in K_range:
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        labels_k = km.fit_predict(X)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X, labels_k))
        db_scores.append(davies_bouldin_score(X, labels_k))

    km1 = KMeans(n_clusters=1, n_init=10, random_state=42).fit(X)
    inertia_full = [km1.inertia_] + inertias
    K_full = [1] + K_range

    metrics_table = pd.DataFrame({
        "K": K_range, "Inertia": inertias,
        "Silhouette": sil_scores, "Davies-Bouldin": db_scores
    })
    metrics_table.to_csv(f"{OUT_DIR}/k_metrics_{set_name}.csv", index=False)
    all_metrics[set_name] = {"K_full": K_full, "inertia_full": inertia_full,
                              "sil_scores": sil_scores, "db_scores": db_scores,
                              "best_k_by_silhouette": K_range[int(np.argmax(sil_scores))]}
    print(f"\n[{set_name}] best K by silhouette = {all_metrics[set_name]['best_k_by_silhouette']}")
    print(metrics_table)

# --- Elbow plot: raw vs engineered, side by side ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, set_name in zip(axes, ["raw_5d", "engineered_2d"]):
    m = all_metrics[set_name]
    ax.plot(m["K_full"], m["inertia_full"], marker="o", color="#2563eb")
    ax.set_xlabel("Number of clusters (K)")
    ax.set_ylabel("Inertia (WCSS)")
    ax.set_title(f"Elbow Method — {set_name}")
    ax.set_xticks(m["K_full"])
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/ElbowPlot_comparison.png")
plt.close()

# --- Silhouette plot: raw vs engineered vs combined, overlaid ---
plt.figure(figsize=(7.5, 5.5))
colors = {"raw_5d": "#94a3b8", "engineered_2d": "#16a34a", "raw_plus_engineered": "#2563eb"}
for set_name in FEATURE_SETS:
    m = all_metrics[set_name]
    plt.plot(K_range, m["sil_scores"], marker="o", color=colors[set_name], label=set_name)
plt.axvline(4, color="red", linestyle="--", alpha=0.5, label="true class count (4)")
plt.xlabel("Number of clusters (K)")
plt.ylabel("Average Silhouette Score")
plt.title("Silhouette Score vs K — raw vs. engineered features")
plt.xticks(K_range)
plt.legend(fontsize=8)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/SilhouettePlot_comparison.png")
plt.close()

# ---------------------------------------------------------------
# 4. Fit K-Means at several K per feature set, compare to TRUE labels
#    (post-hoc, for comparison only — never used in fitting)
# ---------------------------------------------------------------
K_to_compare = [2, 3, 4, 5, 6]
compare_rows = []
cluster_label_maps = {}   # (set_name, k) -> cluster ids, kept for K=4 plots below

for set_name, cols in FEATURE_SETS.items():
    X = StandardScaler().fit_transform(df[cols])
    for k in K_to_compare:
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42)
        cluster_ids = km.fit_predict(X)
        ari = adjusted_rand_score(true_labels, cluster_ids)
        nmi = normalized_mutual_info_score(true_labels, cluster_ids)
        sil = silhouette_score(X, cluster_ids)
        compare_rows.append({"FeatureSet": set_name, "K": k, "ARI": ari, "NMI": nmi, "Silhouette": sil})
        cluster_label_maps[(set_name, k)] = cluster_ids

        if k == 4:
            ct = pd.crosstab(pd.Series(cluster_ids, name="Cluster"),
                              pd.Series(true_labels.values, name="TrueLabel"))
            ct.to_csv(f"{OUT_DIR}/crosstab_{set_name}_k4.csv")

compare_df = pd.DataFrame(compare_rows)
compare_df.to_csv(f"{OUT_DIR}/cluster_vs_label_metrics.csv", index=False)
print("\nFull comparison (all feature sets, K=2..6):")
print(compare_df)

# ---------------------------------------------------------------
# 5. Visualise clusters (PCA 2D, fit on raw features for a common view)
#    for K=4: true labels vs raw-feature clusters vs engineered-feature clusters
# ---------------------------------------------------------------
X_raw_scaled = StandardScaler().fit_transform(df[feat_cols])
pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_raw_scaled)
print("\nPCA explained variance ratio (raw features):", pca.explained_variance_ratio_,
      "sum:", pca.explained_variance_ratio_.sum())

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))

label_to_int = {lab: i for i, lab in enumerate(sorted(true_labels.unique()))}
true_int = true_labels.map(label_to_int).values
axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=true_int, cmap="tab10", s=5, alpha=0.6)
axes[0].set_title("Ground-truth NextWindowState\n(Lab 2 supervised labels)")
handles = [plt.Line2D([0], [0], marker='o', color='w',
           markerfacecolor=plt.cm.tab10(v / max(1, len(label_to_int)-1)), markersize=8)
           for v in label_to_int.values()]
axes[0].legend(handles, label_to_int.keys(), fontsize=8, loc="best")

axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_label_maps[("raw_5d", 4)], cmap="tab10", s=5, alpha=0.6)
axes[1].set_title("K-Means clusters, K=4\n(raw 5-D features)")

axes[2].scatter(X_pca[:, 0], X_pca[:, 1], c=cluster_label_maps[("raw_plus_engineered", 4)], cmap="tab10", s=5, alpha=0.6)
axes[2].set_title("K-Means clusters, K=4\n(raw + engineered: d1..d5 + mean_dist + trend_slope)")

for ax in axes:
    ax.set_xlabel("PC1 (of raw features)")
    ax.set_ylabel("PC2 (of raw features)")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig_pca_grid_comparison.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 6. Cluster size distribution at K=4: true vs raw vs raw+engineered
# ---------------------------------------------------------------
true_sizes = true_labels.value_counts()
raw_sizes = pd.Series(cluster_label_maps[("raw_5d", 4)]).value_counts().sort_index()
combo_sizes = pd.Series(cluster_label_maps[("raw_plus_engineered", 4)]).value_counts().sort_index()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].bar(true_sizes.index.astype(str), true_sizes.values, color="#f59e0b")
axes[0].set_title("True class distribution\n(supervised labels, Lab 2)")
axes[0].set_ylabel("Number of samples")
axes[0].tick_params(axis='x', rotation=30)

axes[1].bar(raw_sizes.index.astype(str), raw_sizes.values, color="#94a3b8")
axes[1].set_title("K-Means cluster sizes, K=4\n(raw features)")
axes[1].set_xlabel("Cluster ID")

axes[2].bar(combo_sizes.index.astype(str), combo_sizes.values, color="#2563eb")
axes[2].set_title("K-Means cluster sizes, K=4\n(raw + engineered features)")
axes[2].set_xlabel("Cluster ID")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/fig_distribution_compare.png", dpi=150)
plt.close()

print(f"\nAll outputs written to ./{OUT_DIR}/")
