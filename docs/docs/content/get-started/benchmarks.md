# :material-speedometer: Performance Benchmarks

Rayforce-Py delivers exceptional performance, closely matching native Rayforce while significantly outperforming Pandas. Our benchmarks are based on the [H2OAI Group By Benchmark](https://h2oai.github.io/db-benchmark/) standard.


<div style="margin: 1.5rem 0;">
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Rayforce-Py</span>
        <span style="color: var(--gold-500); font-weight: 700;">772 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--gold-500), var(--gold-400)); height: 100%; width: 21.5%;"></div>
      </div>
    </div>
    <div style="color: var(--gold-500); font-weight: 700; min-width: 60px; text-align: right;">4.66x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Native Rayforce</span>
        <span style="color: var(--navy-300); font-weight: 700;">767 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--navy-400), var(--navy-300)); height: 100%; width: 21.3%;"></div>
      </div>
    </div>
    <div style="color: var(--navy-300); font-weight: 700; min-width: 60px; text-align: right;">4.69x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Pandas</span>
        <span style="color: var(--text-secondary); font-weight: 700;">3,597 μs</span>
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
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">1M</div>
    <div style="color: var(--text-secondary); font-size: 0.9rem;">Rows Tested</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">4.76x</div>
    <div style="color: var(--text-secondary); font-size: 0.9rem;">Faster than Pandas</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">99%</div>
    <div style="color: var(--text-secondary); font-size: 0.9rem;">Native Performance</div>
  </div>
</div>

!!! info "Benchmark Methodology"
    - **Dataset**: 1,000,000 rows, 6 columns (id1, id2, id3, v1, v2, v3)
    - **Timing**: Median of 20 runs
    - **Warmup**: 5 runs per query to warm caches
    - **Data**: Deterministic (seed=42) for reproducibility

---

#### Q1: Group by `id1`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **772** | ±45 | 0.99x | **4.66x** |
| Native Rayforce | 767 | ±22 | 1.00x | 4.69x |
| Pandas | 3,597 | ±140 | 4.69x | 1.00x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **2,376** | ±55 | 1.00x | **5.73x** |
| Native Rayforce | 2,388 | ±43 | 1.00x | 5.70x |
| Pandas | 13,609 | ±258 | 5.70x | 1.00x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.73x faster** than Pandas.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **1,148** | ±44 | 1.01x | **4.17x** |
| Native Rayforce | 1,154 | ±50 | 1.00x | 4.15x |
| Pandas | 4,787 | ±69 | 4.15x | 1.00x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **1,649** | ±62 | 1.00x | **3.73x** |
| Native Rayforce | 1,642 | ±85 | 1.00x | 3.75x |
| Pandas | 6,152 | ±113 | 3.75x | 1.00x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **1,235** | ±62 | 0.95x | **5.58x** |
| Native Rayforce | 1,178 | ±47 | 1.00x | 5.85x |
| Pandas | 6,899 | ±113 | 5.85x | 1.00x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.58x faster** than Pandas, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas |
|----------------|-----------|---------|------------|-----------|
| **Rayforce-Py** | **1,004** | ±36 | 0.99x | **4.72x** |
| Native Rayforce | 999 | ±43 | 1.00x | 4.74x |
| Pandas | 4,736 | ±74 | 4.74x | 1.00x |

---

| Query | Rayforce-Py Speedup | Native Rayforce Speedup |
|-------|---------------------|------------------------|
| Q1 | **4.66x** | 4.69x |
| Q2 | **5.73x** | 5.70x |
| Q3 | **4.17x** | 4.15x |
| Q4 | **3.73x** | 3.75x |
| Q5 | **5.58x** | 5.85x |
| Q6 | **4.72x** | 4.74x |
| **Average** | **4.76x** | **4.81x** |

!!! note "Overhead Analysis"
    Rayforce-Py adds only **0.88% average overhead** compared to native Rayforce, demonstrating the efficiency of the Python bindings. Most queries show less than 1% overhead, with Q5 being the outlier at 4.85%.

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

---

*Benchmarks run on: macOS M4 32GB, 1M rows, 100 groups, 20 runs (median), 5 warmup runs*

