"use client";

import { useEffect, useState } from "react";
import { API_BASE, BenchmarkRun, fetchApi, Stats } from "@/lib/api";

export function LiveOverview() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [runs, setRuns] = useState<BenchmarkRun[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchApi<Stats>("/api/dataset/stats"),
      fetchApi<{ runs: BenchmarkRun[] }>("/api/benchmark/summary"),
    ]).then(([nextStats, summary]) => {
      setStats(nextStats);
      setRuns(summary.runs || []);
    }).catch(() => setError(true));
  }, []);

  if (error) return <div className="callout">Local API is offline. Start the backend at {API_BASE} to load generated statistics.</div>;
  if (!stats) return <p className="muted">Loading local benchmark artifacts…</p>;
  const seen = runs.find((run) => run.split === "eval_seen");
  const unseen = runs.find((run) => run.split === "eval_unseen");
  return (
    <>
      <div className="grid">
        <div className="card stat"><strong>{stats.total}</strong><span>generated documents</span></div>
        <div className="card stat"><strong>{stats.tampered?.true ?? "—"}</strong><span>tampered samples</span></div>
        <div className="card stat"><strong>digit_edit</strong><span>held-out tamper</span></div>
      </div>
      <div className="card" style={{marginTop: 16}}>
        <div className="status"><span className="dot" /> Data source: local generated manifests</div>
        {seen ? <>
          <h3>Measured offline baseline</h3>
          <Metric label="Field exact match · seen" value={seen.field_extraction.macro_normalized_exact_match} />
          <Metric label="Tamper F1 · seen" value={seen.tamper_detection.f1} />
          {unseen?.held_out_digit_edit && <Metric label="Held-out digit-edit recall" value={unseen.held_out_digit_edit.recall} />}
          <p className="muted">This deterministic heuristic proves the evaluation path; it is explicitly not presented as a VLM result.</p>
        </> : <p>Benchmark not yet executed locally.</p>}
      </div>
    </>
  );
}

export function Metric({label, value}: {label: string; value: number}) {
  const percent = Math.round(value * 1000) / 10;
  return <div className="chartRow"><span>{label}</span><div className="bar"><i style={{width: `${percent}%`}} /></div><b>{percent}%</b></div>;
}

