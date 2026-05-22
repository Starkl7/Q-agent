# Chapter 13 - Graph Theory-Based Portfolios

Source: `../../books/Advanced_Portfolio_Optimization/978-3-031-84304-4 (1).pdf`

## Chapter Purpose

This chapter shows how graph structure can be translated into portfolio constraints. The central idea is that diversification should not be measured only by covariance or standalone risk contribution. It should also reflect where assets sit inside a network of relationships.

The chapter uses two related structures:

- graphs such as MST and TMFG built from asset relationships
- dendrogram-derived cluster networks built from hierarchical clustering

The goal is not to replace portfolio optimization. The goal is to enrich it with structural information that standard mean-risk formulations usually ignore.

## Big Picture

The chapter builds an argument in stages:

1. represent asset relationships as graphs
2. quantify how central or connected each asset is
3. define portfolio-level measures of connectedness and relatedness
4. turn those measures into optimization constraints

This is one of the most practically interesting chapters in the book because it turns network intuition into explicit optimization objects.

## 13.1 Constraints On Graphs

### Basic Graph Concepts

The chapter briefly reviews standard graph ideas:

- undirected and directed graphs
- connected graphs
- complete graphs
- weighted graphs
- spanning trees

This review matters because financial networks are usually built as weighted, undirected graphs, and many of the later constraints depend on how adjacency is represented in matrix form.

### Adjacency Matrix

The first major tool is the adjacency matrix. This is the bridge from visualization to optimization.

Why it matters:

- a graph drawing is intuitive but not directly usable in a solver
- an adjacency matrix can be embedded in linear, integer, or semidefinite constraints

The chapter also emphasizes a deeper property: powers of the adjacency matrix count walks of different lengths between nodes. That leads to connection matrices that say not only whether two assets are directly linked, but whether they are linked through short paths.

### Connection Matrices

This is a key idea in the chapter. Instead of asking only whether two assets are neighbors, the author defines matrices that capture whether they are connected by walks of length:

- exactly `k`
- or between `1` and `l`

This allows the portfolio designer to say things like:

- do not hold direct neighbors
- do not hold assets that are connected within two hops
- penalize concentration in tightly connected network neighborhoods

That is much richer than a plain pairwise-correlation threshold.

## Centrality Measures

The chapter then introduces node importance measures.

### Degree

Degree counts direct edges. In portfolio terms, a high-degree asset is one that is directly related to many others.

### Eigenvector Centrality

This measures influence beyond immediate neighbors. A node is important not just if it has many links, but if it is connected to other important nodes.

### Subgraph Centrality

This measures how strongly a node participates in closed walks in the network. It is a more global notion of embeddedness.

### Why Centrality Matters In Portfolios

The chapter’s diversification logic is intuitive:

- assets near the center of the network are more entangled with the rest of the universe
- assets on the periphery are more isolated
- a portfolio tilted toward peripheral assets may achieve a different kind of diversification than one built solely from covariance minimization

This is not saying peripheral assets are always better. It is saying their network role can be controlled deliberately.

## Graphs In Financial Markets

### Minimum Spanning Tree (MST)

The MST is presented as the classic network filter from Mantegna’s work. It keeps the most important links while connecting all nodes with the minimum number of edges.

Its practical interpretation is straightforward:

- assets with low degree and peripheral position are less entangled
- assets with higher degree are more structurally central

The book’s diversification intuition is that portfolios may become more diversified if they emphasize peripheral or nonadjacent assets in the MST.

### Triangulated Maximally Filtered Graph (TMFG)

TMFG is presented as a richer alternative to the MST. It retains more information because it keeps many more edges while still imposing structure.

The chapter notes:

- TMFG has substantially more edges than MST
- this means it preserves more of the strong-relationship structure in the market
- the same diversification intuition still applies, but on a denser network

The trade-off is familiar:

- MST is simpler and more aggressively filtered
- TMFG is richer but more structurally complex

## Portfolio Measures Based On Graphs

The chapter then defines portfolio-level quantities rather than asset-level quantities.

### Average Centrality Measure

This is the weighted average of node centrality under the portfolio weights.

Interpretation:

- high average centrality means the portfolio leans toward graph-center assets
- low average centrality means the portfolio leans toward graph-periphery assets

This creates a direct bridge between a descriptive network statistic and an optimization control variable.

### Percentage Invested In Connected Assets

This measure captures how much capital is placed in assets that are linked under the chosen connection matrix.

Interpretation:

- if two connected assets both receive nonzero weight, the portfolio is structurally concentrated in that neighborhood
- if the portfolio avoids connected pairs, this measure falls

This is a more structural notion of crowding than simple correlation limits.

## Centrality Constraint

The first major optimization idea is simple:

- optimize the portfolio objective
- subject to the portfolio having a chosen average centrality level

This is a powerful idea because it lets the designer steer the portfolio toward:

- more peripheral assets
- more central assets
- or a specific structural profile

The chapter points out that this constraint can be combined with the earlier machinery from Chapters 8 and 9:

- any classic objective function
- linear constraints
- convex risk limits
- tracking error constraints

So graph structure is not a replacement for portfolio optimization. It is an additional control dimension layered onto it.

## Neighborhood Constraint

This is one of the chapter’s most interesting contributions.

### Mixed-Integer Version

The mixed-integer model uses binary variables to say whether an asset is selected. The constraint ensures that selected assets are not neighbors, or more generally are not connected within a chosen walk length.

Interpretation:

- if asset A is chosen, assets too close to A in the graph cannot be chosen
- the walk-length parameter controls how strict this exclusion is

This turns graph distance into a diversification rule.

