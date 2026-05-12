// Thai Oil Prices — frontend with animations
const BRANDS = [
  { id: 'ptt',      name: 'PTT',      color: '#0066b3', emoji: '🔵' },
  { id: 'bangchak', name: 'Bangchak', color: '#00a651', emoji: '🟢' },
  { id: 'shell',    name: 'Shell',    color: '#d4a017', emoji: '🟡' },
  { id: 'esso',     name: 'Esso',     color: '#ed1c24', emoji: '🔴' },
  { id: 'caltex',   name: 'Caltex',   color: '#003da6', emoji: '🔷' },
];

const FUEL_TYPES = [
  { id: 'diesel_b7',      name: 'ดีเซล B7' },
  { id: 'diesel_b20',     name: 'ดีเซล B20' },
  { id: 'premium_diesel', name: 'พรีเมียมดีเซล' },
];

let DATA = null;
let activeFuel = 'diesel_b7';
const expandedBrands = new Set();
let chart = null;
let barChart = null;

// ===== utilities =====
async function loadData() {
  const res = await fetch(`data/prices.json?t=${Date.now()}`);
  DATA = await res.json();
}

const fmtPrice = (p) => (p == null ? '–' : p.toFixed(2));

function getSnapshots() {
  const days = Object.keys(DATA.history).sort();
  const today = days[days.length - 1];
  const yest  = days.length >= 2 ? days[days.length - 2] : null;
  return {
    todayKey: today,
    yestKey:  yest,
    today: DATA.history[today],
    yest:  yest ? DATA.history[yest] : null,
  };
}

