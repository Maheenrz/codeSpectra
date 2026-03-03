import React, { useState, useEffect, useRef } from "react";
import { Link, useParams } from "react-router-dom";
import analysisService from "../../services/analysisService";

// ─── Helpers ──────────────────────────────────────────────────────────────────
const pct = (n) => `${Math.round((n || 0) * 100)}%`;
const fmtScore = (n) =>
  typeof n === "number" ? `${Math.round(n * 100)}%` : "—";

const RISK = {
  HIGH: {
    label: "High",
    bg: "bg-red-100",
    text: "text-red-700",
    bar: "bg-red-500",
    dot: "bg-red-500",
  },
  MEDIUM: {
    label: "Medium",
    bg: "bg-amber-100",
    text: "text-amber-700",
    bar: "bg-amber-400",
    dot: "bg-amber-400",
  },
  LOW: {
    label: "Low",
    bg: "bg-blue-100",
    text: "text-blue-700",
    bar: "bg-blue-400",
    dot: "bg-blue-400",
  },
  NONE: {
    label: "None",
    bg: "bg-gray-100",
    text: "text-gray-500",
    bar: "bg-gray-300",
    dot: "bg-gray-300",
  },
  CRITICAL: {
    label: "Critical",
    bg: "bg-red-200",
    text: "text-red-800",
    bar: "bg-red-600",
    dot: "bg-red-600",
  },
};

function getRisk(score) {
  const s = typeof score === "number" ? score : parseFloat(score) / 100;
  if (s >= 0.85) return "CRITICAL";
  if (s >= 0.7) return "HIGH";
  if (s >= 0.5) return "MEDIUM";
  if (s >= 0.3) return "LOW";
  return "NONE";
}

// ─── Similarity bar ───────────────────────────────────────────────────────────
const SimilarityBar = ({ score, className = "" }) => {
  const risk = RISK[getRisk(score)];
  const pctVal = Math.round((score || 0) * 100);
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${risk.bar}`}
          style={{ width: `${pctVal}%` }}
        />
      </div>
      <span
        className={`text-sm font-black min-w-[3rem] text-right ${risk.text}`}
      >
        {pctVal}%
      </span>
    </div>
  );
};

// ─── Risk badge ───────────────────────────────────────────────────────────────
const RiskBadge = ({ score }) => {
  const level = getRisk(score);
  const r = RISK[level];
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full ${r.bg} ${r.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${r.dot}`} />
      {r.label}
    </span>
  );
};

