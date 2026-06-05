from __future__ import annotations

import csv
import html
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from med_school_ranker.paths import (
    ADMISSIONS_SOURCE_QUEUE_CSV,
    ADMISSIONS_STATS_CSV,
    APPLICANT_PROFILES_CSV,
    DATA_QUALITY_REPORT_CSV,
    MASTER_CSV,
    OUT,
    PARTNER_INPUTS_CSV,
    RANKINGS_CSV,
    ROOT,
    SITE_DIR,
    SITE_INDEX_HTML,
)


JSON_OUTPUTS = {
    "school_master": MASTER_CSV,
    "calculated_rankings": RANKINGS_CSV,
    "applicant_profiles": APPLICANT_PROFILES_CSV,
    "admissions_stats": ADMISSIONS_STATS_CSV,
    "partner_inputs": PARTNER_INPUTS_CSV,
    "admissions_source_queue": ADMISSIONS_SOURCE_QUEUE_CSV,
    "data_quality_report": DATA_QUALITY_REPORT_CSV,
    "project_subplans": ROOT / "data/project_subplans.csv",
}

MCAT_GPA_FIELDS = {
    "mcat_median_accepted",
    "mcat_median_matriculated",
    "mcat_mean_enrolled",
    "mcat_10th_percentile",
    "mcat_25th_percentile",
    "mcat_75th_percentile",
    "mcat_90th_percentile",
    "overall_gpa_median_accepted",
    "overall_gpa_median_matriculated",
    "overall_gpa_mean_enrolled",
    "science_gpa_mean_enrolled",
}