// Smooth number tween. Calls `setter(value)` on each frame.
function tweenNumber(from, to, ms, setter) {
  if (from == null || isNaN(from)) { setter(to); return; }
  if (to == null || isNaN(to)) { setter(to); return; }
  const start = performance.now();
  function frame(now) {
    const t = Math.min(1, (now - start) / ms);
    const eased = 1 - Math.pow(1 - t, 3);            // ease-out cubic
    setter(from + (to - from) * eased);
    if (t < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

// Add a ripple where the user clicked (relative to element)
function addRipple(el, ev) {
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = (ev.clientX ?? rect.left + rect.width/2) - rect.left - size/2;
  const y = (ev.clientY ?? rect.top + rect.height/2) - rect.top - size/2;
  const r = document.createElement('span');
  r.className = 'ripple';
  r.style.width = r.style.height = size + 'px';
  r.style.left = x + 'px';
  r.style.top  = y + 'px';
  el.appendChild(r);
  setTimeout(() => r.remove(), 650);
}

function diffBadge(today, yest) {
  if (today == null || yest == null) return '<span class="price-same text-xs">—</span>';
  const d = today - yest;
  if (Math.abs(d) < 0.001) return '<span class="price-same text-xs">▬ 0.00</span>';
  if (d > 0) return `<span class="price-up text-xs font-semibold"><span class="arrow-up">▲</span> +${d.toFixed(2)}</span>`;
  return `<span class="price-down text-xs font-semibold"><span class="arrow-down">▼</span> ${d.toFixed(2)}</span>`;
}

// ===== Fuel tabs =====
function renderFuelTabs() {
  const tabs = document.getElementById('fuel-tabs');
  tabs.innerHTML = FUEL_TYPES.map(f => `
    <button data-fuel="${f.id}"
            class="fuel-tab ripple-host px-3 py-1.5 rounded-full text-sm font-medium
                   ${f.id === activeFuel ? 'active' : 'bg-slate-100 text-slate-700'}">
      ${f.name}
    </button>`).join('');
  tabs.querySelectorAll('.fuel-tab').forEach(btn => {
    btn.onclick = (ev) => {
      addRipple(btn, ev);
      if (btn.dataset.fuel === activeFuel) return;
      activeFuel = btn.dataset.fuel;
      renderFuelTabs();
      animateCardSwap();
      renderBrandsBar();
    };
  });
}

// ===== Brand cards =====
function cardHtml(b, snap, prevSnap) {
  const tp = snap?.[b.id]?.[activeFuel];
  const yp = prevSnap?.[b.id]?.[activeFuel];
  const fuelName = FUEL_TYPES.find(f => f.id === activeFuel)?.name;
  const detailRows = FUEL_TYPES.map(f => {
    const v = snap?.[b.id]?.[f.id];
    const py = prevSnap?.[b.id]?.[f.id];
    return `
      <div class="flex justify-between items-center py-1 border-b border-slate-100 last:border-0 text-sm">
        <span class="text-slate-600">${f.name}</span>
        <span class="flex items-baseline gap-2">
          <span class="font-semibold">${fmtPrice(v)}</span>
          ${diffBadge(v, py)}
        </span>
      </div>`;
  }).join('');
  const expanded = expandedBrands.has(b.id) ? 'expanded' : '';
  return `
    <div class="brand-card ripple-host bg-white rounded-xl shadow p-5 border-l-4 ${expanded}"
         data-brand="${b.id}" style="border-color:${b.color}; color:${b.color}">
      <div class="flex items-center justify-between mb-2 text-slate-800">
        <div class="font-bold text-lg">${b.emoji} ${b.name}</div>
        <div class="flex items-center gap-2">
          ${diffBadge(tp, yp)}
          <span class="chevron text-xs">▼</span>
        </div>
      </div>
      <div class="text-xs text-slate-500 mb-1">${fuelName}</div>
      <div class="text-4xl font-bold price-num"
           data-num data-from="${tp ?? ''}" style="color:${b.color}">
        ${fmtPrice(tp)}
        <span class="text-base font-normal text-slate-400 ml-1">บาท/ลิตร</span>
      </div>
      <div class="text-xs text-slate-400 mt-2">เมื่อวาน: ${fmtPrice(yp)}</div>
      <div class="details bg-slate-50/60 rounded-lg px-3 pt-2 pb-1">
        <div class="text-xs text-slate-500 mb-1">ราคาทุกชนิดน้ำมัน</div>
        ${detailRows}
      </div>
    </div>`;
}

function renderBrandCards(stagger = true) {
  const { today, yest } = getSnapshots();
  const wrap = document.getElementById('brand-cards');
  wrap.innerHTML = BRANDS.map(b => cardHtml(b, today, yest)).join('');

  const cards = wrap.querySelectorAll('.brand-card');
  cards.forEach((card, i) => {
    if (stagger) {
      card.classList.add('anim-in');
      card.style.animationDelay = (0.08 * i + 0.08) + 's';
    }
    card.addEventListener('click', (ev) => {
      // ignore clicks inside the details panel rows
      if (ev.target.closest('.details') && expandedBrands.has(card.dataset.brand)) return;
      addRipple(card, ev);
      const bid = card.dataset.brand;
      if (expandedBrands.has(bid)) expandedBrands.delete(bid);
      else expandedBrands.add(bid);
      card.classList.toggle('expanded');
    });
  });
}

// Swap fuel — tween price numbers from old to new instead of jumping
function animateCardSwap() {
  const { today, yest } = getSnapshots();
  const wrap = document.getElementById('brand-cards');
  const cards = wrap.querySelectorAll('.brand-card');
  cards.forEach(card => {
    const bid = card.dataset.brand;
    const tp = today?.[bid]?.[activeFuel];
    const yp = yest?.[bid]?.[activeFuel];

    // tween big price number
    const priceEl = card.querySelector('[data-num]');
    const oldVal = parseFloat(priceEl.dataset.from);
    priceEl.dataset.from = tp == null ? '' : tp;
    const suffix = `<span class="text-base font-normal text-slate-400 ml-1">บาท/ลิตร</span>`;
    if (tp == null) {
      priceEl.innerHTML = '–' + suffix;
    } else {
      tweenNumber(isNaN(oldVal) ? tp : oldVal, tp, 450, v => {
        priceEl.innerHTML = v.toFixed(2) + suffix;
      });
    }

    // update fuel-name caption
    const fuelLabel = card.querySelector('.text-xs.text-slate-500');
    if (fuelLabel) fuelLabel.textContent = FUEL_TYPES.find(f => f.id === activeFuel).name;

    // update "เมื่อวาน" line
    const yLine = card.querySelectorAll('.text-xs.text-slate-400')[0];
    if (yLine) yLine.textContent = `เมื่อวาน: ${fmtPrice(yp)}`;

    // update diff badge (top right)
    const badgeHost = card.querySelector('.flex.items-center.gap-2');
    if (badgeHost) badgeHost.firstElementChild.outerHTML = diffBadge(tp, yp);

    // flash highlight if value changed
    if (tp != null && yp != null && Math.abs(tp - yp) > 0.001) {
      priceEl.classList.remove('flash'); void priceEl.offsetWidth; priceEl.classList.add('flash');
    }
  });
}

// ===== Comparison table =====
function renderCompareTable() {
  const { today, yest } = getSnapshots();
  const tbl = document.getElementById('compare-table');
  tbl.querySelector('thead').innerHTML = `
    <tr class="bg-gradient-to-r from-slate-100 to-slate-50 text-slate-700">
      <th class="text-left p-2 font-semibold rounded-l-lg">ชนิด \\ แบรนด์</th>
      ${BRANDS.map((b,i) => `<th class="p-2 text-center ${i===BRANDS.length-1?'rounded-r-lg':''}"
                                  style="color:${b.color}">${b.name}</th>`).join('')}
    </tr>`;
  tbl.querySelector('tbody').innerHTML = FUEL_TYPES.map(f => `
    <tr class="border-t border-slate-100">
      <td class="p-2 font-medium text-slate-700">${f.name}</td>
      ${BRANDS.map(b => {
        const tp = today?.[b.id]?.[f.id];
        const yp = yest?.[b.id]?.[f.id];
        if (tp == null) return `<td class="p-2 text-center text-slate-300">–</td>`;
        return `<td class="p-2 text-center">
          <div class="font-semibold">${fmtPrice(tp)}</div>
          <div>${diffBadge(tp, yp)}</div>
        </td>`;
      }).join('')}
    </tr>`).join('');
}

// ===== Bar chart: brands today =====
function renderBrandsBar() {
  const { today } = getSnapshots();
  const fuel = activeFuel;
  const labels = BRANDS.map(b => b.name);
  const values = BRANDS.map(b => today?.[b.id]?.[fuel] ?? null);
  const colors = BRANDS.map(b => b.color);

  document.getElementById('bar-fuel-label').textContent =
      FUEL_TYPES.find(f => f.id === fuel)?.name ?? fuel;

  // Compute a sensible y-axis range:
  //   - pad ~5 baht below the lowest value (but never below 0)
  //   - pad ~2 baht above the highest value
  // This avoids the auto-fit problem where similar values get exaggerated
  // (e.g. all 42.45 except one 42.95 → tiny bars + one giant bar).
  const valid = values.filter(v => v != null);
  let yMin = 0, yMax = 1;
  if (valid.length) {
    const lo = Math.min(...valid);
    const hi = Math.max(...valid);
    yMin = Math.max(0, Math.floor(lo - 5));
    yMax = Math.ceil(hi + 2);
    // Avoid a too-tight range when all values are identical
    if (yMax - yMin < 6) yMax = yMin + 6;
  }

  const ctx = document.getElementById('brands-bar');
  if (!ctx) return;
  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'ราคา (บาท/ลิตร)',
        data: values,
        backgroundColor: colors.map(c => c + 'cc'),
        borderColor:     colors,
        borderWidth: 2,
        borderRadius: 8,
        maxBarThickness: 90,
      }]
    },
    options: {
      maintainAspectRatio: false, responsive: true,
      layout: { padding: { top: 24 } },
      animation: { duration: 600, easing: 'easeOutBack' },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: c => (c.parsed.y == null ? 'ไม่มีข้อมูล' : c.parsed.y.toFixed(2) + ' บาท/ลิตร'),
          },
        },
      },
      scales: {
        y: {
          min: yMin,
          max: yMax,
          ticks: { callback: v => v.toFixed(2), stepSize: Math.max(1, Math.round((yMax - yMin) / 6)) },
          grid: { color: '#f1f5f9' },
        },
        x: { grid: { display: false } },
      },
    },
    plugins: [{
      id: 'valueLabel',
      afterDatasetsDraw(c) {
        const { ctx } = c;
        c.data.datasets[0].data.forEach((v, i) => {
          if (v == null) return;
          const bar = c.getDatasetMeta(0).data[i];
          ctx.save();
          ctx.fillStyle = colors[i];
          ctx.font = '600 14px Comfortaa, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(v.toFixed(2), bar.x, bar.y - 8);
          ctx.restore();
        });
      },
    }],
  });
}

// ===== Chart: history =====
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
        data: prices,
        borderColor: color,
        backgroundColor: color + '20',
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointBackgroundColor: color,
        spanGaps: true,
        borderWidth: 2.5,
      }]
    },
    options: {
      maintainAspectRatio: false, responsive: true,
      animation: { duration: 700, easing: 'easeOutQuart' },
      plugins: { legend: { position: 'top' } },
      scales: { y: { ticks: { callback: v => v.toFixed(2) } } },
    }
  });
}

function renderAll() {
  renderFuelTabs();
  renderBrandCards(true);
  renderBrandsBar();
  renderCompareTable();
  renderChart();
}

(async () => {
  try {
    await loadData();
    const { todayKey } = getSnapshots();
    document.getElementById('last-updated').textContent = todayKey;
    renderAll();
  } catch (e) {
    document.body.innerHTML = `<div class="p-8 text-center">
      <h1 class="text-2xl font-bold text-red-600">ไม่สามารถโหลดข้อมูลได้</h1>
      <p class="mt-2 text-slate-600">รอ scheduled scrape รันครั้งแรก</p>
      <pre class="mt-4 text-xs text-left bg-slate-100 p-3 rounded">${e.message}</pre>
    </div>`;
  }
})();