// ─── Side-by-side code block ──────────────────────────────────────────────────
const CodeDiffBlock = ({ fragmentA, fragmentB, similarLines = [] }) => {
  const similarSet = new Set(similarLines);

  const renderLines = (lines = [], side) => (
    <div className="flex-1 min-w-0 overflow-auto">
      <div className="font-mono text-xs leading-6">
        {lines.map((line, i) => (
          <div
            key={i}
            className={`flex ${similarSet.has(i) ? "bg-yellow-50 border-l-2 border-yellow-400" : "hover:bg-gray-50/60"}`}
          >
            <span className="select-none text-gray-300 w-10 text-right pr-3 py-0.5 flex-shrink-0 border-r border-gray-100">
              {i + 1}
            </span>
            <pre
              className={`flex-1 px-3 py-0.5 whitespace-pre-wrap break-all ${similarSet.has(i) ? "text-gray-900" : "text-gray-600"}`}
            >
              {line || " "}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );

  const linesA = (fragmentA?.source || "").split("\n");
  const linesB = (fragmentB?.source || "").split("\n");

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden bg-white">
      {/* Header row */}
      <div className="grid grid-cols-2 divide-x divide-gray-200 border-b border-gray-200 bg-gray-50">
        <div className="px-4 py-2.5">
          <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-0.5">
            Student A
          </p>
          <p className="text-xs font-bold text-gray-800 truncate">
            {fragmentA?.file || "—"}
          </p>
          {fragmentA?.name && (
            <p className="text-[10px] text-gray-500">
              fn:{" "}
              <span className="font-mono text-gray-700">{fragmentA.name}</span>{" "}
              · lines {fragmentA.start}–{fragmentA.end}
            </p>
          )}
        </div>
        <div className="px-4 py-2.5">
          <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-0.5">
            Student B
          </p>
          <p className="text-xs font-bold text-gray-800 truncate">
            {fragmentB?.file || "—"}
          </p>
          {fragmentB?.name && (
            <p className="text-[10px] text-gray-500">
              fn:{" "}
              <span className="font-mono text-gray-700">{fragmentB.name}</span>{" "}
              · lines {fragmentB.start}–{fragmentB.end}
            </p>
          )}
        </div>
      </div>
      {/* Code columns */}
      <div className="grid grid-cols-2 divide-x divide-gray-100 max-h-80 overflow-auto">
        {renderLines(linesA, "a")}
        {renderLines(linesB, "b")}
      </div>
    </div>
  );
};

// ─── Pair card (expandable) ───────────────────────────────────────────────────
const PairCard = ({ pair, rank }) => {
  const [open, setOpen] = useState(false);

  const score = pair.similarity ?? pair.combined_score ?? 0;
  const risk = getRisk(score);
  const R = RISK[risk];
  const pctVal = Math.round(score * 100);
  const navigate = useNavigate();
  
  // Clone pairs / fragments from matching_blocks
  const fragments = (() => {
    try {
      const mb = pair.matching_blocks;
      if (!mb) return [];
      const parsed = typeof mb === "string" ? JSON.parse(mb) : mb;
      if (Array.isArray(parsed)) return parsed;
      if (parsed.fragments) return parsed.fragments;
      return [];
    } catch {
      return [];
    }
  })();

  const cloneTypes = pair.clone_type
    ? pair.clone_type.split("_AND_").map((t) => t.replace("TYPE", "T"))
    : [];

  return (
    <div
      className={`rounded-2xl border overflow-hidden transition-all duration-200
      ${open ? "border-slate-300 shadow-md" : "border-gray-100 hover:border-gray-300 hover:shadow-sm"}`}
    >
      {/* Collapsed header */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full text-left px-6 py-5 bg-white flex items-center gap-4"
      >
        {/* Rank */}
        <span className="text-xs font-black text-gray-300 w-6 flex-shrink-0">
          #{rank}
        </span>

        {/* Score ring */}
        <div
          className={`w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 font-black text-sm ${R.bg} ${R.text}`}
        >
          {pctVal}%
        </div>

        {/* Students */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-gray-900 text-sm">
              {pair.student_a_name || "Student A"}
            </span>
            <span className="text-gray-300 text-xs">↔</span>
            <span className="font-bold text-gray-900 text-sm">
              {pair.student_b_name || "Student B"}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <RiskBadge score={score} />
            {cloneTypes.map((t) => (
              <span
                key={t}
                className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600"
              >
                {t}
              </span>
            ))}
            {fragments.length > 0 && (
              <span className="text-[10px] text-gray-400">
                {fragments.length} matching fragment
                {fragments.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>

        {/* Score breakdown mini */}
        <div className="hidden md:flex flex-col gap-1 min-w-[160px]">
          <div className="flex items-center gap-2 text-[10px] text-gray-400">
            <span className="w-12 text-right">Structural</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-violet-400 rounded-full"
                style={{
                  width: fmtScore(pair.structural_score || pair.type3_score),
                }}
              />
            </div>
            <span className="text-gray-600 font-semibold">
              {fmtScore(pair.structural_score || pair.type3_score)}
            </span>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-gray-400">
            <span className="w-12 text-right">Semantic</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-rose-400 rounded-full"
                style={{
                  width: fmtScore(pair.semantic_score || pair.type4_score),
                }}
              />
            </div>
            <span className="text-gray-600 font-semibold">
              {fmtScore(pair.semantic_score || pair.type4_score)}
            </span>
          </div>
        </div>

        {/* Chevron */}
        <svg
          className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      <button
        onClick={() =>
          navigate(`/analysis/pair/${pair.pair_id || "detail"}`, {
            state: { pair },
          })
        }
        className="px-4 py-2 rounded-lg text-xs font-bold bg-slate-900 text-white hover:bg-slate-700 transition-colors"
      >
        Full Comparison →
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="border-t border-gray-100 bg-gray-50/50 px-6 pb-6 pt-4 space-y-5">
          {/* Score breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              {
                label: "Type-1 (Exact)",
                score: pair.type1_score,
                color: "bg-blue-500",
              },
              {
                label: "Type-2 (Renamed)",
                score: pair.type2_score,
                color: "bg-violet-500",
              },
              {
                label: "Type-3 (Structural)",
                score: pair.structural_score || pair.type3_score,
                color: "bg-amber-500",
              },
              {
                label: "Type-4 (Semantic)",
                score: pair.semantic_score || pair.type4_score,
                color: "bg-rose-500",
              },
            ].map(({ label, score: s, color }) => (
              <div
                key={label}
                className="bg-white rounded-xl border border-gray-100 px-4 py-3"
              >
                <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-2">
                  {label}
                </p>
                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-1.5">
                  <div
                    className={`h-full rounded-full ${color}`}
                    style={{ width: s ? `${Math.round(s * 100)}%` : "0%" }}
                  />
                </div>
                <p className="text-lg font-black text-gray-900">
                  {s ? `${Math.round(s * 100)}%` : "—"}
                </p>
              </div>
            ))}
          </div>

          {/* Fragment comparisons */}
          {fragments.length > 0 ? (
            <div className="space-y-4">
              <p className="text-xs font-black uppercase tracking-widest text-gray-500">
                Matching Code Fragments ({fragments.length})
              </p>
              {fragments.slice(0, 5).map((frag, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-yellow-100 text-yellow-700">
                      Fragment {i + 1} ·{" "}
                      {frag.similarity
                        ? `${Math.round(frag.similarity * 100)}% match`
                        : "match"}
                    </span>
                  </div>
                  <CodeDiffBlock
                    fragmentA={{
                      file: frag.file_a,
                      name: frag.func_a,
                      start: frag.start_a,
                      end: frag.end_a,
                      source: frag.source_a,
                    }}
                    fragmentB={{
                      file: frag.file_b,
                      name: frag.func_b,
                      start: frag.start_b,
                      end: frag.end_b,
                      source: frag.source_b,
                    }}
                    similarLines={frag.similar_lines || []}
                  />
                </div>
              ))}
              {fragments.length > 5 && (
                <p className="text-xs text-gray-400 text-center">
                  + {fragments.length - 5} more fragments not shown
                </p>
              )}
            </div>
          ) : (
            /* No fragment data — show file-level info */
            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  label: "Submission A",
                  id: pair.submission_a_id,
                  name: pair.student_a_name,
                },
                {
                  label: "Submission B",
                  id: pair.submission_b_id,
                  name: pair.student_b_name,
                },
              ].map(({ label, id, name }) => (
                <div
                  key={label}
                  className="bg-white border border-gray-100 rounded-xl px-4 py-3"
                >
                  <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">
                    {label}
                  </p>
                  <p className="text-sm font-semibold text-gray-800">{name}</p>
                  {id && (
                    <Link
                      to={`/submissions/${id}`}
                      className="text-xs text-slate-600 hover:text-slate-900 font-semibold underline underline-offset-2 mt-1 inline-block"
                    >
                      View submission →
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Action links */}
          <div className="flex gap-2 pt-1">
            {pair.submission_a_id && (
              <Link
                to={`/submissions/${pair.submission_a_id}`}
                className="px-4 py-2 rounded-lg text-xs font-bold border border-gray-200 text-gray-700 hover:bg-white transition-colors"
              >
                Open Submission A
              </Link>
            )}
            {pair.submission_b_id && (
              <Link
                to={`/submissions/${pair.submission_b_id}`}
                className="px-4 py-2 rounded-lg text-xs font-bold border border-gray-200 text-gray-700 hover:bg-white transition-colors"
              >
                Open Submission B
              </Link>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Stat card ────────────────────────────────────────────────────────────────
const Stat = ({ label, value, sub, accent }) => (
  <div className="bg-white rounded-2xl border border-gray-100 px-6 py-5">
    <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">
      {label}
    </p>
    <p
      className={`text-3xl font-black tracking-tight ${accent || "text-gray-900"}`}
    >
      {value}
    </p>
    {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
  </div>
);

// ─── Main page ────────────────────────────────────────────────────────────────
const AnalysisResults = () => {
  const { assignmentId } = useParams();
  const [results, setResults] = useState(null);
  const [threshold, setThreshold] = useState(0.5);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // all | high | medium | low
  const [sort, setSort] = useState("score"); // score | name
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [assignmentId, threshold]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const data = await analysisService.getAssignmentResults(
        assignmentId,
        threshold * 100,
      );
      setResults(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const triggerAnalysis = async () => {
    setRunning(true);
    try {
      await analysisService.analyzeAssignment(assignmentId);
      setTimeout(fetchResults, 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  // Derive pairs
  const rawPairs = results?.highSimilarityPairs || [];

  const filtered = rawPairs.filter((p) => {
    const s = p.similarity ?? p.combined_score ?? 0;
    if (filter === "high") return s >= 0.7;
    if (filter === "medium") return s >= 0.5 && s < 0.7;
    if (filter === "low") return s < 0.5;
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sort === "name")
      return (a.student_a_name || "").localeCompare(b.student_a_name || "");
    const sa = a.similarity ?? a.combined_score ?? 0;
    const sb = b.similarity ?? b.combined_score ?? 0;
    return sb - sa;
  });

  const criticalCount = rawPairs.filter(
    (p) => getRisk(p.similarity ?? p.combined_score ?? 0) === "CRITICAL",
  ).length;
  const highCount = rawPairs.filter(
    (p) => getRisk(p.similarity ?? p.combined_score ?? 0) === "HIGH",
  ).length;
  const avgScore = rawPairs.length
    ? rawPairs.reduce(
        (s, p) => s + (p.similarity ?? p.combined_score ?? 0),
        0,
      ) / rawPairs.length
    : 0;

  return (
    <div
      className="min-h-screen bg-gray-50"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}
    >
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&display=swap');`}</style>

      {/* Top bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <Link
              to={`/assignments/${assignmentId}`}
              className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800 flex-shrink-0"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Assignment
            </Link>
            <span className="text-gray-200">|</span>
            <p className="text-xs font-black uppercase tracking-widest text-gray-400 truncate">
              Plagiarism Report
            </p>
          </div>
          <button
            onClick={triggerAnalysis}
            disabled={running}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-700 disabled:opacity-50 transition-all flex-shrink-0"
          >
            {running ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />{" "}
                Running…
              </>
            ) : (
              "▶ Re-run Analysis"
            )}
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        {/* Headline */}
        <div>
          <h1 className="text-2xl font-black text-gray-900 tracking-tight">
            Similarity Report
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            All {results?.results?.length || "—"} student files pooled and
            compared by language group. Showing {sorted.length} pair
            {sorted.length !== 1 ? "s" : ""} above {Math.round(threshold * 100)}
            % threshold.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat label="Total pairs" value={rawPairs.length} />
          <Stat
            label="Critical"
            value={criticalCount}
            sub="≥ 85% similarity"
            accent={criticalCount > 0 ? "text-red-600" : "text-gray-400"}
          />
          <Stat
            label="High risk"
            value={highCount}
            sub="70–85%"
            accent={highCount > 0 ? "text-amber-600" : "text-gray-400"}
          />
          <Stat
            label="Avg similarity"
            value={`${Math.round(avgScore * 100)}%`}
          />
        </div>

        {/* Alert banner if critical */}
        {criticalCount > 0 && (
          <div className="flex items-center gap-3 px-5 py-4 rounded-xl bg-red-50 border border-red-200">
            <span className="text-xl flex-shrink-0">🚨</span>
            <p className="text-sm text-red-800 font-semibold">
              {criticalCount} pair{criticalCount !== 1 ? "s" : ""} require
              immediate review — similarity ≥ 85%.
            </p>
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Threshold */}
          <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5">
            <span className="text-xs font-bold text-gray-500 flex-shrink-0">
              Min similarity
            </span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-32 accent-slate-900"
            />
            <span className="text-sm font-black text-slate-900 w-12">
              {Math.round(threshold * 100)}%
            </span>
          </div>

          {/* Filter chips */}
          <div className="flex gap-1.5">
            {["all", "high", "medium", "low"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all
                  ${filter === f ? "bg-slate-900 text-white" : "bg-white border border-gray-200 text-gray-600 hover:border-gray-400"}`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Sort */}
          <div className="ml-auto flex gap-1.5">
            {[
              ["score", "Sort by score"],
              ["name", "Sort by name"],
            ].map(([v, l]) => (
              <button
                key={v}
                onClick={() => setSort(v)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all
                  ${sort === v ? "bg-slate-100 text-slate-900" : "text-gray-500 hover:text-gray-800"}`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        {/* Pairs list */}
        {loading ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <span className="w-6 h-6 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-gray-500 font-medium">
              Loading results…
            </span>
          </div>
        ) : sorted.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-4">✅</span>
            <p className="font-bold text-gray-700 text-lg">
              No pairs above {Math.round(threshold * 100)}%
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Lower the threshold or re-run the analysis.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sorted.map((pair, i) => (
              <PairCard key={pair.pair_id || i} pair={pair} rank={i + 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;
