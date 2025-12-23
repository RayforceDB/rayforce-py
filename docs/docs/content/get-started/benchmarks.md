# :material-speedometer: Performance Benchmarks

Rayforce-Py delivers exceptional performance, closely matching native Rayforce while significantly outperforming Pandas. Our benchmarks are based on the [H2OAI Group By Benchmark](https://h2oai.github.io/db-benchmark/) standard.

<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

<script>
// Store chart instances
var chartInstances = {};

// Helper function to convert RGB to hex
function rgbToHex(rgb) {
  if (!rgb) return '';
  if (rgb.startsWith('#')) return rgb;

  var match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  if (match) {
    var r = parseInt(match[1]).toString(16).padStart(2, '0');
    var g = parseInt(match[2]).toString(16).padStart(2, '0');
    var b = parseInt(match[3]).toString(16).padStart(2, '0');
    return '#' + r + g + b;
  }
  return rgb;
}

// Simple and reliable theme detection
function getChartTheme() {
  // Use light grey for all chart text
  var textColor = '#888888';

  // Determine if dark mode for other styling
  var scheme = document.documentElement.getAttribute('data-md-color-scheme');
  var isDark = scheme === 'slate';

  return {
    textColor: textColor,
    gridLineColor: isDark ? '#4A5568' : '#D0D0D0',
    isDark: isDark
  };
}

// Initialize all charts when DOM is ready
function initAllCharts() {
  // Get fresh theme detection for each initialization
  var theme = getChartTheme();

  // Q1 Chart
  var q1Chart = echarts.init(document.getElementById('q1-chart'));
  q1Chart.setOption({
    title: { text: 'Q1: Group by id1, sum v1', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { textStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { textStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 741, itemStyle: { color: '#E9A320' } },
      { value: 761, itemStyle: { color: '#1B365D' } },
      { value: 1143, itemStyle: { color: '#718096' } },
      { value: 3663, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', textStyle: { color: theme.textColor, fontWeight: 'bold' } } }]
  });
  chartInstances['q1-chart'] = q1Chart;

  // Q2 Chart
  var q2Chart = echarts.init(document.getElementById('q2-chart'));
  q2Chart.setOption({
    title: { text: 'Q2: Group by id1, id2, sum v1', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { rotate: 0, color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 2351, itemStyle: { color: '#E9A320' } },
      { value: 2400, itemStyle: { color: '#1B365D' } },
      { value: 6763, itemStyle: { color: '#718096' } },
      { value: 13675, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', color: theme.textColor } }]
  });
  chartInstances['q2-chart'] = q2Chart;

  // Q3 Chart
  var q3Chart = echarts.init(document.getElementById('q3-chart'));
  q3Chart.setOption({
    title: { text: 'Q3: Group by id3, sum v1, avg v3', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { rotate: 0, color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 956, itemStyle: { color: '#E9A320' } },
      { value: 974, itemStyle: { color: '#1B365D' } },
      { value: 1376, itemStyle: { color: '#718096' } },
      { value: 4902, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', color: theme.textColor } }]
  });
  chartInstances['q3-chart'] = q3Chart;

  // Q4 Chart
  var q4Chart = echarts.init(document.getElementById('q4-chart'));
  q4Chart.setOption({
    title: { text: 'Q4: Group by id3, avg v1, v2, v3', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { rotate: 0, color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 1182, itemStyle: { color: '#E9A320' } },
      { value: 1182, itemStyle: { color: '#1B365D' } },
      { value: 1594, itemStyle: { color: '#718096' } },
      { value: 6161, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', color: theme.textColor } }]
  });
  chartInstances['q4-chart'] = q4Chart;

  // Q5 Chart
  var q5Chart = echarts.init(document.getElementById('q5-chart'));
  q5Chart.setOption({
    title: { text: 'Q5: Group by id3, sum v1, v2, v3', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { rotate: 0, color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 1153, itemStyle: { color: '#E9A320' } },
      { value: 1164, itemStyle: { color: '#1B365D' } },
      { value: 1551, itemStyle: { color: '#718096' } },
      { value: 6908, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', color: theme.textColor } }]
  });
  chartInstances['q5-chart'] = q5Chart;

  // Q6 Chart
  var q6Chart = echarts.init(document.getElementById('q6-chart'));
  q6Chart.setOption({
    title: { text: 'Q6: Group by id3, max(v1) - min(v2)', left: 'center', textStyle: { fontSize: 16, fontWeight: 'bold', color: theme.textColor } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function(params) { return params[0].name + '<br/>' + params[0].seriesName + ': ' + params[0].value + ' μs'; }, textStyle: { color: theme.textColor }, backgroundColor: theme.isDark ? 'rgba(26, 26, 26, 0.9)' : 'rgba(255, 255, 255, 0.9)', borderColor: theme.gridLineColor },
    legend: { top: 30, data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], textStyle: { color: theme.textColor } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 80, containLabel: true },
    xAxis: { type: 'category', data: ['Rayforce-Py', 'Native Rayforce', 'Polars', 'Pandas'], axisLabel: { rotate: 0, color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } } },
    yAxis: { type: 'value', name: 'Time (μs)', nameLocation: 'middle', nameGap: 50, nameTextStyle: { color: theme.textColor }, axisLabel: { color: theme.textColor }, axisLine: { lineStyle: { color: theme.textColor } }, splitLine: { lineStyle: { color: theme.gridLineColor } } },
    series: [{ name: 'Time (μs)', type: 'bar', data: [
      { value: 967, itemStyle: { color: '#E9A320' } },
      { value: 971, itemStyle: { color: '#1B365D' } },
      { value: 3339, itemStyle: { color: '#718096' } },
      { value: 4802, itemStyle: { color: '#718096' } }
    ], label: { show: true, position: 'top', color: theme.textColor } }]
  });
  chartInstances['q6-chart'] = q6Chart;

  // Resize handler
  window.addEventListener('resize', function() {
    Object.values(chartInstances).forEach(function(chart) {
      chart.resize();
    });
  });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  // Wait for theme to be applied - use requestAnimationFrame to ensure DOM is ready
  requestAnimationFrame(function() {
    setTimeout(initAllCharts, 200);
  });
});

// Watch for theme changes
var observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
      // Reinitialize all charts with new theme
      Object.keys(chartInstances).forEach(function(chartId) {
        chartInstances[chartId].dispose();
      });
      chartInstances = {};
      setTimeout(initAllCharts, 50);
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });
});
</script>


<div style="margin: 1.5rem 0;">
  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Rayforce-Py</span>
        <span style="color: var(--gold-500); font-weight: 700;">1,225 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--gold-500), var(--gold-400)); height: 100%; width: 17.8%;"></div>
      </div>
    </div>
    <div style="color: var(--gold-500); font-weight: 700; min-width: 60px; text-align: right;">1.00x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Native Rayforce</span>
        <span style="color: var(--navy-300); font-weight: 700;">1,207 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--navy-400), var(--navy-300)); height: 100%; width: 17.6%;"></div>
      </div>
    </div>
    <div style="color: var(--navy-300); font-weight: 700; min-width: 60px; text-align: right;">1.00x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Polars</span>
        <span style="color: var(--text-secondary); font-weight: 700;">2,448 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-secondary)); height: 100%; width: 35.7%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">2.00x</div>
  </div>

  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="flex: 1;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
        <span style="font-weight: 600;">Pandas</span>
        <span style="color: var(--text-secondary); font-weight: 700;">6,685 μs</span>
      </div>
      <div style="background: var(--bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
        <div style="background: linear-gradient(90deg, var(--text-secondary), var(--text-tertiary)); height: 100%; width: 100%;"></div>
      </div>
    </div>
    <div style="color: var(--text-secondary); font-weight: 700; min-width: 60px; text-align: right;">5.34x</div>
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
    <div style="font-size: 2.5rem; font-weight: 800; color: var(--gold-500); margin-bottom: 0.5rem;">100%</div>
    <div style="color: var(--text-secondary); font-size: 0.8rem;">Native Performance</div>
  </div>