### Why It Is Useful

It can be combined with:

- any convex risk measure
- cardinality constraints
- realistic investability bounds

That makes it expressive. It is a way to say not merely "hold few assets" but "hold few assets that are structurally distinct from one another."

### Limitation

The obvious cost is combinatorial complexity. As the number of assets rises, mixed-integer models become hard to solve. The chapter also notes that if the connection matrix becomes too dense, the problem may become infeasible or practically unusable.

### Semidefinite Relaxation

To address that, the chapter introduces an SDP-style approximation. Instead of enforcing exact mutual exclusion through binaries, it constrains or penalizes the matrix that approximates outer products of weights.

Conceptually, the SDP version says:

- if two assets are connected, the product of their weights should be pushed toward zero

That does not always give the exact discrete solution, but it often gives a tractable approximation.

### Why The SDP Version Matters

Its advantage is robustness when the exact MIP formulation is too hard or infeasible. It trades exact selection logic for a softer, continuous approximation.

This is a recurring theme in advanced optimization:

- MIP gives sharper logical control
- SDP gives smoother approximations that may scale better

## 13.2 Cluster Constraint

The second half of the chapter applies the same logic not to graph neighborhoods but to dendrogram-defined clusters.

### From Dendrogram To Matrix

The chapter first turns clusters into matrix objects:

- a label matrix `L`, which records cluster membership
- an adjacency label matrix `L_A`, which records whether two assets belong to the same cluster

This is important because it shows how clustering information can become solver input rather than just a chart on screen.

### Percentage Invested In Related Assets

This is the cluster analogue of percentage invested in connected assets. Instead of asking whether the portfolio concentrates in graph neighbors, it asks whether it concentrates in assets from the same cluster.

Interpretation:

- high relatedness means capital is concentrated in behaviorally similar assets
- low relatedness means capital is spread across distinct clusters

This is a clean formalization of a diversification intuition many investors use informally.

### Mixed-Integer Cluster Constraint

The MIP version uses binary variables and the label matrix to enforce a rule such as:

- at most one asset per cluster

The chapter also notes this can be generalized:

- at most `K` assets per cluster
- or different cluster-specific limits

This is a useful practical result because it generalizes many familiar portfolio rules:

- one name per industry bucket
- a limited number of holdings from any correlated theme
- diversified exposure across behaviorally defined groups

The author also notes that this behaves like a cardinality constraint because the maximum number of held assets is tied to the number of clusters.

### Semidefinite Cluster Constraint

As with neighborhoods, the chapter gives an SDP approximation. The logic is parallel:

- if two assets are in the same cluster, the product of their weights should go to zero

This gives an approximate "one asset per cluster" rule without discrete variables.

### Trade-Off Between MIP And SDP

The comparison is consistent with the earlier discussion:

- MIP is exact but harder to solve
- SDP is approximate but often more forgiving

The chapter makes one limitation of the SDP version explicit: it does not generalize as naturally as the MIP version to "more than one asset per cluster" rules.

## What This Chapter Is Really Adding

The deepest contribution of the chapter is that it converts descriptive network structure into prescriptive portfolio controls.

Without this chapter, graph analysis might remain a research visualization tool:

- here is the market network
- here is who looks central
- here is which assets cluster together

With this chapter, those observations become optimization constraints:

- cap average centrality
- avoid graph neighbors
- avoid short-path connected assets
- hold no more than one asset per cluster
- penalize relatedness rather than only variance

That is a substantial shift from analysis to implementation.

## Relationship To Earlier Chapters

This chapter is best understood as an extension of Chapters 8, 9, and 12:

- Chapter 8 provides the objective functions
- Chapter 9 provides the broader language of realistic constraints
- Chapter 12 provides clustering structure
- Chapter 13 turns graph and cluster structure into additional constraint families

So Chapter 13 is not isolated. It is the structural overlay on top of the book’s optimization core.

## Practical Interpretation

The graph-based framework is useful when:

- the user cares about hidden concentration, not just variance concentration
- the asset universe contains many near-substitutes
- pairwise covariance misses higher-order network structure
- the portfolio manager wants explicit control over similarity crowding

Examples of practical use:

- ensure a long-only portfolio does not hold several stocks that sit in the same dense network neighborhood
- enforce that selected assets come from different behavioral clusters
- penalize allocations that drift toward graph-central names if the goal is structural diversification

## Limitations And Cautions

The chapter is sophisticated, but the method choices still matter:

- the graph depends on the codependence measure
- MST and TMFG retain different amounts of information
- cluster definitions depend on linkage and cluster-count selection
- dense graphs can make exact MIP constraints difficult
- approximate SDP formulations may not preserve the exact logical intent

So the graph layer adds information, but it also adds model risk. A bad graph can create false precision.

## Practical Takeaways

- MST is a simple filtered network and is easier to reason about.
- TMFG preserves more information and may be better when the user wants a richer structural picture.
- Centrality constraints are the easiest entry point because they add a continuous structural control without requiring discrete optimization.
- Neighborhood and cluster constraints are stronger but computationally more demanding.
- The real use case is not "replace mean-variance." It is "prevent structurally redundant portfolios that still look acceptable under standard risk metrics."

## Bottom Line

Chapter 13 takes network ideas that are often treated as exploratory visuals and turns them into actual portfolio design tools. Its main insight is that diversification can be defined structurally:

- diversify away from graph-central assets
- diversify away from connected assets
- diversify away from same-cluster assets

That is more nuanced than simply minimizing variance or maximizing Sharpe. The chapter is especially valuable for portfolio builders who already trust convex optimization but want additional controls against hidden concentration in related names.
