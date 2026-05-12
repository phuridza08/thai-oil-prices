// Thai Oil Prices — frontend
const BRANDS = [
  { id: 'ptt',      name: 'PTT',      color: '#0066b3', emoji: '🔵' },
  { id: 'bangchak', name: 'Bangchak', color: '#00a651', emoji: '🟢' },
  { id: 'shell',    name: 'Shell',    color: '#fbcc04', emoji: '🟡' },
  { id: 'esso',     name: 'Esso',     color: '#ed1c24', emoji: '🔴' },
  { id: 'caltex',   name: 'Caltex',   color: '#003da6', emoji: '🔷' },
];

const FUEL_TYPES = [
  { id: 'gasoline_95', name: 'เบนซิน 95' },
  { id: 'gasohol_95',  name: 'แก๊สโซฮอล์ 95' },
  { id: 'gasohol_91',  name: 'แก๊สโซฮอล์ 91' },
  { id: 'e20',         name: 'E20' },
  { id: 'e85',         name: 'E85' },
  { id: 'diesel_b7',   name: 'ดีเซล B7' },
  { id: 'diesel_b20',  name: 'ดีเซล B20' },
  { id: 'premium_diesel', name: 'พรีเมียมดีเซล' },
];

let DATA = null;
let activeFuel = 'gasohol_95';
let chart = null;

async function loadData() {
  const res = await fetch(`data/prices.json?t=${Date.now()}`);
  DATA = await res.json();
}

function fmtPrice(p) {
  return (p == null) ? '–' : p.toFixed(2);
}

function diffBadge(today, yesterday) {
  if (today == null || yesterday == null) return '<span class="price-same text-xs">—</span>';
  const d = today - yesterday;
  if (Math.abs(d) < 0.001) return '<span class="price-same text-xs">▬ 0.00</span>';
  if (d > 0) return `<span class="price-up text-xs font-semibold">▲ +${d.toFixed(2)}</span>`;
  return `<span class="price-down text-xs font-semibold">▼ ${d.toFixed(2)}</span>`;
}

function renderFuelTabs() {
  const tabs = document.getElementById('fuel-tabs');
  tabs.innerHTML = FUEL_TYPES.map(f => `
    <button data-fuel="${f.id}"
      class="fuel-tab px-3 py-1.5 rounded-full text-sm font-medium transition
             ${f.id === activeFuel
                ? 'bg-sky-600 text-white shadow'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-700'}">
      ${f.name}
    </button>`).join('');
  tabs.querySelectorAll('.fuel-tab').forEach(b =>
    b.onclick = () => { activeFuel = b.dataset.fuel; renderAll(); });
}

function getLatestSnapshot() {
  const days = Object.keys(DATA.history).sort();
  return { date: days[days.length-1], data: DATA.history[days[days.length-1]] };
}
function getPreviousSnapshot() {
  const days = Object.keys(DATA.history).sort();
  if (days.length < 2) return null;
  return { date: days[days.length-2], data: DATA.history[days[days.length-2]] };
}

function renderBrandCards() {
  const today = getLatestSnapshot();
  const yest  = getPreviousSnapshot();
  const wrap = document.getElementById('brand-cards');
  wrap.innerHTML = BRANDS.map(b => {
    const tp = today?.data?.[b.id]?.[activeFuel];
    const yp = yest?.data?.[b.id]?.[activeFuel];
    const fuelName = FUEL_TYPES.find(f => f.id === activeFuel)?.name;
    return `
      <div class="bg-white rounded-xl shadow hover:shadow-lg transition p-5 border-l-4"
           style="border-color: ${b.color}">
        <div class="flex items-center justify-between mb-2">
          <div class="font-bold text-slate-700 text-lg">${b.emoji} ${b.name}</div>
          ${diffBadge(tp, yp)}
        </div>
        <div class="text-xs text-slate-500 mb-1">${fuelName}</div>
        <div class="text-4xl font-bold" style="color: ${b.color}">
          ${fmtPrice(tp)}
          <span class="text-base font-normal text-slate-400 ml-1">บาท/ลิตร</span>
        </div>
        <div class="text-xs text-slate-400 mt-2">
          เมื่อวาน: ${fmtPrice(yp)}
        </div>
      </div>`;
  }).join('');
}

function renderCompareTable() {
  const today = getLatestSnapshot();
  const yest  = getPreviousSnapshot();
  const tbl = document.getElementById('compare-table');
  const thead = tbl.querySelector('thead');
  const tbody = tbl.querySelector('tbody');

  thead.innerHTML = `
    <tr class="bg-slate-100 text-slate-700">
      <th class="text-left p-2 font-semibold">ชนิด \\ แบรนด์</th>
      ${BRANDS.map(b => `<th class="p-2 text-center" style="color:${b.color}">${b.name}</th>`).join('')}
    </tr>`;
  tbody.innerHTML = FUEL_TYPES.map(f => `
    <tr class="border-t hover:bg-sky-50/40">
      <td class="p-2 font-medium text-slate-700">${f.name}</td>
      ${BRANDS.map(b => {
        const tp = today?.data?.[b.id]?.[f.id];
        const yp = yest?.data?.[b.id]?.[f.id];
        if (tp == null) return `<td class="p-2 text-center text-slate-300">–</td>`;
        return `<td class="p-2 text-center">
          <div class="font-semibold">${fmtPrice(tp)}</div>
          <div>${diffBadge(tp, yp)}</div>
        </td>`;
      }).join('')}
    </tr>`).join('');
}

function renderChart() {
  const brandSel = document.getElementById('chart-brand');
  const fuelSel  = document.getElementById('chart-fuel');
  if (!brandSel.options.length) {
    BRANDS.forEach(b => brandSel.add(new Option(b.name, b.id)));
    FUEL_TYPES.forEach(f => fuelSel.add(new Option(f.name, f.id)));
    fuelSel.value = activeFuel;
    brandSel.onchange = renderChart;
    fuelSel.onchange  = renderChart;
  }
  const brand = brandSel.value, fuel = fuelSel.value;
  const days = Object.keys(DATA.history).sort();
  const labels = days.map(d => d.slice(5));
  const prices = days.map(d => DATA.history[d]?.[brand]?.[fuel] ?? null);

  const color = BRANDS.find(b => b.id === brand)?.color || '#0284c7';
  if (chart) chart.destroy();
  chart = new Chart(document.getElementById('history-chart'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: `${BRANDS.find(b=>b.id===brand).name} — ${FUEL_TYPES.find(f=>f.id===fuel).name}`,
        data: prices, borderColor: color,
        backgroundColor: color + '20', fill: true, tension: 0.3,
        pointRadius: 3, pointHoverRadius: 6, spanGaps: true,
      }]
    },
    options: {
      maintainAspectRatio: false, responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: { y: { ticks: { callback: v => v.toFixed(2) } } },
    }
  });
}

function renderAll() {
  renderFuelTabs();
  renderBrandCards();
  renderCompareTable();
  renderChart();
}

(async () => {
  try {
    await loadData();
    const latest = getLatestSnapshot();
    document.getElementById('last-updated').textContent = latest.date;
    renderAll();
  } catch (e) {
    document.body.innerHTML = `<div class="p-8 text-center">
      <h1 class="text-2xl font-bold text-red-600">ไม่สามารถโหลดข้อมูลได้</h1>
      <p class="mt-2 text-slate-600">รอ GitHub Action รันครั้งแรกที่ 07:00 น. หรือกดรัน workflow มือ</p>
      <pre class="mt-4 text-xs text-left bg-slate-100 p-3 rounded">${e.message}</pre>
    </div>`;
  }
})();
