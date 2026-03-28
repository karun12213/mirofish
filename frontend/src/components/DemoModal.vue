<template>
  <!-- Trigger Button (use this in your Home.vue or wherever your CTA is) -->
  <!-- <button @click="open = true">Launch Live Demo</button> -->

  <Teleport to="body">
    <Transition name="mf-fade">
      <div v-if="open" class="mf-backdrop" @click.self="open = false">
        <div class="mf-modal">

          <!-- HEADER -->
          <div class="mf-header">
            <div class="mf-header-left">
              <span class="mf-live-dot" />
              <span class="mf-live-label">LIVE</span>
              <span class="mf-divider">│</span>
              <span class="mf-brand">MIROFISH</span>
              <span class="mf-subtitle">SIMULATION COMMAND CENTER</span>
            </div>
            <button class="mf-close" @click="open = false">✕ ESC</button>
          </div>

          <!-- STAT BAR -->
          <div class="mf-statbar">
            <div v-for="s in stats" :key="s.label" class="mf-stat">
              <div class="mf-stat-value" :style="{ color: s.color }">{{ s.value }}</div>
              <div class="mf-stat-label">{{ s.label }}</div>
            </div>
          </div>

          <!-- TICKER -->
          <div class="mf-ticker">
            <span class="mf-blink">▶</span>
            <Transition name="mf-tick">
              <span :key="tickerIdx" class="mf-ticker-text" :class="{ warn: isWarn }">
                {{ tickers[tickerIdx] }}
              </span>
            </Transition>
          </div>

          <!-- CHARTS GRID -->
          <div class="mf-grid">

            <!-- Network Graph -->
            <div class="mf-panel">
              <div class="mf-panel-head">
                <span class="mf-panel-title">Agent Network</span>
                <span class="mf-badge cyan">34 NODES ACTIVE</span>
              </div>
              <div class="mf-panel-body">
                <svg ref="networkSvg" class="mf-svg" viewBox="0 0 320 190" />
                <div class="mf-legend">
                  <span v-for="l in netLegend" :key="l.label" class="mf-legend-item">
                    <span class="mf-dot" :style="{ background: l.color }" />{{ l.label }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Sentiment Chart -->
            <div class="mf-panel">
              <div class="mf-panel-head">
                <span class="mf-panel-title">Voter Sentiment · Live</span>
                <span class="mf-badge green">● STREAMING</span>
              </div>
              <div class="mf-panel-body">
                <svg ref="sentimentSvg" class="mf-svg" viewBox="0 0 300 160" />
              </div>
            </div>

            <!-- Demographics -->
            <div class="mf-panel">
              <div class="mf-panel-head">
                <span class="mf-panel-title">Voter Demographics · Booth 12</span>
                <span class="mf-badge amber">SECTOR C</span>
              </div>
              <div class="mf-panel-body mf-demo-body">
                <svg ref="demoSvg" class="mf-svg-fixed" viewBox="0 0 160 160" width="160" height="160" />
                <div class="mf-demo-legend">
                  <div v-for="d in demoData" :key="d.label" class="mf-demo-row">
                    <span class="mf-demo-sq" :style="{ background: d.color }" />
                    <span class="mf-demo-name">{{ d.label }}</span>
                    <span class="mf-demo-pct">{{ d.pct }}</span>
                  </div>
                  <div class="mf-demo-tag">BOOTH 12 · SECTOR C · ANNA NAGAR</div>
                </div>
              </div>
            </div>

            <!-- Ward Risk -->
            <div class="mf-panel">
              <div class="mf-panel-head">
                <span class="mf-panel-title">Ward Risk Index</span>
                <span class="mf-badge red">⚠ 3 CRITICAL</span>
              </div>
              <div class="mf-panel-body">
                <svg ref="wardSvg" class="mf-svg" viewBox="0 0 280 168" />
                <div class="mf-legend">
                  <span v-for="l in riskLegend" :key="l.label" class="mf-legend-item">
                    <span class="mf-sq" :style="{ background: l.color }" />{{ l.label }}
                  </span>
                </div>
              </div>
            </div>

          </div>

          <!-- FOOTER / CTA -->
          <div class="mf-footer">
            <div class="mf-constituency">
              <span class="mf-cslabel">CONSTITUENCY</span>
              <select v-model="constituency" class="mf-select">
                <option v-for="c in constituencies" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="mf-cta-row">
              <button class="mf-btn-secondary">VIEW FULL REPORT</button>
              <button class="mf-btn-primary" @click="bookDemo">BOOK FULL DEMO →</button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import * as d3 from 'd3'

/* ── OPEN/CLOSE ── */
const open = defineModel({ default: false })

/* ── ESC KEY ── */
const onKey = (e) => { if (e.key === 'Escape') open.value = false }
window.addEventListener('keydown', onKey)
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

/* ── STATS ── */
const stats = [
  { label: 'TOTAL AGENTS',    value: '2,841', color: '#00ccff' },
  { label: 'WARD COVERAGE',   value: '94.2%', color: '#00e676' },
  { label: 'WIN PROBABILITY', value: '63.7%', color: '#ffb300' },
  { label: 'DAYS TO VOTE',    value: '47',    color: '#ff1f44' },
]

/* ── TICKER ── */
const tickers = [
  '⚠  WARD 12  ·  HIGH RISK THRESHOLD BREACHED',
  '↑  INFLUENCER NODE A04 ACTIVATED  ·  +2.3% REACH DELTA',
  '↗  SENTIMENT SHIFT: SUPPORT +1.4% IN LAST 90 MIN',
  '●  247 NEW VOTER PROFILES INGESTED FROM BOOTH AGENTS',
  '✔  SIMULATION CYCLE #4,821 COMPLETE  ·  0 ERRORS',
  '⚠  OPPONENT ACTIVITY SPIKE DETECTED  ·  WARDS 07 & 19',
]
const tickerIdx = ref(0)
const isWarn = computed(() => tickers[tickerIdx.value].startsWith('⚠'))
let tickerTimer = setInterval(() => {
  tickerIdx.value = (tickerIdx.value + 1) % tickers.length
}, 3200)
onBeforeUnmount(() => clearInterval(tickerTimer))

/* ── LEGENDS ── */
const netLegend = [
  { label: 'Influencer', color: '#00ccff' },
  { label: 'Opponent',   color: '#ff1f44' },
  { label: 'Voter',      color: '#1d4a6b' },
]
const riskLegend = [
  { label: 'HIGH', color: '#ff1f44' },
  { label: 'MED',  color: '#ffb300' },
  { label: 'LOW',  color: '#00e676' },
]

/* ── DEMOGRAPHICS DATA ── */
const demoData = [
  { label: '18–25', pct: '22%', value: 22, color: '#00ccff'  },
  { label: '26–35', pct: '31%', value: 31, color: '#0099cc'  },
  { label: '36–50', pct: '28%', value: 28, color: '#005577'  },
  { label: '51+',   pct: '19%', value: 19, color: '#1c3348'  },
]

/* ── WARDS ── */
const wards = [
  { name: 'Ward 12', risk: 88 },
  { name: 'Ward 07', risk: 74 },
  { name: 'Ward 19', risk: 61 },
  { name: 'Ward 03', risk: 53 },
  { name: 'Ward 24', risk: 42 },
  { name: 'Ward 11', risk: 33 },
  { name: 'Ward 08', risk: 22 },
]
const riskColor = (v) => v > 70 ? '#ff1f44' : v > 50 ? '#ffb300' : '#00e676'

/* ── CONSTITUENCY ── */
const constituencies = [
  'Loyola College Ward (Demo)',
  'Anna Nagar East', 'Adyar', 'T. Nagar', 'Velachery', 'Mylapore',
]
const constituency = ref(constituencies[0])

/* ── BOOK DEMO ── */
const bookDemo = () => {
  window.open('https://wa.me/919XXXXXXXXX?text=Hi%2C+I%27d+like+to+book+a+full+MiroFish+demo', '_blank')
}

/* ── SVG REFS ── */
const networkSvg  = ref(null)
const sentimentSvg = ref(null)
const demoSvg     = ref(null)
const wardSvg     = ref(null)

/* ── SENTIMENT LIVE DATA ── */
const sentimentData = ref([])
let sentimentTimer = null
let sentimentPaths = {}

/* ── RENDER CHARTS WHEN MODAL OPENS ── */
watch(open, (val) => {
  if (!val) {
    clearInterval(sentimentTimer)
    return
  }
  // D3 renders need the DOM to be ready
  setTimeout(() => {
    renderNetwork()
    renderSentiment()
    renderDemographics()
    renderWards()
  }, 80)
})

/* ───────────────────────────────────────
   D3: NETWORK GRAPH
─────────────────────────────────────── */
function renderNetwork() {
  const el = networkSvg.value
  if (!el) return
  const W = 320, H = 190
  const nodes = Array.from({ length: 34 }, (_, i) => ({
    id: i, type: i < 4 ? 'influencer' : i < 13 ? 'opponent' : 'voter',
  }))
  const links = []
  for (let i = 0; i < 4; i++)
    for (let j = 4; j < 34; j++)
      if (Math.random() < 0.16) links.push({ source: i, target: j })
  for (let i = 4; i < 34; i++)
    for (let j = i + 1; j < 34; j++)
      if (Math.random() < 0.05) links.push({ source: i, target: j })

  const svg = d3.select(el)
  svg.selectAll('*').remove()

  const defs = svg.append('defs')
  const glow = defs.append('filter').attr('id', 'glow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%')
  glow.append('feGaussianBlur').attr('stdDeviation', 2.5).attr('result', 'blur')
  const merge = glow.append('feMerge')
  merge.append('feMergeNode').attr('in', 'blur')
  merge.append('feMergeNode').attr('in', 'SourceGraphic')

  const g = svg.append('g')
  const cMap = { influencer: '#00ccff', opponent: '#ff1f44', voter: '#1d4a6b' }
  const rMap = { influencer: 7, opponent: 5, voter: 3 }

  const link = g.append('g').selectAll('line').data(links).join('line')
    .attr('stroke', '#0b1929').attr('stroke-width', 0.5).attr('stroke-opacity', 0.7)

  g.append('g').selectAll('circle').data(nodes).join('circle')
    .attr('r', d => rMap[d.type])
    .attr('fill', d => cMap[d.type])
    .attr('fill-opacity', d => d.type === 'voter' ? 0.55 : 0.85)
    .attr('filter', d => d.type === 'influencer' ? 'url(#glow)' : 'none')

  const rings = g.append('g').selectAll('circle.ring')
    .data(nodes.filter(d => d.type === 'influencer')).join('circle')
    .attr('fill', 'none').attr('stroke', '#00ccff').attr('stroke-width', 0.8).attr('r', 7)

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(24))
    .force('charge', d3.forceManyBody().strength(-38))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collision', d3.forceCollide().radius(d => rMap[d.type] + 3))

  sim.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    g.selectAll('circle:not(.ring)').attr('cx', d => d.x).attr('cy', d => d.y)
    rings.attr('cx', d => d.x).attr('cy', d => d.y)
  })

  function pulse() {
    rings.transition().duration(1800).ease(d3.easeLinear)
      .attr('r', 22).attr('stroke-opacity', 0)
      .transition().duration(0).attr('r', 7).attr('stroke-opacity', 0.8)
      .on('end', pulse)
  }
  setTimeout(pulse, 600)
}

