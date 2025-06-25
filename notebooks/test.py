# %%
import matplotlib.pyplot as plt
import numpy as np
from sentence_transformers import SentenceTransformer

# %%
sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode(sentences)

# (idx, vec)
print(embeddings.shape)

# %%
sen = "Database example here, converted sentence."
sen_enc = model.encode(sen)
distances = np.linalg.norm(embeddings - sen_enc, axis=1)
idx = np.argmin(distances)
dist = distances[idx]

print(f"{idx}, {dist}")

# %%
embeddings = np.vstack([embeddings, sen_enc[np.newaxis, :]])
print(embeddings.shape)


# %%
def pca_numpy(X, num_components):
    # Step 1: Center the data
    X_meaned = X - np.mean(X, axis=0)

    # Step 2: Covariance matrix
    cov_matrix = np.cov(X_meaned, rowvar=False)

    # Step 3: Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(
        cov_matrix
    )  # 'eigh' is for symmetric matrices

    # Step 4: Sort eigenvectors by descending eigenvalues
    sorted_idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sorted_idx]
    eigenvectors = eigenvectors[:, sorted_idx]

    # Step 5: Select top components
    eigenvectors_subset = eigenvectors[:, :num_components]

    # Step 6: Transform the data
    X_reduced = np.dot(X_meaned, eigenvectors_subset)

    return X_reduced, eigenvalues[:num_components], eigenvectors_subset


X_pca, eigvals, eigvecs = pca_numpy(embeddings, num_components=2)
print("Reduced shape:", X_pca.shape)
print("Explained variance", eigvals / np.sum(eigvals))

# %%
all_sentences = sentences + [sen]

plt.figure(figsize=(8, 6))
plt.scatter(
    X_pca[:-1, 0], X_pca[:-1, 1], label="Original sentences", color="blue"
)
plt.scatter(
    X_pca[-1, 0],
    X_pca[-1, 1],
    label="Query sentence",
    color="red",
    marker="x",
    s=100,
)

# Annotate each point with its sentence
for i, txt in enumerate(all_sentences):
    plt.annotate(txt, (X_pca[i, 0], X_pca[i, 1]), fontsize=8, alpha=0.7)

plt.title("PCA of Sentence Embeddings")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend()
plt.tight_layout()
plt.show()
