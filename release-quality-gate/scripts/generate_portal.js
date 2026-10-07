#!/usr/bin/env node
/**
 * Universal Release Quality Gate Portal Generator
 * Part of skill: release-quality-gate
 * Standalone Node.js script (Zero external dependencies)
 */

const fs = require('fs');
const path = require('path');

function getArg(name, defaultValue = '') {
  const prefix = `--${name}=`;
  const arg = process.argv.find((a) => a.startsWith(prefix));
  return arg ? arg.slice(prefix.length) : defaultValue;
}

const inputPath = getArg('input') || path.join(__dirname, '..', 'templates', 'sample_cases.json');
const outputPath = getArg('output') || path.join(process.cwd(), 'Release_Quality_Gate_Portal.html');
const evidencePath = getArg('evidence', '');

if (!fs.existsSync(inputPath)) {
  console.error(`[ERROR] File input không tồn tại: ${inputPath}`);
  process.exit(1);
}

const rawData = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

// Optional evidence merge
if (evidencePath && fs.existsSync(evidencePath)) {
  try {
    const evidenceData = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));
    console.log(`[INFO] Merging evidence from: ${evidencePath}`);
    const resultsMap = new Map();
    if (Array.isArray(evidenceData)) {
      evidenceData.forEach(item => resultsMap.set(item.id, item));
    } else if (Array.isArray(evidenceData.results)) {
      evidenceData.results.forEach(item => resultsMap.set(item.id, item));
    } else if (Array.isArray(evidenceData.cases)) {
      evidenceData.cases.forEach(item => resultsMap.set(item.id, item));
    }

    if (Array.isArray(rawData.testCases)) {
      rawData.testCases.forEach(tc => {
        if (resultsMap.has(tc.id)) {
          const ev = resultsMap.get(tc.id);
          tc.status = (ev.status || (ev.passed ? 'PASSED' : 'FAILED')).toUpperCase();
          tc.actual = ev.actual || ev.response || tc.actual;
          tc.evidence = ev.evidence || ev.detail || (ev.durationMs ? `Duration: ${ev.durationMs}ms` : tc.evidence);
        }
      });
    }
  } catch (err) {
    console.warn(`[WARN] Không thể merge evidence: ${err.message}`);
  }
}

const projectName = rawData.projectName || 'Software Project';
const version = rawData.version || '1.0.0';
const releaseDate = rawData.releaseDate || new Date().toISOString().split('T')[0];
const targetDomain = rawData.targetDomain || 'https://example.com';
const checklistSections = rawData.checklistSections || [];
const testCases = rawData.testCases || [];

