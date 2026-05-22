# Chapter 12 - Hierarchical Clustering Portfolios

Source: `../../books/Advanced_Portfolio_Optimization/978-3-031-84304-4 (1).pdf`

## Chapter Purpose

This chapter studies portfolio-allocation methods built around hierarchical clustering and dendrogram structure. The core idea is that assets do not only differ by standalone risk and expected return; they also sit inside a hierarchy of relationships. If we can detect that hierarchy, we may be able to allocate capital in a way that is more robust to estimation error than classic mean-variance optimization.

The chapter focuses on three methods:

- HRP: Hierarchical Risk Parity
- HERC: Hierarchical Equal Risk Contribution
- NCO: Nested Clustered Optimization

These methods all start with the same broad intuition:

- assets with similar behavior should be grouped together
- allocation should respect those groups rather than treating the covariance matrix as an unstructured input
- clustering can reduce the influence of noisy pairwise covariance estimates

## Why This Chapter Matters

The book presents hierarchical methods as a response to familiar weaknesses in classic mean-variance optimization:

- covariance estimates are noisy
- optimized portfolios can become fragile and overconcentrated
- small input changes can create large allocation shifts

Hierarchical methods try to solve that by using structure first and optimization second, or in some cases by avoiding a full convex optimization altogether.

## Common Building Blocks

All three methods depend on a few shared ideas.

### 1. Codependence To Distance

The process starts with a codependence or similarity matrix, such as a correlation matrix. That matrix is then converted into a dissimilarity or distance matrix so that clustering algorithms can operate on it.

This step is conceptually important because the whole hierarchy depends on how "closeness" is defined. A different codependence measure can produce a different tree and therefore a different portfolio.

### 2. Hierarchical Clustering

Hierarchical clustering builds a tree-like structure that shows which assets merge first and which groups remain far apart. The output is a linkage matrix, which can be plotted as a dendrogram.

The chapter reviews common linkage rules:

- single linkage
- complete linkage
- average linkage
- weighted linkage
- centroid linkage
- median linkage
- Ward linkage
- DBHT, a graph-based alternative

This matters because the linkage rule is not just a technical footnote. It directly affects the shape of the tree. Some linkages create long chains, others create compact clusters, and those differences propagate into the final allocation.

### 3. Seriation Or Quasi-Diagonalization

Once the dendrogram exists, assets are reordered so that similar assets sit near each other. In covariance-based settings this quasi-diagonalizes the covariance matrix; in scenario-based settings it reorders the return matrix.

The purpose is practical:

- similar assets are brought together
- dissimilar assets are pushed apart
- later splitting steps can operate on ordered blocks rather than on a scrambled asset list

### 4. Recursive Splitting

All three methods eventually use the hierarchical structure to allocate capital across subgroups. The difference is in how they define those subgroups and what optimization happens inside them.

## 12.1 Hierarchical Risk Parity (HRP)

HRP is presented as the foundational method in this family. López de Prado designed it as a more robust alternative to classic mean-variance optimization.

### Why HRP Was Important

The chapter emphasizes several reasons HRP became popular:

- it does not require the covariance matrix to be positive semidefinite
- it can be adapted beyond pure variance-based risk
- it often produces more diversified and more stable allocations than fragile minimum-variance solutions

That first point is more important than it may look. In practice, covariance estimates built from factor models, shrinkage procedures, custom constructions, or blended inputs are not always numerically well behaved. HRP avoids making positive semidefiniteness the central bottleneck.

### HRP Step 1: Hierarchical Clustering

HRP begins by building a dendrogram from the distance matrix. The tree captures nested similarity relationships among assets.

The chapter’s broader message is that this tree is a structural summary of the universe:

- assets that merge early are very similar
- assets that stay separate until late are more distinct

### HRP Step 2: Seriation

The assets are then reordered based on dendrogram leaf order. This places related assets next to one another.

The chapter notes that HRP is highly sensitive to leaf order. This is one of the chapter’s recurring warnings: even if the tree shape is fixed, the exact ordering of leaves can affect the allocation materially.