/* ───────────────────────────────────────
   D3: SENTIMENT LIVE CHART
─────────────────────────────────────── */
function renderSentiment() {
  const el = sentimentSvg.value
  if (!el) return
  const W = 300, H = 160
  const M = { t: 8, r: 8, b: 24, l: 26 }
  const iw = W - M.l - M.r, ih = H - M.t - M.b
  const N = 26

  let s = 44, n = 32
  sentimentData.value = Array.from({ length: N }, () => {
    s = Math.max(22, Math.min(63, s + (Math.random() - 0.44) * 2.5))
    n = Math.max(14, Math.min(42, n + (Math.random() - 0.5) * 2))
    return { s, n, o: 100 - s - n }
  })

  const svg = d3.select(el)
  svg.selectAll('*').remove()
  const g = svg.append('g').attr('transform', `translate(${M.l},${M.t})`)

  const x = d3.scaleLinear().domain([0, N - 1]).range([0, iw])
  const y = d3.scaleLinear().domain([0, 70]).range([ih, 0])

  ;[20, 40, 60].forEach(v => {
    g.append('line').attr('x1', 0).attr('x2', iw).attr('y1', y(v)).attr('y2', y(v))
      .attr('stroke', '#0b1929').attr('stroke-dasharray', '3,3')
  })
  g.append('g').call(d3.axisLeft(y).ticks(3).tickSize(0))
    .call(ag => ag.select('.domain').remove())
    .call(ag => ag.selectAll('text').attr('fill', '#1c3348').attr('font-size', 8).attr('font-family', 'Courier New'))
  g.append('g').attr('transform', `translate(0,${ih})`)
    .call(d3.axisBottom(x).ticks(4).tickSize(0))
    .call(ag => ag.select('.domain').remove())
    .call(ag => ag.selectAll('text').attr('fill', '#1c3348').attr('font-size', 8).attr('font-family', 'Courier New'))

  const series = [
    { key: 's', color: '#00ccff', label: 'Support' },
    { key: 'n', color: '#ffb300', label: 'Neutral' },
    { key: 'o', color: '#ff1f44', label: 'Oppose'  },
  ]
  series.forEach(({ key, color }) => {
    const gen = d3.line().x((d, i) => x(i)).y(d => y(d[key])).curve(d3.curveCatmullRom)
    sentimentPaths[key] = g.append('path')
      .datum(sentimentData.value).attr('fill', 'none').attr('stroke', color)
      .attr('stroke-width', 1.6).attr('d', gen)
  })
  series.forEach(({ color, label }, i) => {
    const lx = iw - 148 + i * 52
    g.append('line').attr('x1', lx).attr('x2', lx + 10).attr('y1', ih + 16).attr('y2', ih + 16)
      .attr('stroke', color).attr('stroke-width', 2)
    g.append('text').attr('x', lx + 13).attr('y', ih + 20).attr('fill', '#1c3348')
      .attr('font-size', 8).attr('font-family', 'Courier New').text(label)
  })

  sentimentTimer = setInterval(() => {
    const prev = sentimentData.value[sentimentData.value.length - 1]
    const ns = Math.max(22, Math.min(63, prev.s + (Math.random() - 0.44) * 2.5))
    const nn = Math.max(14, Math.min(42, prev.n + (Math.random() - 0.5) * 2))
    sentimentData.value = [...sentimentData.value.slice(1), { s: ns, n: nn, o: 100 - ns - nn }]
    series.forEach(({ key }) => {
      const gen = d3.line().x((d, i) => x(i)).y(d => y(d[key])).curve(d3.curveCatmullRom)
      sentimentPaths[key].transition().duration(900).attr('d', gen(sentimentData.value))
    })
  }, 2000)
}

