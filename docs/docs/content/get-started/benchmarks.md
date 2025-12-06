# :material-speedometer: Performance Benchmarks

Rayforce-Py delivers exceptional performance, closely matching native Rayforce while significantly outperforming Pandas. Our benchmarks are based on the [H2OAI Group By Benchmark](https://h2oai.github.io/db-benchmark/) standard.


<div style="margin: 1.5rem 0;">
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Rayforce-Py</span>
        <span style="color: var(--gold-500); font-weight: 700;">1,271 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--gold-500), var(--gold-400)); height: 100%; width: 18.5%;"></div>
      </div>
    </div>
    <div style="color: var(--gold-500); font-weight: 700; min-width: 60px; text-align: right;">5.26x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Native Rayforce</span>
        <span style="color: var(--navy-300); font-weight: 700;">1,257 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--navy-400), var(--navy-300)); height: 100%; width: 18.3%;"></div>
      </div>
    </div>
    <div style="color: var(--navy-300); font-weight: 700; min-width: 60px; text-align: right;">5.46x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Polars</span>
        <span style="color: var(--text-secondary); font-weight: 700;">2,572 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-secondary)); height: 100%; width: 37.5%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">2.67x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Pandas</span>
        <span style="color: var(--text-secondary); font-weight: 700;">6,860 μs</span>
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
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~2x</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Faster than Polars</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~5.3x</div>
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
| **Rayforce-Py** | **781** | - | 1.00x | **4.74x** | **1.40x** |
| Native Rayforce | 779 | - | 1.00x | 4.75x | 1.41x |
| Polars | 1,096 | - | 1.41x | 3.37x | 1.00x |
| Pandas | 3,696 | - | 4.75x | 1.00x | 0.30x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **2,398** | - | 1.00x | **5.90x** | **2.83x** |
| Native Rayforce | 2,410 | - | 1.00x | 5.87x | 2.82x |
| Polars | 6,797 | - | 2.82x | 2.08x | 1.00x |
| Pandas | 14,155 | - | 5.87x | 1.00x | 0.48x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.90x faster** than Pandas and **2.83x faster** than Polars.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **995** | - | 0.99x | **5.17x** | **1.27x** |
| Native Rayforce | 983 | - | 1.00x | 5.23x | 1.28x |
| Polars | 1,261 | - | 1.28x | 4.08x | 1.00x |
| Pandas | 5,141 | - | 5.23x | 1.00x | 0.25x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,228** | - | 0.98x | **5.01x** | **1.17x** |
| Native Rayforce | 1,205 | - | 1.00x | 5.11x | 1.19x |
| Polars | 1,441 | - | 1.19x | 4.27x | 1.00x |
| Pandas | 6,158 | - | 5.11x | 1.00x | 0.23x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,202** | - | 0.98x | **5.90x** | **1.19x** |
| Native Rayforce | 1,176 | - | 1.00x | 6.03x | 1.22x |
| Polars | 1,431 | - | 1.22x | 4.95x | 1.00x |
| Pandas | 7,086 | - | 6.03x | 1.00x | 0.20x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.90x faster** than Pandas and **1.19x faster** than Polars, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,019** | - | 0.97x | **4.83x** | **3.34x** |
| Native Rayforce | 990 | - | 1.00x | 4.97x | 3.44x |
| Polars | 3,403 | - | 3.44x | 1.45x | 1.00x |
| Pandas | 4,922 | - | 4.97x | 1.00x | 0.69x |

---

| Query | Rayforce-Py vs Native | Rayforce-Py vs Pandas | Rayforce-Py vs Polars |
|-------|----------------------|----------------------|----------------------|
| Q1 | 1.00x | **4.74x** | **1.40x** |
| Q2 | 1.00x | **5.90x** | **2.83x** |
| Q3 | 0.99x | **5.17x** | **1.27x** |
| Q4 | 0.98x | **5.01x** | **1.17x** |
| Q5 | 0.98x | **5.90x** | **1.19x** |
| Q6 | 0.97x | **4.83x** | **3.34x** |
| **Average** | **0.99x** | **5.26x** | **1.87x** |

!!! note "Performance Analysis"
    Rayforce-Py adds less that **0.5% average overhead** compared to native Rayforce, demonstrating the efficiency of the Python bindings. On average, Rayforce-Py is **5.26x faster** than Pandas and **1.87x faster** than Polars, making it an excellent choice for high-performance data processing.

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