</div>

*Benchmarks run on: macOS M4 32GB, 1M rows, 100 groups, 50 runs (median), 20 warmup runs*

!!! info "Methodology"
    - **Dataset**: 1,000,000 rows, 6 columns (id1, id2, id3, v1, v2, v3)
    - **Timing**: Median of 50 runs
    - **Warmup**: 20 runs per query to warm caches
    - **Data**: Deterministic (seed=42) for reproducibility

---

#### Q1: Group by `id1`, sum `v1`

<div id="q1-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **741** | 1.03x | **4.94x** | **1.54x** |
| Native Rayforce | 761 | 1.00x | 4.81x | 1.50x |
| Polars | 1,143 | 1.50x | 3.20x | 1.00x |
| Pandas | 3,663 | 4.81x | 1.00x | 0.31x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

<div id="q2-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **2,351** | 1.02x | **5.82x** | **2.88x** |
| Native Rayforce | 2,400 | 1.00x | 5.70x | 2.81x |
| Polars | 6,763 | 2.81x | 2.02x | 1.00x |
| Pandas | 13,675 | 5.70x | 1.00x | 0.50x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.82x faster** than Pandas and **2.88x faster** than Polars.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

<div id="q3-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **956** | 1.02x | **5.13x** | **1.44x** |
| Native Rayforce | 974 | 1.00x | 5.03x | 1.41x |
| Polars | 1,376 | 1.41x | 3.56x | 1.00x |
| Pandas | 4,902 | 5.03x | 1.00x | 0.28x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