/* ───────────────────────────────────────
   D3: DEMOGRAPHICS DONUT
─────────────────────────────────────── */
function renderDemographics() {
  const el = demoSvg.value
  if (!el) return
  const W = 160, H = 160, R = Math.min(W, H) / 2 - 10
  const svg = d3.select(el)
  svg.selectAll('*').remove()
  const g = svg.append('g').attr('transform', `translate(${W / 2},${H / 2})`)
  const pie = d3.pie().value(d => d.value).sort(null).padAngle(0.04)
  const arc = d3.arc().innerRadius(R * 0.56).outerRadius(R)

  g.selectAll('path').data(pie(demoData)).join('path')
    .attr('fill', d => d.data.color).attr('stroke', '#04080f').attr('stroke-width', 2)
    .attr('d', arc).attr('opacity', 0)
    .transition().duration(550).delay((_, i) => i * 110).attr('opacity', 1)

  g.append('text').attr('text-anchor', 'middle').attr('dy', '-0.3em')
    .attr('fill', '#ddf0ff').attr('font-size', 17).attr('font-family', 'Courier New').attr('font-weight', 'bold').text('182K')
  g.append('text').attr('text-anchor', 'middle').attr('dy', '1.1em')
    .attr('fill', '#1c3348').attr('font-size', 7.5).attr('font-family', 'Courier New').text('REGISTERED')
}

