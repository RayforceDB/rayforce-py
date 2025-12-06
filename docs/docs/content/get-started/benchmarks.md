# :material-speedometer: Performance Benchmarks

Rayforce-Py delivers exceptional performance, closely matching native Rayforce while significantly outperforming Pandas. Our benchmarks are based on the [H2OAI Group By Benchmark](https://h2oai.github.io/db-benchmark/) standard.


<div style="margin: 1.5rem 0;">
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Rayforce-Py</span>
        <span style="color: var(--gold-500); font-weight: 700;">1,093 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--gold-500), var(--gold-400)); height: 100%; width: 16.4%;"></div>
      </div>
    </div>
    <div style="color: var(--gold-500); font-weight: 700; min-width: 60px; text-align: right;">5.16x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Native Rayforce</span>
        <span style="color: var(--navy-300); font-weight: 700;">1,146 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--navy-400), var(--navy-300)); height: 100%; width: 17.2%;"></div>
      </div>
    </div>
    <div style="color: var(--navy-300); font-weight: 700; min-width: 60px; text-align: right;">5.82x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Polars</span>
        <span style="color: var(--text-secondary); font-weight: 700;">2,474 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-secondary)); height: 100%; width: 37.1%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">2.70x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Pandas</span>
        <span style="color: var(--text-secondary); font-weight: 700;">6,667 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-tertiary)); height: 100%; width: 100%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">1.00x</div>
  </div>
</div>


<div class="benchmark-stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~1.81x</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Faster than Polars</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~5.16x</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Faster than Pandas</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">99%+</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Native Performance</div>
  </div>
</div>

*Benchmarks run on: macOS M4 32GB, 1M rows, 100 groups, 20 runs (median), 5 warmup runs*

!!! info "Methodology"
    - **Dataset**: 1,000,000 rows, 6 columns (id1, id2, id3, v1, v2, v3)
    - **Timing**: Median of 20 runs
    - **Warmup**: 5 runs per query to warm caches
    - **Data**: Deterministic (seed=42) for reproducibility

---

#### Q1: Group by `id1`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **767** | ±72 | 0.99x | **4.74x** | **1.36x** |
| Native Rayforce | 762 | ±31 | 1.00x | 4.78x | 1.37x |
| Polars | 1,045 | ±92 | 1.37x | 3.48x | 1.00x |
| Pandas | 3,638 | ±113 | 4.78x | 1.00x | 0.29x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **2,410** | ±104 | 1.00x | **5.76x** | **2.75x** |
| Native Rayforce | 2,420 | ±84 | 1.00x | 5.74x | 2.75x |
| Polars | 6,634 | ±595 | 2.75x | 2.09x | 1.00x |
| Pandas | 13,885 | ±232 | 5.74x | 1.00x | 0.48x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.76x faster** than Pandas and **2.75x faster** than Polars.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **978** | ±38 | 0.99x | **5.05x** | **1.27x** |
| Native Rayforce | 970 | ±28 | 1.00x | 5.09x | 1.28x |
| Polars | 1,245 | ±811 | 1.28x | 3.96x | 1.00x |
| Pandas | 4,936 | ±102 | 5.09x | 1.00x | 0.25x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,224** | ±40 | 0.98x | **4.87x** | **1.16x** |
| Native Rayforce | 1,195 | ±60 | 1.00x | 4.99x | 1.18x |
| Polars | 1,415 | ±114 | 1.18x | 4.21x | 1.00x |
| Pandas | 5,960 | ±215 | 4.99x | 1.00x | 0.24x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,182** | ±66 | 0.98x | **5.76x** | **1.14x** |
| Native Rayforce | 1,161 | ±23 | 1.00x | 5.87x | 1.16x |
| Polars | 1,345 | ±77 | 1.16x | 5.06x | 1.00x |
| Pandas | 6,815 | ±65 | 5.87x | 1.00x | 0.20x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.76x faster** than Pandas and **1.14x faster** than Polars, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **996** | ±49 | 0.97x | **4.79x** | **3.18x** |
| Native Rayforce | 970 | ±27 | 1.00x | 4.92x | 3.26x |
| Polars | 3,163 | ±171 | 3.26x | 1.51x | 1.00x |
| Pandas | 4,767 | ±56 | 4.92x | 1.00x | 0.66x |

---

| Query | Rayforce-Py vs Native | Rayforce-Py vs Pandas | Rayforce-Py vs Polars |
|-------|----------------------|----------------------|----------------------|
| Q1 | 0.99x | **4.74x** | **1.36x** |
| Q2 | 1.00x | **5.76x** | **2.75x** |
| Q3 | 0.99x | **5.05x** | **1.27x** |
| Q4 | 0.98x | **4.87x** | **1.16x** |
| Q5 | 0.98x | **5.76x** | **1.14x** |
| Q6 | 0.97x | **4.79x** | **3.18x** |
| **Average** | **0.99x** | **5.16x** | **1.81x** |

!!! note "Performance Analysis"
    Rayforce-Py adds only **1% average overhead** compared to native Rayforce, demonstrating the efficiency of the Python bindings. On average, Rayforce-Py is **5.16x faster** than Pandas and **1.81x faster** than Polars, making it an excellent choice for high-performance data processing.

---

## :material-cog: Running Your Own Benchmarks

You can run the benchmarks yourself using the provided benchmark suite:

```bash
# Default (15 runs, 5 warmup)
make benchmarkdb

# Custom configuration
make benchmarkdb ARGS="--runs 20 --warmup 5"
```

!!! tip "For Accurate Results"
    - Use at least **15-20 runs** for statistical significance
    - Ensure your system is idle to minimize interference
    - Results use **median** (more robust than mean) with standard deviation reported

## :material-book-open: Learn More

- [Getting Started Guide](overview.md) - Learn how to use Rayforce-Py
- [Query Guide](../documentation/query-guide/overview.md) - Explore query capabilities