TRUTHY = {"1", "true", "t", "yes", "y"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def is_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in TRUTHY


def has_partner_input(row: dict[str, str]) -> bool:
    fields = [
        "could_live_here_4_years_score",
        "location_fit_score",
        "culture_fit_score",
        "regret_index_score",
        "hard_no_flag",
        "hard_no_reason",
        "partner_notes",
    ]
    return any(row.get(field, "").strip() for field in fields)


def has_admissions_stats(row: dict[str, str]) -> bool:
    return any(row.get(field, "").strip() for field in MCAT_GPA_FIELDS)


def first_by_school(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_school: dict[str, dict[str, str]] = {}
    for row in rows:
        school_id = row.get("school_id", "").strip()
        if school_id and school_id not in by_school:
            by_school[school_id] = row
    return by_school


def suggested_next_action(
    partner_row: dict[str, str],
    source_row: dict[str, str],
    warning_count: int,
    error_count: int,
) -> str:
    if not has_partner_input(partner_row):
        return "review partner input"
    if not source_row.get("candidate_source_url", "").strip():
        return "find admissions source"
    if warning_count or error_count:
        return "review data quality"
    return "review ranking"


def build_site_payload() -> dict[str, object]:
    school_master = read_csv(MASTER_CSV)
    rankings = read_csv(RANKINGS_CSV)
    applicant_profiles = read_csv(APPLICANT_PROFILES_CSV)
    admissions_stats = read_csv(ADMISSIONS_STATS_CSV)
    partner_inputs = read_csv(PARTNER_INPUTS_CSV)
    source_queue = read_csv(ADMISSIONS_SOURCE_QUEUE_CSV)
    data_quality = read_csv(DATA_QUALITY_REPORT_CSV)
    project_subplans = read_csv(ROOT / "data/project_subplans.csv")

    rankings_by_school = first_by_school(rankings)
    partner_by_school = first_by_school(partner_inputs)
    source_by_school = first_by_school(source_queue)
    stats_by_school = first_by_school(admissions_stats)

    warning_counts: Counter[str] = Counter()
    error_counts: Counter[str] = Counter()
    issues_by_school: dict[str, list[dict[str, str]]] = defaultdict(list)
    for issue in data_quality:
        school_id = issue.get("row_id", "").strip()
        severity = issue.get("severity", "").strip().lower()
        if not school_id:
            continue
        if severity == "warning":
            warning_counts[school_id] += 1
        elif severity == "error":
            error_counts[school_id] += 1
        issues_by_school[school_id].append(issue)

    schools = []
    for school in school_master:
        school_id = school.get("school_id", "")
        partner_row = partner_by_school.get(school_id, {})
        source_row = source_by_school.get(school_id, {})
        stats_row = stats_by_school.get(school_id, {})
        warning_count = warning_counts[school_id]
        error_count = error_counts[school_id]
        schools.append(
            {
                "school": school,
                "ranking": rankings_by_school.get(school_id, {}),
                "partner_input": partner_row,
                "admissions_source": source_row,
                "admissions_stats": stats_row,
                "data_quality": issues_by_school.get(school_id, []),
                "derived": {
                    "warning_count": warning_count,
                    "error_count": error_count,
                    "partner_input_status": "present" if has_partner_input(partner_row) else "missing",
                    "partner_notes_indicator": "yes" if partner_row.get("partner_notes", "").strip() else "no",
                    "hard_no_flag": is_truthy(partner_row.get("hard_no_flag")),
                    "admissions_stats_present": "yes" if has_admissions_stats(stats_row) else "no",
                    "source_queue_status": source_row.get("source_status", "").strip() or "not_started",
                    "suggested_next_action": suggested_next_action(
                        partner_row,
                        source_row,
                        warning_count,
                        error_count,
                    ),
                },
            }
        )

    degree_counts = Counter(row.get("degree_type", "Unknown") or "Unknown" for row in school_master)
    return {
        "meta": {
            "site_privacy_mode": "local_full",
            "active_school_count": len(school_master),
            "degree_counts": dict(sorted(degree_counts.items())),
        },
        "schools": schools,
        "school_master": school_master,
        "calculated_rankings": rankings,
        "applicant_profiles": applicant_profiles,
        "admissions_stats": admissions_stats,
        "partner_inputs": partner_inputs,
        "admissions_source_queue": source_queue,
        "data_quality_report": data_quality,
        "project_subplans": project_subplans,
    }


def write_site_json(payload: dict[str, object]) -> None:
    data_dir = SITE_DIR / "data"
    for key, source in JSON_OUTPUTS.items():
        write_json(data_dir / f"{key}.json", read_csv(source))
    write_json(data_dir / "site_payload.json", payload)


def render_site_html(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    escaped_payload = html.escape(payload_json, quote=False)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Medical School Ranker</title>
  <style>{CSS}</style>
</head>
<body>
  <header class="app-header">
    <div>
      <h1>Medical School Ranker</h1>
      <p id="summaryText">Static local review dashboard</p>
    </div>
    <label class="search-label">Search
      <input id="globalSearch" type="search" placeholder="School, city, state">
    </label>
  </header>
  <nav class="tabs" aria-label="Primary views">
    <button data-view="dashboard" class="active">Dashboard</button>
    <button data-view="rankings">Rankings</button>
    <button data-view="detail">School Detail</button>
    <button data-view="partner">Partner Review</button>
    <button data-view="sources">Admissions Sources</button>
    <button data-view="quality">Data Quality</button>
    <button data-view="plans">Plans</button>
  </nav>
  <main>
    <section id="dashboard" class="view active"></section>
    <section id="rankings" class="view"></section>
    <section id="detail" class="view"></section>
    <section id="partner" class="view"></section>
    <section id="sources" class="view"></section>
    <section id="quality" class="view"></section>
    <section id="plans" class="view"></section>
  </main>
  <script type="application/json" id="site-data">{escaped_payload}</script>
  <script>{JS}</script>
</body>
</html>
"""


CSS = r"""
:root {
  color-scheme: light;
  --border: #d7dee8;
  --header: #13324f;
  --muted: #627386;
  --bg: #f5f7fa;
  --panel: #ffffff;
  --accent: #146c94;
  --warn: #8a5a00;
  --error: #a12d2d;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg);
  color: #172331;
}
.app-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: end;
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
h1 { margin: 0; font-size: 22px; color: var(--header); }
h2 { margin: 0 0 12px; font-size: 18px; color: var(--header); }
h3 { margin: 0 0 8px; font-size: 15px; color: var(--header); }
p { margin: 4px 0 0; color: var(--muted); }
.search-label { display: grid; gap: 4px; color: var(--muted); font-size: 12px; min-width: 280px; }
input, select {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  font: inherit;
  background: #fff;
}
.tabs {
  display: flex;
  gap: 6px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: #eaf0f6;
  overflow-x: auto;
}
button {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  background: #fff;
  color: #203347;
  cursor: pointer;
  white-space: nowrap;
}
button.active { background: var(--accent); border-color: var(--accent); color: #fff; }
main { padding: 18px; }
.view { display: none; }
.view.active { display: block; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 18px; }
.metric, .panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
}
.metric strong { display: block; font-size: 24px; color: var(--header); }
.filters { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 12px; align-items: end; }
.table-wrap { overflow: auto; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); }
table { width: 100%; border-collapse: collapse; min-width: 900px; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; font-size: 13px; }
th { position: sticky; top: 0; background: #eef4f8; color: var(--header); cursor: pointer; z-index: 1; }
tr:hover td { background: #f8fbfd; }
.badge { display: inline-block; border-radius: 999px; padding: 2px 8px; font-size: 12px; border: 1px solid var(--border); background: #f7fafc; }
.badge.warn { color: var(--warn); border-color: #e6c773; background: #fff8df; }
.badge.error { color: var(--error); border-color: #e7aaaa; background: #fff0f0; }
.badge.good { color: #17623a; border-color: #a9d6bb; background: #eefaf2; }
.muted { color: var(--muted); }
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
a { color: var(--accent); }
@media (max-width: 760px) {
  .app-header { display: grid; align-items: stretch; }
  .search-label { min-width: 0; }
  main { padding: 12px; }
}
"""


JS = r"""
const payload = JSON.parse(document.getElementById('site-data').textContent);
let currentView = 'dashboard';
let selectedSchoolId = payload.schools[0]?.school?.school_id || '';
let sortState = {};
let filters = {
  rankings: {degree: '', state: '', tier: '', bucket: '', hardNo: '', warnings: '', partner: ''},
  sources: {sourceMissing: ''},
};

const $ = (id) => document.getElementById(id);
const missing = (value) => value === undefined || value === null || value === '' ? 'Missing' : value;
const truthy = (value) => ['1','true','t','yes','y'].includes(String(value || '').toLowerCase());
const schoolText = (item) => [
  item.school.school_name,
  item.school.city,
  item.school.state,
  item.school.degree_type,
].join(' ').toLowerCase();

function filteredSchools() {
  const query = $('globalSearch').value.trim().toLowerCase();
  return payload.schools.filter(item => !query || schoolText(item).includes(query));
}

function setView(view) {
  currentView = view;
  document.querySelectorAll('.tabs button').forEach(btn => btn.classList.toggle('active', btn.dataset.view === view));
  document.querySelectorAll('.view').forEach(section => section.classList.toggle('active', section.id === view));
  render();
}

function openDetail(schoolId) {
  selectedSchoolId = schoolId;
  setView('detail');
}

function metric(label, value) {
  return `<div class="metric"><span class="muted">${label}</span><strong>${value}</strong></div>`;
}

function badge(text, type='') {
  return `<span class="badge ${type}">${text}</span>`;
}

function table(headers, rows, key) {
  const head = headers.map(h => `<th data-key="${h.key}" data-table="${key}">${h.label}</th>`).join('');
  const body = rows.map(row => `<tr>${headers.map(h => `<td>${h.render(row)}</td>`).join('')}</tr>`).join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body || `<tr><td colspan="${headers.length}">No rows</td></tr>`}</tbody></table></div>`;
}

function optionTags(values, selected) {
  return values.map(value => `<option value="${value}" ${value === selected ? 'selected' : ''}>${value}</option>`).join('');
}

function sortRows(rows, tableKey, defaultKey, defaultDir='asc') {
  const state = sortState[tableKey] || {key: defaultKey, dir: defaultDir};
  return [...rows].sort((a, b) => {
    const av = String(state.get ? state.get(a) : state.key.split('.').reduce((o,k)=>o?.[k], a) || '').toLowerCase();
    const bv = String(state.get ? state.get(b) : state.key.split('.').reduce((o,k)=>o?.[k], b) || '').toLowerCase();
    const an = Number(av), bn = Number(bv);
    const result = !Number.isNaN(an) && !Number.isNaN(bn) ? an - bn : av.localeCompare(bv);
    return state.dir === 'desc' ? -result : result;
  });
}

function warningCount() { return payload.data_quality_report.filter(i => i.severity === 'warning').length; }
function errorCount() { return payload.data_quality_report.filter(i => i.severity === 'error').length; }

function renderDashboard() {
  const schools = filteredSchools();
  const md = payload.schools.filter(s => s.school.degree_type === 'MD').length;
  const degreeDo = payload.schools.filter(s => s.school.degree_type === 'DO').length;
  const partnerPresent = payload.schools.filter(s => s.derived.partner_input_status === 'present').length;
  const hardNo = payload.schools.filter(s => s.derived.hard_no_flag).length;
  const sourceFound = payload.schools.filter(s => s.admissions_source.candidate_source_url).length;
  const priority = schools
    .filter(s => s.derived.suggested_next_action !== 'review ranking')
    .slice(0, 20);
  $('dashboard').innerHTML = `
    <div class="grid">
      ${metric('Active schools', payload.meta.active_school_count)}
      ${metric('MD', md)}
      ${metric('DO', degreeDo)}
      ${metric('Partner inputs', partnerPresent)}
      ${metric('Hard no', hardNo)}
      ${metric('Errors', errorCount())}
      ${metric('Warnings', warningCount())}
      ${metric('Admissions sources found', sourceFound)}
    </div>
    <div class="panel">
      <h2>Top Research Priorities</h2>
      ${table([
        {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
        {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
        {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
        {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
        {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status},
        {key:'derived.suggested_next_action', label:'Next Action', render:s=>s.derived.suggested_next_action},
      ], priority, 'dashboard')}
    </div>`;
}

function linkSchool(item) {
  return `<a href="#" data-school="${item.school.school_id}">${item.school.school_name}</a>`;
}

function rankingFilters() {
  const degrees = [...new Set(payload.schools.map(s => s.school.degree_type).filter(Boolean))].sort();
  const states = [...new Set(payload.schools.map(s => s.school.state).filter(Boolean))].sort();
  const tiers = [...new Set(payload.schools.map(s => s.ranking.dynamic_tier).filter(Boolean))].sort();
  const buckets = [...new Set(payload.schools.map(s => s.ranking.suggested_funnel_bucket).filter(Boolean))].sort();
  const f = filters.rankings;
  return `
    <div class="filters">
      <label>Degree <select id="rankDegree"><option value="" ${f.degree === '' ? 'selected' : ''}>All</option>${optionTags(degrees, f.degree)}</select></label>
      <label>State <select id="rankState"><option value="" ${f.state === '' ? 'selected' : ''}>All</option>${optionTags(states, f.state)}</select></label>
      <label>Tier <select id="rankTier"><option value="" ${f.tier === '' ? 'selected' : ''}>All</option>${optionTags(tiers, f.tier)}</select></label>
      <label>Bucket <select id="rankBucket"><option value="" ${f.bucket === '' ? 'selected' : ''}>All</option>${optionTags(buckets, f.bucket)}</select></label>
      <label>Hard No <select id="rankHardNo"><option value="" ${f.hardNo === '' ? 'selected' : ''}>All</option><option value="yes" ${f.hardNo === 'yes' ? 'selected' : ''}>Yes</option><option value="no" ${f.hardNo === 'no' ? 'selected' : ''}>No</option></select></label>
      <label>Warnings <select id="rankWarnings"><option value="" ${f.warnings === '' ? 'selected' : ''}>All</option><option value="yes" ${f.warnings === 'yes' ? 'selected' : ''}>Has warnings</option><option value="no" ${f.warnings === 'no' ? 'selected' : ''}>No warnings</option></select></label>
      <label>Partner <select id="rankPartner"><option value="" ${f.partner === '' ? 'selected' : ''}>All</option><option value="present" ${f.partner === 'present' ? 'selected' : ''}>Present</option><option value="missing" ${f.partner === 'missing' ? 'selected' : ''}>Missing</option></select></label>
    </div>`;
}

function rankingsRows() {
  const {degree, state, tier, bucket, hardNo, warnings, partner} = filters.rankings;
  return filteredSchools().filter(s => {
    if (degree && s.school.degree_type !== degree) return false;
    if (state && s.school.state !== state) return false;
    if (tier && s.ranking.dynamic_tier !== tier) return false;
    if (bucket && s.ranking.suggested_funnel_bucket !== bucket) return false;
    if (hardNo === 'yes' && !s.derived.hard_no_flag) return false;
    if (hardNo === 'no' && s.derived.hard_no_flag) return false;
    if (warnings === 'yes' && s.derived.warning_count < 1) return false;
    if (warnings === 'no' && s.derived.warning_count > 0) return false;
    if (partner && s.derived.partner_input_status !== partner) return false;
    return true;
  });
}

function renderRankings() {
  $('rankings').innerHTML = `<h2>Rankings</h2>${rankingFilters()}<div id="rankTable"></div>`;
  const bindings = {
    rankDegree: 'degree',
    rankState: 'state',
    rankTier: 'tier',
    rankBucket: 'bucket',
    rankHardNo: 'hardNo',
    rankWarnings: 'warnings',
    rankPartner: 'partner',
  };
  Object.entries(bindings).forEach(([id, key]) => $(id).addEventListener('change', event => {
    filters.rankings[key] = event.target.value;
    renderRankingTable();
  }));
  renderRankingTable();
}

function renderRankingTable() {
  const rows = sortRows(rankingsRows(), 'rankings', 'ranking.overall_rank');
  $('rankTable').innerHTML = `<p>${rows.length} visible schools</p>` + table([
    {key:'ranking.overall_rank', label:'Rank', render:s=>missing(s.ranking.overall_rank)},
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'ranking.dynamic_tier', label:'Tier', render:s=>missing(s.ranking.dynamic_tier)},
    {key:'ranking.suggested_funnel_bucket', label:'Bucket', render:s=>missing(s.ranking.suggested_funnel_bucket)},
    {key:'ranking.overall_school_value', label:'Overall', render:s=>missing(s.ranking.overall_school_value)},
    {key:'ranking.admissions_score', label:'Admissions', render:s=>missing(s.ranking.admissions_score)},
    {key:'ranking.attendance_score', label:'Attendance', render:s=>missing(s.ranking.attendance_score)},
    {key:'ranking.data_completeness_score', label:'Data', render:s=>missing(s.ranking.data_completeness_score)},
    {key:'derived.warning_count', label:'Warnings', render:s=>s.derived.warning_count ? badge(s.derived.warning_count, 'warn') : '0'},
    {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''},
    {key:'derived.partner_input_status', label:'Partner', render:s=>s.derived.partner_input_status},
  ], rows, 'rankings');
}

function renderDetail() {
  const item = payload.schools.find(s => s.school.school_id === selectedSchoolId) || payload.schools[0];
  if (!item) { $('detail').innerHTML = '<p>No school selected.</p>'; return; }
  selectedSchoolId = item.school.school_id;
  const sourceUrl = item.school.source_url ? `<a href="${item.school.source_url}" target="_blank">Source</a>` : 'Missing';
  $('detail').innerHTML = `
    <h2>${item.school.school_name}</h2>
    <p>${item.school.degree_type} · ${missing(item.school.city)}, ${missing(item.school.state)} · ${sourceUrl}</p>
    <div class="detail-grid">
      ${detailPanel('Identity', [
        ['School ID', item.school.school_id],
        ['Parent', item.school.parent_school_name],
        ['Campus', item.school.campus_name],
        ['Accreditation', item.school.accreditation_status],
      ])}
      ${detailPanel('Ranking', [
        ['Overall rank', item.ranking.overall_rank],
        ['Tier', item.ranking.dynamic_tier],
        ['Bucket', item.ranking.suggested_funnel_bucket],
        ['Admissions', item.ranking.admissions_score],
        ['Attendance', item.ranking.attendance_score],
        ['Data completeness', item.ranking.data_completeness_score],
      ])}
      ${detailPanel('Partner Review', [
        ['Could live here', item.partner_input.could_live_here_4_years_score],
        ['Location fit', item.partner_input.location_fit_score],
        ['Culture fit', item.partner_input.culture_fit_score],
        ['Regret index', item.partner_input.regret_index_score],
        ['Hard no', item.derived.hard_no_flag ? 'Yes' : 'No'],
        ['Reason', item.partner_input.hard_no_reason],
        ['Notes', item.partner_input.partner_notes],
      ])}
      ${detailPanel('Admissions Research', [
        ['Source status', item.derived.source_queue_status],
        ['Candidate URL', item.admissions_source.candidate_source_url],
        ['Stats present', item.derived.admissions_stats_present],
        ['Confidence', item.admissions_stats.data_confidence],
      ])}
      ${detailPanel('Data Quality', [
        ['Warnings', item.derived.warning_count],
        ['Errors', item.derived.error_count],
        ['Next action', item.derived.suggested_next_action],
      ])}
    </div>
    <div class="panel" style="margin-top:12px">
      <h3>Issues</h3>
      ${table([
        {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
        {key:'file', label:'File', render:i=>i.file},
        {key:'field', label:'Field', render:i=>i.field},
        {key:'message', label:'Message', render:i=>i.message},
        {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
      ], item.data_quality, 'detailIssues')}
    </div>`;
}

function detailPanel(title, rows) {
  return `<div class="panel"><h3>${title}</h3>${rows.map(([k,v])=>`<p><strong>${k}:</strong> ${missing(v)}</p>`).join('')}</div>`;
}

function renderPartner() {
  const rows = filteredSchools();
  $('partner').innerHTML = `<h2>Partner Review</h2>` + table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'partner_input.could_live_here_4_years_score', label:'4 Years', render:s=>missing(s.partner_input.could_live_here_4_years_score)},
    {key:'partner_input.location_fit_score', label:'Location', render:s=>missing(s.partner_input.location_fit_score)},
    {key:'partner_input.culture_fit_score', label:'Culture', render:s=>missing(s.partner_input.culture_fit_score)},
    {key:'partner_input.regret_index_score', label:'Regret', render:s=>missing(s.partner_input.regret_index_score)},
    {key:'derived.hard_no_flag', label:'Hard No', render:s=>s.derived.hard_no_flag ? badge('Hard No', 'error') : ''},
    {key:'partner_input.partner_notes', label:'Notes', render:s=>missing(s.partner_input.partner_notes)},
  ], rows, 'partner');
}

function renderSources() {
  const current = filters.sources.sourceMissing;
  $('sources').innerHTML = `<h2>Admissions Sources</h2>
    <div class="filters"><label>Source URL <select id="sourceMissing"><option value="">All</option><option value="missing">Missing</option><option value="present">Present</option></select></label></div>
    <div id="sourceTable"></div>`;
  $('sourceMissing').value = current;
  $('sourceMissing').addEventListener('change', event => {
    filters.sources.sourceMissing = event.target.value;
    renderSourceTable();
  });
  renderSourceTable();
}

function renderSourceTable() {
  const rows = filteredSchools().filter(s => {
    const filter = filters.sources.sourceMissing;
    return !filter || (filter === 'missing' ? !s.admissions_source.candidate_source_url : !!s.admissions_source.candidate_source_url);
  });
  $('sourceTable').innerHTML = table([
    {key:'school.school_name', label:'School', render:s=>linkSchool(s)},
    {key:'school.degree_type', label:'Degree', render:s=>badge(s.school.degree_type)},
    {key:'school.city', label:'City', render:s=>`${missing(s.school.city)}, ${missing(s.school.state)}`},
    {key:'admissions_source.candidate_source_url', label:'Candidate URL', render:s=>s.admissions_source.candidate_source_url ? `<a href="${s.admissions_source.candidate_source_url}" target="_blank">Open</a>` : 'Missing'},
    {key:'derived.source_queue_status', label:'Source Status', render:s=>s.derived.source_queue_status},
    {key:'derived.admissions_stats_present', label:'Stats', render:s=>s.derived.admissions_stats_present},
    {key:'admissions_source.notes', label:'Notes', render:s=>missing(s.admissions_source.notes)},
  ], rows, 'sources');
}

function renderQuality() {
  const severity = $('qualitySeverity')?.value || '';
  const rows = payload.data_quality_report.filter(i => !severity || i.severity === severity);
  $('quality').innerHTML = `<h2>Data Quality</h2>
    <div class="grid">${metric('Errors', errorCount())}${metric('Warnings', warningCount())}</div>
    <div class="filters"><label>Severity <select id="qualitySeverity"><option value="">All</option><option value="error">Error</option><option value="warning">Warning</option><option value="info">Info</option></select></label></div>
    <div id="qualityTable"></div>`;
  $('qualitySeverity').value = severity;
  $('qualitySeverity').addEventListener('change', renderQuality);
  $('qualityTable').innerHTML = table([
    {key:'severity', label:'Severity', render:i=>badge(i.severity, i.severity)},
    {key:'file', label:'File', render:i=>i.file},
    {key:'row_id', label:'Row', render:i=>i.row_id},
    {key:'field', label:'Field', render:i=>i.field},
    {key:'message', label:'Message', render:i=>i.message},
    {key:'suggested_fix', label:'Suggested Fix', render:i=>i.suggested_fix},
  ], rows, 'quality');
}

function renderPlans() {
  $('plans').innerHTML = `<h2>Plans</h2>` + table([
    {key:'plan_name', label:'Plan', render:p=>p.plan_name},
    {key:'status', label:'Status', render:p=>badge(p.status)},
    {key:'priority', label:'Priority', render:p=>p.priority},
    {key:'phase', label:'Phase', render:p=>p.phase},
    {key:'current_decision_summary', label:'Decision', render:p=>p.current_decision_summary},
    {key:'next_action', label:'Next Action', render:p=>p.next_action},
    {key:'doc_path', label:'Doc', render:p=>p.doc_path},
  ], payload.project_subplans, 'plans');
}

function render() {
  $('summaryText').textContent = `${payload.meta.active_school_count} active schools · ${warningCount()} warnings · ${errorCount()} errors`;
  if (currentView === 'dashboard') renderDashboard();
  if (currentView === 'rankings') renderRankings();
  if (currentView === 'detail') renderDetail();
  if (currentView === 'partner') renderPartner();
  if (currentView === 'sources') renderSources();
  if (currentView === 'quality') renderQuality();
  if (currentView === 'plans') renderPlans();
  document.querySelectorAll('[data-school]').forEach(el => el.addEventListener('click', event => {
    event.preventDefault();
    openDetail(el.dataset.school);
  }));
}

document.querySelectorAll('.tabs button').forEach(btn => btn.addEventListener('click', () => setView(btn.dataset.view)));
$('globalSearch').addEventListener('input', render);
document.addEventListener('click', event => {
  const th = event.target.closest('th[data-key]');
  if (!th) return;
  const tableKey = th.dataset.table;
  const key = th.dataset.key;
  const prior = sortState[tableKey] || {};
  sortState[tableKey] = {key, dir: prior.key === key && prior.dir === 'asc' ? 'desc' : 'asc'};
  render();
});
render();
"""


def build_site() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_site_payload()
    write_site_json(payload)
    SITE_INDEX_HTML.write_text(render_site_html(payload), encoding="utf-8")
    return SITE_INDEX_HTML


def main() -> None:
    output = build_site()
    print(f"Wrote {output.relative_to(ROOT)}")