const htmlContent = `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${projectName} - Release Verification & Quality Gate Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }
    code, pre, .font-mono { font-family: 'JetBrains Mono', monospace; }
    .badge-blocker { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .badge-p1 { background: #ffedd5; color: #9a3412; border: 1px solid #fb923c; }
    .badge-p2 { background: #fef9c3; color: #854d0e; border: 1px solid #facc15; }
    .badge-p3 { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .tab-active { border-bottom: 3px solid #2563eb; color: #1d4ed8; font-weight: 700; }
    
    @media print {
      .no-print { display: none !important; }
      body { background: white !important; color: black !important; font-size: 11px !important; }
      .tab-content { display: block !important; }
      .shadow-sm, .shadow-xl, .shadow-md { box-shadow: none !important; }
      table { border: 1px solid #ddd !important; }
      th, td { border: 1px solid #eee !important; padding: 4px !important; }
    }
  </style>
</head>
<body class="bg-slate-100 text-slate-800 min-h-screen">

  <!-- Top Executive Header -->
  <header class="bg-slate-900 text-white sticky top-0 z-50 shadow-2xl border-b border-slate-800 no-print">
    <div class="max-w-[1750px] mx-auto px-4 sm:px-6 py-3 flex flex-wrap justify-between items-center gap-4">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
          <i class="fa-solid fa-shield-halved text-xl"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-base font-extrabold tracking-tight">${projectName}</h1>
            <span class="px-2 py-0.5 text-[11px] rounded bg-blue-500/20 text-blue-300 border border-blue-400/30 font-semibold font-mono">RELEASE QUALITY GATE</span>
            <span class="px-2 py-0.5 text-[11px] rounded bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 font-medium">v${version}</span>
            <span class="px-2 py-0.5 text-[11px] rounded bg-purple-500/20 text-purple-300 border border-purple-400/30 font-medium">${testCases.length} Master Cases</span>
          </div>
          <p class="text-xs text-slate-400">IEEE 829 & ISTQB Enterprise Release Verification Protocol · Target: <code class="text-blue-300">${targetDomain}</code> · Date: ${releaseDate}</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 text-xs">
        <button onclick="exportToCSV()" class="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white font-medium shadow-sm transition flex items-center gap-1.5" title="Xuất kết quả test ra Excel CSV">
          <i class="fa-solid fa-file-csv"></i> Xuất CSV (Excel)
        </button>
        <button onclick="exportStateJSON()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-1.5" title="Backup toàn bộ tiến độ test">
          <i class="fa-solid fa-download"></i> Backup JSON
        </button>
        <label class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-1.5 cursor-pointer" title="Khôi phục phiên test">
          <i class="fa-solid fa-upload"></i> Restore JSON
          <input type="file" id="import-json-file" accept=".json" class="hidden" onchange="importStateJSON(event)">
        </label>
        <button onclick="window.print()" class="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md shadow-indigo-600/30 transition flex items-center gap-1.5">
          <i class="fa-solid fa-print"></i> In / Xuất PDF
        </button>
        <button onclick="resetAllProgress()" class="px-2.5 py-1.5 rounded-lg bg-rose-900/60 hover:bg-rose-800 text-rose-200 border border-rose-800/80 transition" title="Đặt lại trạng thái">
          <i class="fa-solid fa-rotate-left"></i>
        </button>
      </div>
    </div>

    <!-- Live Telemetry & Quality Gate Banner -->
    <div class="bg-slate-950 border-t border-slate-800 px-4 sm:px-6 py-2.5">
      <div class="max-w-[1750px] mx-auto flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <span class="text-xs uppercase font-bold tracking-wider text-slate-400">CỔNG DUYỆT RELEASE:</span>
          <div id="gate-decision-badge" class="px-3.5 py-1 rounded-full text-xs font-black tracking-wide flex items-center gap-2 shadow-inner">
            <span class="inline-block w-2.5 h-2.5 rounded-full animate-pulse"></span>
            <span id="gate-decision-text">ĐANG TÍNH TOÁN...</span>
          </div>
        </div>

        <!-- KPI Mini Counters -->
        <div class="flex items-center gap-4 text-xs font-mono">
          <div class="flex items-center gap-1.5 text-slate-300">
            <span class="text-slate-500">TỔNG:</span>
            <span id="kpi-total" class="font-bold text-white text-sm">${testCases.length}</span>
          </div>
          <div class="w-px h-3 bg-slate-800"></div>
          <div class="flex items-center gap-1.5 text-emerald-400">
            <i class="fa-solid fa-circle-check text-xs"></i>
            <span>PASS:</span>
            <span id="kpi-pass" class="font-bold text-white text-sm">0</span>
            <span id="kpi-pass-pct" class="text-[11px] text-emerald-500 font-normal">(0%)</span>
          </div>
          <div class="w-px h-3 bg-slate-800"></div>
          <div class="flex items-center gap-1.5 text-rose-400">
            <i class="fa-solid fa-circle-xmark text-xs"></i>
            <span>FAIL:</span>
            <span id="kpi-fail" class="font-bold text-white text-sm">0</span>
          </div>
          <div class="w-px h-3 bg-slate-800"></div>
          <div class="flex items-center gap-1.5 text-amber-400">
            <i class="fa-solid fa-triangle-exclamation text-xs"></i>
            <span>BLOCKER (P0):</span>
            <span id="kpi-blocker-pending" class="font-bold text-amber-300 text-sm">0</span>
          </div>
          <div class="w-px h-3 bg-slate-800"></div>
          <div class="flex items-center gap-1.5 text-slate-400">
            <span>CHƯA TEST:</span>
            <span id="kpi-untested" class="font-bold text-slate-200 text-sm">0</span>
          </div>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-[1750px] mx-auto px-4 sm:px-6 py-6 space-y-6">

    <!-- Tab Navigation -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-2 flex flex-wrap gap-2 no-print">
      <button onclick="switchTab('checklist')" id="tab-btn-checklist" class="px-5 py-2.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-blue-600 hover:bg-blue-50/50 transition flex items-center gap-2">
        <i class="fa-solid fa-clipboard-check"></i> 1. Checklist Phát Hành (Pre-Release)
      </button>
      <button onclick="switchTab('cases')" id="tab-btn-cases" class="px-5 py-2.5 rounded-lg text-xs font-semibold tab-active flex items-center gap-2">
        <i class="fa-solid fa-vial-circle-check"></i> 2. Chi Tiết Test Cases (${testCases.length} Cases)
      </button>
    </div>

    <!-- TAB 1: PRE-RELEASE CHECKLIST -->
    <section id="tab-checklist" class="tab-content hidden space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        ${checklistSections.map(sec => `
          <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-3">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2 border-b pb-2">
              <i class="fa-solid fa-list-check text-blue-600"></i> ${sec.title}
            </h3>
            <div class="space-y-2 text-xs">
              ${sec.items.map(item => `
                <label class="flex items-start gap-2.5 p-2 rounded-lg hover:bg-slate-50 cursor-pointer border border-transparent hover:border-slate-200 transition">
                  <input type="checkbox" id="chk-${item.id}" class="mt-0.5 rounded text-blue-600 focus:ring-blue-500 checklist-item" onchange="saveChecklistState()">
                  <div>
                    <span class="font-mono text-[11px] text-slate-400">${item.id}</span> -
                    <span class="font-medium text-slate-700">${item.name}</span>
                    <span class="ml-1 px-1.5 py-0.5 text-[10px] rounded bg-slate-100 text-slate-500 uppercase font-mono">${item.env}</span>
                  </div>
                </label>
              `).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </section>

    <!-- TAB 2: TEST CASES TABLE -->
    <section id="tab-cases" class="tab-content space-y-4">

      <!-- Filter Controls Bar -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-4 space-y-3 no-print">
        <div class="flex flex-wrap items-center justify-between gap-3">
          
          <!-- Search box -->
          <div class="relative flex-1 min-w-[280px]">
            <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
            <input type="text" id="filter-search" oninput="renderTable()" placeholder="Tìm kiếm nhanh mã case, tiêu đề, bước test, mong đợi..." class="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-xs focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
          </div>

          <!-- Filters -->
          <div class="flex flex-wrap items-center gap-2 text-xs">
            <select id="filter-priority" onchange="renderTable()" class="px-3 py-2 rounded-lg border border-slate-200 text-xs bg-white text-slate-700 font-medium">
              <option value="">Tất cả mức độ (P0 - P3)</option>
              <option value="P0">P0 - Blocker (Bắt buộc)</option>
              <option value="P1">P1 - Critical</option>
              <option value="P2">P2 - Major</option>
              <option value="P3">P3 - Minor</option>
            </select>

            <select id="filter-env" onchange="renderTable()" class="px-3 py-2 rounded-lg border border-slate-200 text-xs bg-white text-slate-700 font-medium">
              <option value="">Mọi môi trường</option>
              <option value="Prod">Production</option>
              <option value="Staging">Staging</option>
              <option value="Local">Local</option>
            </select>

            <select id="filter-status" onchange="renderTable()" class="px-3 py-2 rounded-lg border border-slate-200 text-xs bg-white text-slate-700 font-medium">
              <option value="">Tất cả trạng thái</option>
              <option value="PASSED">✅ PASSED</option>
              <option value="FAILED">❌ FAILED</option>
              <option value="BLOCKED">🚫 BLOCKED</option>
              <option value="UNTESTED">⏳ UNTESTED</option>
            </select>

            <select id="filter-module" onchange="renderTable()" class="px-3 py-2 rounded-lg border border-slate-200 text-xs bg-white text-slate-700 font-medium">
              <option value="">Tất cả phân hệ</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Master Cases Table -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-slate-900 text-slate-300 uppercase font-mono text-[11px] tracking-wider border-b border-slate-800">
              <tr>
                <th class="py-3 px-3 w-24">Mã Case</th>
                <th class="py-3 px-2 w-16 text-center">Ưu tiên</th>
                <th class="py-3 px-3 w-32">Phân hệ</th>
                <th class="py-3 px-3">Tên & Mô tả Test Case</th>
                <th class="py-3 px-3 w-48">Điều kiện & Bước test</th>
                <th class="py-3 px-3 w-56">Kết quả kỳ vọng</th>
                <th class="py-3 px-3 w-56">Thực tế & Evidence</th>
                <th class="py-3 px-2 w-28 text-center">Trạng thái</th>
              </tr>
            </thead>
            <tbody id="cases-tbody" class="divide-y divide-slate-100 font-sans">
              <!-- Dynamically populated -->
            </tbody>
          </table>
        </div>
        <div id="cases-empty" class="hidden p-12 text-center text-slate-400 text-xs">
          <i class="fa-solid fa-magnifying-glass text-2xl mb-2 text-slate-300"></i>
          <p>Không tìm thấy test case nào phù hợp với bộ lọc hiện tại.</p>
        </div>
      </div>
    </section>

  </main>

  <script>
    const INITIAL_CASES = ${JSON.stringify(testCases, null, 2)};
    const STORAGE_KEY = 'release_gate_${projectName.toLowerCase().replace(/[^a-z0-9]/g, '_')}_v${version}';
    let casesData = [];

    function init() {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          casesData = INITIAL_CASES.map(tc => {
            const match = parsed.find(p => p.id === tc.id);
            return match ? { ...tc, status: match.status, actual: match.actual || tc.actual, evidence: match.evidence || tc.evidence } : tc;
          });
        } catch(e) {
          casesData = JSON.parse(JSON.stringify(INITIAL_CASES));
        }
      } else {
        casesData = JSON.parse(JSON.stringify(INITIAL_CASES));
      }

      // Populate Modules
      const modules = Array.from(new Set(casesData.map(c => c.module).filter(Boolean)));
      const modSelect = document.getElementById('filter-module');
      modules.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        modSelect.appendChild(opt);
      });

      renderTable();
      updateTelemetry();
    }

    function switchTab(tab) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('[id^="tab-btn-"]').forEach(el => el.classList.remove('tab-active'));
      
      document.getElementById('tab-' + tab).classList.remove('hidden');
      document.getElementById('tab-btn-' + tab).classList.add('tab-active');
    }

    function updateTelemetry() {
      const total = casesData.length;
      const passed = casesData.filter(c => c.status === 'PASSED').length;
      const failed = casesData.filter(c => c.status === 'FAILED').length;
      const blocked = casesData.filter(c => c.status === 'BLOCKED').length;
      const untested = casesData.filter(c => !c.status || c.status === 'UNTESTED').length;
      const pct = total ? Math.round((passed / total) * 100) : 0;

      const p0Cases = casesData.filter(c => c.priority === 'P0' || c.isBlocker);
      const p0Pending = p0Cases.filter(c => c.status !== 'PASSED').length;

      document.getElementById('kpi-total').textContent = total;
      document.getElementById('kpi-pass').textContent = passed;
      document.getElementById('kpi-pass-pct').textContent = '(' + pct + '%)';
      document.getElementById('kpi-fail').textContent = failed;
      document.getElementById('kpi-blocker-pending').textContent = p0Pending;
      document.getElementById('kpi-untested').textContent = untested;

      const gateBadge = document.getElementById('gate-decision-badge');
      const gateText = document.getElementById('gate-decision-text');

      if (p0Pending === 0 && failed === 0 && pct >= 90) {
        gateBadge.className = 'px-3.5 py-1 rounded-full text-xs font-black tracking-wide flex items-center gap-2 shadow-inner bg-emerald-500/20 text-emerald-300 border border-emerald-400/40';
        gateText.textContent = 'READY FOR PRODUCTION RELEASE (100% BLOCKERS PASSED)';
      } else {
        gateBadge.className = 'px-3.5 py-1 rounded-full text-xs font-black tracking-wide flex items-center gap-2 shadow-inner bg-rose-500/20 text-rose-300 border border-rose-400/40';
        gateText.textContent = 'RELEASE BLOCKED (' + p0Pending + ' BLOCKERS / ' + failed + ' FAILED)';
      }
    }

    function renderTable() {
      const search = (document.getElementById('filter-search').value || '').toLowerCase().trim();
      const priority = document.getElementById('filter-priority').value;
      const env = document.getElementById('filter-env').value;
      const status = document.getElementById('filter-status').value;
      const module = document.getElementById('filter-module').value;

      const tbody = document.getElementById('cases-tbody');
      tbody.innerHTML = '';

      const filtered = casesData.filter(c => {
        if (priority && c.priority !== priority) return false;
        if (env && !(c.environment || '').toLowerCase().includes(env.toLowerCase())) return false;
        if (status && c.status !== status) return false;
        if (module && c.module !== module) return false;
        if (search) {
          const text = (c.id + ' ' + c.title + ' ' + c.module + ' ' + (c.steps||'') + ' ' + (c.expected||'')).toLowerCase();
          if (!text.includes(search)) return false;
        }
        return true;
      });

      document.getElementById('cases-empty').classList.toggle('hidden', filtered.length > 0);

      filtered.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50/80 transition group';

        const pBadgeClass = c.priority === 'P0' ? 'badge-blocker' : c.priority === 'P1' ? 'badge-p1' : c.priority === 'P2' ? 'badge-p2' : 'badge-p3';
        const statusBorder = c.status === 'PASSED' ? 'border-l-4 border-l-emerald-500' : c.status === 'FAILED' ? 'border-l-4 border-l-rose-500' : c.status === 'BLOCKED' ? 'border-l-4 border-l-amber-500' : 'border-l-4 border-l-slate-300';

        tr.innerHTML = \`
          <td class="py-3 px-3 font-mono font-bold text-slate-800 \${statusBorder}">
            <div class="flex items-center gap-1.5">
              <span>\${c.id}</span>
            </div>
            <div class="text-[10px] text-slate-400 font-normal mt-0.5">\${c.environment || 'Any'}</div>
          </td>
          <td class="py-3 px-2 text-center">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono \${pBadgeClass}">\${c.priority}</span>
          </td>
          <td class="py-3 px-3 text-slate-600 font-medium">\${c.module}</td>
          <td class="py-3 px-3 font-medium text-slate-900">
            <div>\${c.title}</div>
            \${c.preconditions ? \`<div class="text-[11px] text-slate-400 mt-1"><i class="fa-solid fa-circle-info text-[9px] mr-1"></i>\${c.preconditions}</div>\` : ''}
          </td>
          <td class="py-3 px-3 text-slate-600 font-mono text-[11px] whitespace-pre-line">\${c.steps || '-'}</td>
          <td class="py-3 px-3 text-slate-600 text-[11px] whitespace-pre-line">\${c.expected || '-'}</td>
          <td class="py-3 px-3 text-slate-600 text-[11px]">
            <input type="text" value="\${c.actual || ''}" onchange="updateCaseField('\${c.id}', 'actual', this.value)" placeholder="Ghi chú thực tế..." class="w-full px-2 py-1 rounded border border-slate-200 bg-white text-[11px] focus:ring-1 focus:ring-blue-500 outline-none mb-1">
            \${c.evidence ? \`<div class="text-[10px] font-mono text-slate-500 bg-slate-100 p-1.5 rounded truncate" title="\${c.evidence}">\${c.evidence}</div>\` : ''}
          </td>
          <td class="py-3 px-2 text-center">
            <select onchange="updateCaseStatus('\${c.id}', this.value)" class="px-2 py-1.5 rounded text-[11px] font-bold outline-none border transition cursor-pointer \${
              c.status === 'PASSED' ? 'bg-emerald-50 text-emerald-700 border-emerald-300' :
              c.status === 'FAILED' ? 'bg-rose-50 text-rose-700 border-rose-300' :
              c.status === 'BLOCKED' ? 'bg-amber-50 text-amber-700 border-amber-300' :
              'bg-slate-50 text-slate-600 border-slate-300'
            }">
              <option value="PASSED" \${c.status === 'PASSED' ? 'selected' : ''}>✅ PASS</option>
              <option value="FAILED" \${c.status === 'FAILED' ? 'selected' : ''}>❌ FAIL</option>
              <option value="BLOCKED" \${c.status === 'BLOCKED' ? 'selected' : ''}>🚫 BLOCK</option>
              <option value="UNTESTED" \${!c.status || c.status === 'UNTESTED' ? 'selected' : ''}>⏳ UNTESTED</option>
            </select>
          </td>
        \`;
        tbody.appendChild(tr);
      });
    }

    function updateCaseStatus(id, newStatus) {
      const c = casesData.find(item => item.id === id);
      if (c) {
        c.status = newStatus;
        saveState();
        updateTelemetry();
        renderTable();
      }
    }

    function updateCaseField(id, field, value) {
      const c = casesData.find(item => item.id === id);
      if (c) {
        c[field] = value;
        saveState();
      }
    }

    function saveState() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(casesData));
    }

    function resetAllProgress() {
      if (confirm('Bạn có chắc muốn đặt lại toàn bộ trạng thái test về mặc định?')) {
        localStorage.removeItem(STORAGE_KEY);
        casesData = JSON.parse(JSON.stringify(INITIAL_CASES));
        renderTable();
        updateTelemetry();
      }
    }

    function exportToCSV() {
      let csv = '\\uFEFFMã Case,Mức độ,Phân hệ,Tiêu đề,Môi trường,Các bước,Kỳ vọng,Thực tế,Trạng thái,Evidence\\n';
      casesData.forEach(c => {
        const row = [
          c.id,
          c.priority,
          '"' + (c.module||'').replace(/"/g, '""') + '"',
          '"' + (c.title||'').replace(/"/g, '""') + '"',
          c.environment || '',
          '"' + (c.steps||'').replace(/"/g, '""') + '"',
          '"' + (c.expected||'').replace(/"/g, '""') + '"',
          '"' + (c.actual||'').replace(/"/g, '""') + '"',
          c.status || 'UNTESTED',
          '"' + (c.evidence||'').replace(/"/g, '""') + '"'
        ];
        csv += row.join(',') + '\\n';
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = '${projectName.replace(/[^a-zA-Z0-9]/g, '_')}_TestResults_v${version}.csv';
      link.click();
    }

    function exportStateJSON() {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(casesData, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", '${projectName.replace(/[^a-zA-Z0-9]/g, '_')}_Backup_v${version}.json');
      downloadAnchor.click();
    }

    function importStateJSON(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const imported = JSON.parse(e.target.result);
          if (Array.isArray(imported)) {
            casesData = imported;
            saveState();
            renderTable();
            updateTelemetry();
            alert('Khôi phục trạng thái thành công!');
          }
        } catch(err) {
          alert('Lỗi khi đọc file JSON: ' + err.message);
        }
      };
      reader.readAsText(file);
    }

    window.onload = init;
  </script>
</body>
</html>
`;

fs.writeFileSync(outputPath, htmlContent, 'utf8');
console.log(`[SUCCESS] Đã tạo thành công Quality Gate Portal: ${outputPath}`);