### HRP Step 3: Recursive Bisection

The portfolio is split recursively:

- start with all assets
- bisect the ordered set into adjacent subsets
- compute risk for each subset
- assign more capital to the lower-risk subset
- repeat until you reach individual assets

Within each subset, the chapter uses a naive risk-parity style local allocation to measure the subset’s risk contribution. This is why HRP is called "risk parity," but the chapter later argues that the final result is not a true equal-risk-contribution portfolio in the strict sense.

### Why HRP Works Intuitively

HRP tries to respect correlation structure before assigning final capital. Instead of solving one global optimization problem that can overreact to noisy inputs, it spreads capital through a hierarchy:

- first across broad groups
- then within subgroups
- then down to assets

This top-down splitting is what gives HRP much of its intuitive appeal.

### HRP Advantages

The author lists several strengths:

- it is more robust than minimum variance in many settings
- it tends to be more diversified
- it can work with nonconvex risk measures because it is not a standard convex optimization problem
- it is useful when covariance estimation is unstable

### HRP Limitations

The chapter is clear that HRP has meaningful drawbacks:

- it is sensitive to the codependence matrix choice
- it is sensitive to linkage choice
- it is sensitive to leaf ordering
- it assigns positive weight to all assets, which is a problem in large universes
- it is long-only in its natural form
- it cannot easily incorporate practical constraints such as linear restrictions or tracking-error controls
- it does not actually use cluster structure deeply; it mostly uses the ordering induced by the tree
- the final portfolio is not a proper equal-risk-contribution portfolio

This is one of the most useful sections of the chapter. It prevents HRP from being treated as a magical cure for optimization instability.

## 12.2 Hierarchical Equal Risk Contribution (HERC)

HERC is presented as an improvement on HRP. The author’s main criticism of HRP is that it largely ignores the actual cluster structure identified by the dendrogram. HERC addresses that by explicitly selecting an optimal number of clusters and using those clusters in the allocation process.

### The Main Upgrade Over HRP

HERC adds a new step:

- determine an optimal number of clusters

This seems small, but conceptually it is a major improvement. It turns the dendrogram from a sorting device into an actual grouping device.

### Optimal Number Of Clusters

The chapter highlights two methods.

#### Standardized Silhouette Score

This measures how well assets sit inside their assigned clusters:

- high values mean assets are close to their own cluster and far from others
- low or negative values mean assets may be poorly grouped

The standardized version gives a single quality score that can be compared across candidate cluster counts.

#### Two-Difference Gap Statistic

This is presented as a computationally simpler alternative to the traditional gap statistic. Instead of using Monte Carlo reference distributions, it uses a second-difference style calculation on within-cluster dispersion.

The practical reason the author likes it is efficiency. It is easier to compute and still provides a disciplined way to choose cluster count.

### HERC Allocation Logic

Once the number of clusters is fixed, HERC performs hierarchical recursive bisection while respecting those clusters. Instead of splitting all the way to leaves in the same way as HRP, it uses the cluster structure as a stopping and grouping mechanism.

The chapter’s description implies the following intuition:

- identify meaningful groups first
- distribute capital across groups based on their aggregate risk
- allocate within groups using a local naive risk-parity style rule

### Why HERC Can Be Better Than HRP

The chapter identifies two main improvements:

- it uses the dendrogram more meaningfully by extracting clusters
- it can be more computationally efficient because the process stops at the cluster level rather than traversing every branch to the bottom in the same way

The author also makes an interesting practical point: once clusters are identified, they can be used as behavioral groupings inside more traditional convex optimization frameworks. That is potentially more informative than using fixed labels such as sector or asset class.

### HERC Limitations

The chapter still sees limitations:

- it is not a proper risk parity portfolio because risk contributions are still uneven
- it can become concentrated when the linkage method creates poor or chain-like clusters
- it is still not a fully general constrained optimization framework

So HERC improves structural awareness, but it does not fully solve the limitations of heuristic hierarchical allocation.

## 12.3 Nested Clustered Optimization (NCO)

