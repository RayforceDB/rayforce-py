# :material-speedometer: Performance Benchmarks

Rayforce-Py delivers exceptional performance, closely matching native Rayforce while significantly outperforming Pandas. Our benchmarks are based on the [H2OAI Group By Benchmark](https://h2oai.github.io/db-benchmark/) standard.


<div style="margin: 1.5rem 0;">
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Rayforce-Py</span>
        <span style="color: var(--gold-500); font-weight: 700;">730 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--gold-500), var(--gold-400)); height: 100%; width: 20.4%;"></div>
      </div>
    </div>
    <div style="color: var(--gold-500); font-weight: 700; min-width: 60px; text-align: right;">4.89x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Native Rayforce</span>
        <span style="color: var(--navy-300); font-weight: 700;">720 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--navy-400), var(--navy-300)); height: 100%; width: 20.2%;"></div>
      </div>
    </div>
    <div style="color: var(--navy-300); font-weight: 700; min-width: 60px; text-align: right;">4.96x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Polars</span>
        <span style="color: var(--text-secondary); font-weight: 700;">993 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-secondary)); height: 100%; width: 27.8%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">3.60x</div>
  </div>
  
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Pandas</span>
        <span style="color: var(--text-secondary); font-weight: 700;">3,572 μs</span>
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
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~1.8x</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Faster than Polars</div>
  </div>
  <div style="background: linear-gradient(135deg, rgba(233, 163, 32, 0.1) 0%, rgba(233, 163, 32, 0.05) 100%); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(233, 163, 32, 0.2);">
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">~5x</div>
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
| **Rayforce-Py** | **730** | ±45 | 0.99x | **4.89x** | **1.36x** |
| Native Rayforce | 720 | ±22 | 1.00x | 4.96x | 1.38x |
| Polars | 993 | ±50 | 1.38x | 3.60x | 1.00x |
| Pandas | 3,572 | ±140 | 4.96x | 1.00x | 0.28x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **2,309** | ±55 | 1.02x | **5.97x** | **2.89x** |
| Native Rayforce | 2,360 | ±43 | 1.00x | 5.85x | 2.83x |
| Polars | 6,684 | ±150 | 2.83x | 2.06x | 1.00x |
| Pandas | 13,797 | ±258 | 5.85x | 1.00x | 0.48x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.97x faster** than Pandas and **2.89x faster** than Polars.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,071** | ±44 | 0.98x | **4.50x** | **1.15x** |
| Native Rayforce | 1,050 | ±50 | 1.00x | 4.59x | 1.17x |
| Polars | 1,232 | ±60 | 1.17x | 3.91x | 1.00x |
| Pandas | 4,824 | ±69 | 4.59x | 1.00x | 0.26x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,526** | ±62 | 1.00x | **3.96x** | **0.92x** |
| Native Rayforce | 1,520 | ±85 | 1.00x | 3.97x | 0.92x |
| Polars | 1,401 | ±55 | 0.92x | 4.31x | 1.00x |
| Pandas | 6,037 | ±113 | 3.97x | 1.00x | 0.23x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **1,282** | ±62 | 0.97x | **5.44x** | **1.20x** |
| Native Rayforce | 1,247 | ±47 | 1.00x | 5.59x | 1.23x |
| Polars | 1,537 | ±70 | 1.23x | 4.54x | 1.00x |
| Pandas | 6,973 | ±113 | 5.59x | 1.00x | 0.22x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.44x faster** than Pandas and **1.20x faster** than Polars, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

| Implementation | Time (μs) | Std Dev | vs Native | vs Pandas | vs Polars |
|----------------|-----------|---------|------------|-----------|-----------|
| **Rayforce-Py** | **989** | ±36 | 0.96x | **4.74x** | **3.23x** |
| Native Rayforce | 954 | ±43 | 1.00x | 4.91x | 3.35x |
| Polars | 3,200 | ±120 | 3.35x | 1.46x | 1.00x |
| Pandas | 4,685 | ±74 | 4.91x | 1.00x | 0.68x |

---

| Query | Rayforce-Py vs Native | Rayforce-Py vs Pandas | Rayforce-Py vs Polars |
|-------|----------------------|----------------------|----------------------|
| Q1 | 0.99x | **4.89x** | **1.36x** |
| Q2 | 1.02x | **5.97x** | **2.89x** |
| Q3 | 0.98x | **4.50x** | **1.15x** |
| Q4 | 1.00x | **3.96x** | 0.92x |
| Q5 | 0.97x | **5.44x** | **1.20x** |
| Q6 | 0.96x | **4.74x** | **3.23x** |
| **Average** | **0.99x** | **4.92x** | **1.79x** |

!!! note "Performance Analysis"
    Rayforce-Py adds only **1% average overhead** compared to native Rayforce, demonstrating the efficiency of the Python bindings. On average, Rayforce-Py is **4.92x faster** than Pandas and **1.79x faster** than Polars, making it an excellent choice for high-performance data processing.

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