/* ───────────────────────────────────────
   D3: WARD RISK BARS
─────────────────────────────────────── */
function renderWards() {
  const el = wardSvg.value
  if (!el) return
  const W = 280, H = 168, M = { t: 4, r: 34, b: 4, l: 50 }
  const iw = W - M.l - M.r, ih = H - M.t - M.b
  const svg = d3.select(el)
  svg.selectAll('*').remove()
  const g = svg.append('g').attr('transform', `translate(${M.l},${M.t})`)
  const x = d3.scaleLinear().domain([0, 100]).range([0, iw])
  const y = d3.scaleBand().domain(wards.map(d => d.name)).range([0, ih]).padding(0.3)

  g.selectAll('rect.bg').data(wards).join('rect')
    .attr('x', 0).attr('y', d => y(d.name)).attr('width', iw).attr('height', y.bandwidth())
    .attr('fill', '#0b1929').attr('rx', 2)
  g.selectAll('rect.bar').data(wards).join('rect')
    .attr('x', 0).attr('y', d => y(d.name)).attr('width', 0).attr('height', y.bandwidth())
    .attr('fill', d => riskColor(d.risk)).attr('fill-opacity', 0.72).attr('rx', 2)
    .transition().duration(650).delay((_, i) => i * 75).attr('width', d => x(d.risk))
  g.selectAll('text.name').data(wards).join('text')
    .attr('x', -5).attr('y', d => y(d.name) + y.bandwidth() / 2).attr('dy', '0.35em')
    .attr('text-anchor', 'end').attr('fill', '#6a9ab8').attr('font-size', 9).attr('font-family', 'Courier New').text(d => d.name)
  g.selectAll('text.val').data(wards).join('text')
    .attr('x', d => x(d.risk) + 4).attr('y', d => y(d.name) + y.bandwidth() / 2)
    .attr('dy', '0.35em').attr('fill', d => riskColor(d.risk))
    .attr('font-size', 9).attr('font-family', 'Courier New').attr('font-weight', 'bold')
    .attr('opacity', 0).transition().delay((_, i) => i * 75 + 400).duration(300)
    .attr('opacity', 1).text(d => d.risk)
}
</script>

