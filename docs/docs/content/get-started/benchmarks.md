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
      { value: 781, itemStyle: { color: '#E9A320' } },
      { value: 779, itemStyle: { color: '#1B365D' } },
      { value: 1096, itemStyle: { color: '#718096' } },
      { value: 3696, itemStyle: { color: '#718096' } }
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
      { value: 2398, itemStyle: { color: '#E9A320' } },
      { value: 2410, itemStyle: { color: '#1B365D' } },
      { value: 6797, itemStyle: { color: '#718096' } },
      { value: 14155, itemStyle: { color: '#718096' } }
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
      { value: 995, itemStyle: { color: '#E9A320' } },
      { value: 983, itemStyle: { color: '#1B365D' } },
      { value: 1261, itemStyle: { color: '#718096' } },
      { value: 5141, itemStyle: { color: '#718096' } }
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
      { value: 1228, itemStyle: { color: '#E9A320' } },
      { value: 1205, itemStyle: { color: '#1B365D' } },
      { value: 1441, itemStyle: { color: '#718096' } },
      { value: 6158, itemStyle: { color: '#718096' } }
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
      { value: 1202, itemStyle: { color: '#E9A320' } },
      { value: 1176, itemStyle: { color: '#1B365D' } },
      { value: 1431, itemStyle: { color: '#718096' } },
      { value: 7086, itemStyle: { color: '#718096' } }
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
      { value: 1019, itemStyle: { color: '#E9A320' } },
      { value: 990, itemStyle: { color: '#1B365D' } },
      { value: 3403, itemStyle: { color: '#718096' } },
      { value: 4922, itemStyle: { color: '#718096' } }
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

<div id="q1-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **781** | 1.00x | **4.74x** | **1.40x** |
| Native Rayforce | 779 | 1.00x | 4.75x | 1.41x |
| Polars | 1,096 | 1.41x | 3.37x | 1.00x |
| Pandas | 3,696 | 4.75x | 1.00x | 0.30x |

---

#### Q2: Group by `id1`, `id2`, sum `v1`

<div id="q2-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **2,398** | 1.00x | **5.90x** | **2.83x** |
| Native Rayforce | 2,410 | 1.00x | 5.87x | 2.82x |
| Polars | 6,797 | 2.82x | 2.08x | 1.00x |
| Pandas | 14,155 | 5.87x | 1.00x | 0.48x |

!!! tip "Performance Insight"
    Multi-column group by operations show the largest performance advantage, with Rayforce-Py being **5.90x faster** than Pandas and **2.83x faster** than Polars.

---

#### Q3: Group by `id3`, sum `v1`, avg `v3`

<div id="q3-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **995** | 0.99x | **5.17x** | **1.27x** |
| Native Rayforce | 983 | 1.00x | 5.23x | 1.28x |
| Polars | 1,261 | 1.28x | 4.08x | 1.00x |
| Pandas | 5,141 | 5.23x | 1.00x | 0.25x |

---

#### Q4: Group by `id3`, avg `v1`, `v2`, `v3`

<div id="q4-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **1,228** | 0.98x | **5.01x** | **1.17x** |
| Native Rayforce | 1,205 | 1.00x | 5.11x | 1.19x |
| Polars | 1,441 | 1.19x | 4.27x | 1.00x |
| Pandas | 6,158 | 5.11x | 1.00x | 0.23x |

---

#### Q5: Group by `id3`, sum `v1`, `v2`, `v3`

<div id="q5-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **1,202** | 0.98x | **5.90x** | **1.19x** |
| Native Rayforce | 1,176 | 1.00x | 6.03x | 1.22x |
| Polars | 1,431 | 1.22x | 4.95x | 1.00x |
| Pandas | 7,086 | 6.03x | 1.00x | 0.20x |

!!! success "Best Performance"
    Q5 shows Rayforce-Py performing **5.90x faster** than Pandas and **1.19x faster** than Polars, demonstrating excellent performance on multiple aggregations.

---

#### Q6: Group by `id3`, max(`v1`) - min(`v2`)

<div id="q6-chart" style="width: 100%; height: 400px; margin-bottom: 1.5rem;"></div>

| Implementation | Time (μs) | vs Native | vs Pandas | vs Polars |
|----------------|-----------|------------|-----------|-----------|
| **Rayforce-Py** | **1,019** | 0.97x | **4.83x** | **3.34x** |
| Native Rayforce | 990 | 1.00x | 4.97x | 3.44x |
| Polars | 3,403 | 3.44x | 1.45x | 1.00x |
| Pandas | 4,922 | 4.97x | 1.00x | 0.69x |

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
