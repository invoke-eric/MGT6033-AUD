# Quiz Questions

## Section 1: Data Preparation and Feature Engineering

1. **(Easy)** Which vectorizer is used to generate the document-term matrix (DTM) for clustering in Demo 5B?  
A. CountVectorizer  
B. TfidfVectorizer  
C. HashingVectorizer  
D. DictVectorizer  

2. **(Medium) Select all that apply:** What are the key parameters set for the TfidfVectorizer in this demo?  
A. token_pattern = r'\b[a-zA-Z]{3,}\b'  
B. stop_words includes custom tokens like "xxxx"  
C. ngram_range = (1,2)  
D. max_features = 1000  
E. use_idf = False  

3. **(Medium)** Why is it acceptable to use TF-IDF weighting for clustering but not for LDA topic modeling?  
A. Clustering algorithms do not require integer counts  
B. LDA requires integer word counts for probabilistic modeling  
C. TF-IDF always improves LDA  
D. Clustering only works with binary features  

4. **(Hard) Select all that apply:** What are the main challenges of clustering high-dimensional textual data?  
A. Curse of dimensionality  
B. Sparsity of data  
C. Scale differences between features  
D. Lack of stopword removal  

5. **(Hard)** What is the effect of standardizing features before clustering?  
A. Each feature has mean zero and standard deviation one  
B. All features are converted to binary  
C. The number of clusters increases  
D. The DTM becomes denser  

## Section 2: K-means Clustering and Cluster Evaluation

6. **(Easy)** What is the primary parameter that must be set when fitting a K-means model?  
A. Number of clusters (n_clusters)  
B. Distance metric  
C. Number of features  
D. Batch size  

7. **(Medium) Select all that apply:** What are typical ways to evaluate the distribution of cluster assignments in K-means?  
A. value_counts() on cluster labels  
B. Reviewing the number of points per cluster  
C. Examining the most and least populous clusters  
D. Counting the number of unique words  

8. **(Medium)** What does the silhouette score measure in clustering evaluation?  
A. How well each point fits within its assigned cluster compared to others  
B. The number of clusters  
C. The average word frequency  
D. The number of features per cluster  

9. **(Hard) Select all that apply:** Which methods are used to interpret the meaning of clusters in K-means?  
A. Examining most prevalent words in each cluster  
B. Identifying features most dissimilar from other clusters  
C. Finding the document closest to each cluster center  
D. Counting the number of clusters  

10. **(Hard)** Why is it useful to standardize cluster centers before identifying influential words?  
A. To compare feature importance across clusters on a common scale  
B. To remove all negative values  
C. To convert all features to binary  
D. To increase the number of clusters  

## Section 3: Dimension Reduction and PCA

11. **(Easy)** What is the primary purpose of applying PCA before clustering?  
A. Reduce the number of features while retaining most variance  
B. Increase the number of clusters  
C. Remove all stopwords  
D. Normalize the DTM  

12. **(Medium) Select all that apply:** What are common criteria for selecting the number of principal components to retain in PCA?  
A. Eigenvalues greater than 1  
B. Cumulative explained variance threshold (e.g., 75%)  
C. Fixed number of components  
D. Minimum word frequency  

13. **(Medium)** What is the effect of standardizing the PCA-transformed matrix before clustering?  
A. Each component has mean zero and standard deviation one  
B. The number of clusters is fixed  
C. All features are converted to binary  
D. The DTM becomes sparser  

14. **(Hard) Select all that apply:** What information can be obtained from the explained_variance_ratio_ attribute in sklearn’s PCA?  
A. Proportion of variance explained by each component  
B. Cumulative variance explained  
C. Which components to retain  
D. The number of clusters  

15. **(Hard)** Why might you want to retain principal components explaining up to 75% of variance?  
A. To balance dimensionality reduction with information retention  
B. To guarantee perfect clustering  
C. To maximize the number of clusters  
D. To remove all rare words  

## Section 4: HDBSCAN, UMAP, and Advanced Clustering

16. **(Easy)** What does HDBSCAN label as “-1” in its cluster assignments?  
A. Noise points  
B. The largest cluster  
C. Outliers only in PCA  
D. The first cluster  

17. **(Medium) Select all that apply:** What are the key parameters for tuning HDBSCAN?  
A. cluster_selection_method  
B. min_cluster_size  
C. min_samples  
D. cluster_selection_epsilon  
E. n_init  

18. **(Medium)** Why does HDBSCAN often classify a large percentage of points as noise in high-dimensional data?  
A. High-dimensional data is sparse, so many points appear unique  
B. HDBSCAN only works with binary features  
C. It requires integer counts  
D. It always produces balanced clusters  

19. **(Hard) Select all that apply:** What are recommended strategies for evaluating HDBSCAN results?  
A. Proportion of points classified as noise  
B. Number of clusters  
C. Maximum and standard deviation of cluster sizes  
D. Number of clusters at minimum size  

20. **(Hard)** Why is UMAP often preferred over PCA for dimensionality reduction before density-based clustering?  
A. UMAP preserves local structure and relationships better  
B. UMAP always produces fewer clusters  
C. PCA is not supported in sklearn  
D. UMAP removes all outliers  

---