<style scoped>
/* ── BACKDROP + MODAL ── */
.mf-backdrop {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.88);
  display: flex; align-items: center; justify-content: center;
  padding: 12px;
  backdrop-filter: blur(3px);
}
.mf-modal {
  width: 100%; max-width: 860px; max-height: 96vh;
  background: #04080f;
  border: 1px solid #162b42;
  display: flex; flex-direction: column;
  box-shadow: 0 0 80px rgba(0,0,0,0.9);
  overflow: hidden;
}

/* ── TRANSITION ── */
.mf-fade-enter-active, .mf-fade-leave-active { transition: opacity 0.22s ease, transform 0.22s ease; }
.mf-fade-enter-from, .mf-fade-leave-to { opacity: 0; transform: scale(0.97); }

/* ── HEADER ── */
.mf-header {
  padding: 9px 14px; border-bottom: 1px solid #0b1929;
  background: #02060e;
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0;
}
.mf-header-left { display: flex; align-items: center; gap: 10px; }
.mf-live-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #ff1f44;
  box-shadow: 0 0 5px #ff1f44;
  animation: mf-blink 1.1s step-end infinite;
  display: inline-block;
}
.mf-live-label  { font-family: 'Courier New', monospace; font-size: 9px; color: #ff1f44; letter-spacing: 2px; }
.mf-divider     { color: #1c3348; }
.mf-brand       { font-family: 'Courier New', monospace; font-size: 13px; color: #00ccff; letter-spacing: 4px; font-weight: bold; }
.mf-subtitle    { font-family: 'Courier New', monospace; font-size: 9px; color: #1c3348; letter-spacing: 2px; }
.mf-close {
  background: none; border: 1px solid #0b1929; color: #6a9ab8;
  cursor: pointer; font-family: 'Courier New', monospace; font-size: 10px;
  padding: 3px 9px; transition: all 0.15s;
}
.mf-close:hover { background: #162b42; color: #ddf0ff; }

/* ── STAT BAR ── */
.mf-statbar { display: grid; grid-template-columns: repeat(4,1fr); gap: 1px; background: #0b1929; flex-shrink: 0; }
.mf-stat    { background: #060c17; padding: 8px 10px; text-align: center; }
.mf-stat-value { font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold; line-height: 1; }
.mf-stat-label { font-family: 'Courier New', monospace; font-size: 8px; color: #1c3348; margin-top: 3px; letter-spacing: 1px; }

/* ── TICKER ── */
.mf-ticker {
  background: #0b1929; padding: 4px 14px;
  display: flex; align-items: center; gap: 10px;
  font-family: 'Courier New', monospace; font-size: 10px;
  overflow: hidden; flex-shrink: 0;
}
.mf-ticker > .mf-blink { color: #ff1f44; font-weight: bold; flex-shrink: 0; animation: mf-blink 1.1s step-end infinite; }
.mf-ticker-text { color: #6a9ab8; white-space: nowrap; }
.mf-ticker-text.warn { color: #ffb300; }
.mf-tick-enter-active { animation: mf-tick-in 0.35s ease; }
.mf-tick-leave-active { animation: mf-tick-out 0.25s ease; position: absolute; }
@keyframes mf-tick-in  { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
@keyframes mf-tick-out { from { opacity:1 } to { opacity:0 } }

/* ── CHARTS GRID ── */
.mf-grid {
  display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr;
  gap: 1px; background: #0b1929; flex: 1; overflow: hidden; min-height: 0;
}
.mf-panel { background: #060c17; display: flex; flex-direction: column; overflow: hidden; }
.mf-panel-head {
  padding: 5px 10px; border-bottom: 1px solid #0b1929;
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
}
.mf-panel-title { font-family: 'Courier New', monospace; font-size: 8px; color: #1c3348; letter-spacing: 2px; text-transform: uppercase; }
.mf-panel-body  { flex: 1; padding: 8px; min-height: 0; display: flex; flex-direction: column; }
.mf-svg         { flex: 1; min-height: 0; }
.mf-svg-fixed   { flex-shrink: 0; }
.mf-demo-body   { flex-direction: row !important; align-items: center; gap: 10px; }
.mf-demo-legend { flex: 1; }
.mf-demo-row    { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.mf-demo-sq     { width: 7px; height: 7px; border-radius: 1px; flex-shrink: 0; }
.mf-demo-name   { font-family: 'Courier New', monospace; font-size: 9px; color: #6a9ab8; flex: 1; }
.mf-demo-pct    { font-family: 'Courier New', monospace; font-size: 12px; color: #b8d4e8; font-weight: bold; }
.mf-demo-tag    { margin-top: 10px; padding: 4px 8px; background: rgba(0,204,255,0.08); border-left: 2px solid #00ccff; font-family: 'Courier New', monospace; font-size: 7.5px; color: #6a9ab8; }

/* ── BADGES ── */
.mf-badge { font-family: 'Courier New', monospace; font-size: 8px; padding: 1px 7px; letter-spacing: 1px; }
.mf-badge.cyan   { color: #00ccff; background: rgba(0,204,255,0.1); }
.mf-badge.green  { color: #00e676; background: rgba(0,230,118,0.1); }
.mf-badge.amber  { color: #ffb300; background: rgba(255,179,0,0.1); }
.mf-badge.red    { color: #ff1f44; background: rgba(255,31,68,0.1); }

/* ── LEGEND ── */
.mf-legend { display: flex; gap: 12px; padding-top: 4px; flex-shrink: 0; }
.mf-legend-item { display: flex; align-items: center; gap: 4px; font-family: 'Courier New', monospace; font-size: 8px; color: #1c3348; }
.mf-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.mf-sq  { width: 6px; height: 6px; display: inline-block; }

/* ── FOOTER ── */
.mf-footer {
  padding: 10px 14px; border-top: 1px solid #0b1929; background: #02060e;
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; flex-wrap: wrap; flex-shrink: 0;
}
.mf-constituency { display: flex; align-items: center; gap: 8px; }
.mf-cslabel { font-family: 'Courier New', monospace; font-size: 8px; color: #1c3348; }
.mf-select {
  font-family: 'Courier New', monospace; font-size: 9px;
  background: #060c17; border: 1px solid #162b42; color: #b8d4e8;
  padding: 3px 8px; cursor: pointer; outline: none;
}
.mf-cta-row { display: flex; gap: 8px; }
.mf-btn-secondary {
  font-family: 'Courier New', monospace; font-size: 10px; padding: 8px 16px;
  background: none; border: 1px solid #162b42; color: #6a9ab8;
  cursor: pointer; letter-spacing: 1px; transition: all 0.15s;
}
.mf-btn-secondary:hover { border-color: #00ccff; color: #00ccff; }
.mf-btn-primary {
  font-family: 'Courier New', monospace; font-size: 10px; padding: 8px 20px;
  background: #00ccff; border: none; color: #02060e;
  cursor: pointer; font-weight: bold; letter-spacing: 1px; transition: all 0.15s;
}
.mf-btn-primary:hover { opacity: 0.88; transform: translateY(-1px); }

/* ── ANIMATIONS ── */
@keyframes mf-blink { 0%,100% { opacity:1 } 50% { opacity:0.15 } }
</style>