NCO is the chapter’s most flexible and arguably most modern method. It tries to combine clustering structure with actual convex optimization.

### Core Idea

NCO proceeds in two stages:

- optimize within clusters
- optimize across clusters

The final asset weights are the product of intra-cluster and inter-cluster weights.

This makes NCO fundamentally different from HRP and HERC. It is not just a tree-based splitting heuristic. It is a framework for decomposing a hard global portfolio problem into a hierarchy of smaller optimization problems.

### Intra-Cluster Optimization

Within each cluster, the user solves an optimization problem using the convex models developed earlier in the book. That means different clusters can in principle use:

- different objectives
- different constraints
- different risk measures

This is the most important conceptual bridge in the chapter. It links the clustering world of Chapter 12 to the objective-function and constraint framework from Chapters 7 through 11.

### Inter-Cluster Optimization

Once each cluster has its own optimized portfolio, those cluster portfolios are treated like meta-assets. A second optimization allocates across them.

The author interprets this as a way to reduce noise:

- assets inside a cluster are similar and handled locally
- cluster portfolios should be less codependent with one another
- the top-level problem may therefore be cleaner than one giant one-shot optimization

### NCO Advantages

The book sees NCO as a major improvement because:

- it can incorporate classic objective functions
- it can incorporate realistic convex constraints
- it allows more customization than HRP or HERC
- it preserves cluster structure while still using formal optimization

This is the chapter’s most useful method if the reader wants both structure and control.

### NCO Weakness

The author’s main criticism is subtle but important: if the same objective is used both within clusters and across clusters, the result can end up looking very similar to a one-step convex optimization on the full universe.

In other words, NCO can reintroduce concentration if the optimization logic dominates the clustering logic. The clustering layer does not automatically guarantee diversification.

The chapter also notes a practical failure mode:

- if the same constraints are applied mechanically to every cluster, some clusters may have infeasible subproblems
- one infeasible cluster can stop the whole procedure

So NCO is flexible, but it requires more design discipline than HRP or HERC.

## How The Three Methods Compare

### HRP

- simplest and most famous
- robust relative to mean-variance
- no need for a PSD covariance matrix
- heuristic rather than full optimization
- weak support for realistic constraints

### HERC

- structurally smarter than HRP
- explicitly uses cluster count and cluster membership
- can improve computational efficiency
- still heuristic and still not true equal-risk contribution

### NCO

- most flexible
- best connection to formal convex portfolio optimization
- supports customized objectives and constraints
- can drift back toward concentrated one-step optimization if not designed carefully

## Broader Interpretation

The chapter’s real contribution is not just three named algorithms. It is the idea that diversification can be organized hierarchically rather than only algebraically.

Traditional optimization says:

- estimate means and covariances
- solve one large optimization problem

Hierarchical methods say:

- first understand who is related to whom
- then allocate in a way that respects that structure

That is a different philosophy. It tends to be more appealing when:

- covariance estimates are unstable
- the asset universe is broad and heterogeneous
- the manager wants structural diversification instead of purely numerical diversification

## Practical Takeaways

- HRP is a good first-pass robust allocator when you do not need complex constraints.
- HERC is better when cluster identity itself matters and you want the dendrogram to do more than impose an ordering.
- NCO is the best choice when you want clustering plus real optimization logic.
- None of these methods eliminate the need to think carefully about codependence metrics, linkage functions, and cluster stability.
- If cluster structure is unstable across windows, the resulting portfolios will also be unstable, even if the methods seem sophisticated.

## Bottom Line

Chapter 12 argues that portfolio construction can be improved by using the hierarchical relationships among assets instead of relying only on a flat covariance matrix. HRP introduced that idea in a simple and robust form. HERC made it more structurally faithful by using cluster counts explicitly. NCO then connected clustering to the broader optimization toolkit of the book. The chapter is strongest when read as a progression:

- HRP shows the intuition
- HERC improves the hierarchy
- NCO restores optimization flexibility

That progression is the main intellectual arc of the chapter.