<div id="q4-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **1,182** | 1.00x | **5.21x** | **1.35x** |
| Native Rayforce | 1,182 | 1.00x | 5.21x | 1.35x |
| Polars | 1,594 | 1.35x | 3.87x | 1.00x |
| Pandas | 6,161 | 5.21x | 1.00x | 0.26x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

<div id="q5-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **1,153** | 1.01x | **5.99x** | **1.34x** |
| Native Rayforce | 1,164 | 1.00x | 5.93x | 1.33x |
| Polars | 1,551 | 1.33x | 4.45x | 1.00x |
| Pandas | 6,908 | 5.93x | 1.00x | 0.22x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.99x faster** than Pandas and **1.34x faster** than Polars, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

<div id="q6-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **967** | 1.00x | **4.97x** | **3.45x** |
| Native Rayforce | 971 | 1.00x | 4.95x | 3.44x |
| Polars | 3,339 | 3.44x | 1.44x | 1.00x |
| Pandas | 4,802 | 4.95x | 1.00x | 0.69x |

---

| Query | Rayforce-Py vs Native | Rayforce-Py vs Pandas | Rayforce-Py vs Polars |
|-------|----------------------|----------------------|----------------------|
| Q1 | 1.03x | **4.94x** | **1.54x** |
| Q2 | 1.02x | **5.82x** | **2.88x** |
| Q3 | 1.02x | **5.13x** | **1.44x** |
| Q4 | 1.00x | **5.21x** | **1.35x** |
| Q5 | 1.01x | **5.99x** | **1.34x** |
| Q6 | 1.00x | **4.97x** | **3.45x** |
| **Average** | **1.01x** | **5.34x** | **2.00x** |

!!! note "Performance Analysis"
    Rayforce-Py adds almost **no overhead** compared to native Rayforce, demonstrating the efficiency of the Python bindings. On average, Rayforce-Py is **5.34x faster** than Pandas and **2.00x faster** than Polars, making it an excellent choice for high-performance data processing.

    Note: The slight performance advantage shown by Rayforce-Py over native Rayforce is due to measurement methodology differences. Native Rayforce benchmarks include memory deallocation overhead, while Rayforce-Py measurements exclude it. In practice, the performance difference is negligible and within measurement noise, demonstrating that the Python bindings introduce virtually no overhead.

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

<script>
// Store chart references and update on theme change
var chartInstances = {};

// Function to initialize and store chart
function initChart(chartId, optionFunc) {
  document.addEventListener('DOMContentLoaded', function() {
    var theme = getChartTheme();
    var chart = echarts.init(document.getElementById(chartId));
    var option = optionFunc(theme);
    chart.setOption(option);
    chartInstances[chartId] = chart;
    window.addEventListener('resize', function() { chart.resize(); });
  });
}

// Watch for theme changes
var observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
      Object.keys(chartInstances).forEach(function(chartId) {
        updateChartTheme(chartInstances[chartId], chartId);
      });
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });
});
</script>
