"use client";

import { useState } from "react";
import {
  staticDiagnosticFailures,
  staticDiagnostics,
  staticRuns,
} from "@/data/static-data";
import type { BenchmarkRun } from "@/lib/api";
import { Metric } from "./LiveOverview";

export function ResultsExplorer() {
  const [runs] = useState<BenchmarkRun[]>(staticRuns);
  const [failures] = useState<FailureExample[]>(
    staticDiagnosticFailures.slice(0, 12) as FailureExample[],
  );
  const [diagnostics] = useState<DiagnosticSummary>(
    staticDiagnostics as DiagnosticSummary,
  );
  if (!runs.length) return <div className="callout">Benchmark not yet executed locally.</div>;
  return <>
    <div className="tableWrap"><table className="dataTable"><thead><tr><th>Model</th><th>Split</th><th>Samples</th><th>Field NEM</th><th>Tamper F1</th><th>Type macro F1</th><th>Median latency</th></tr></thead>
      <tbody>{runs.map((run) => <tr key={`${run.model.id}-${run.split}`}><td>{run.model.display_name}<br/><span className="muted">{run.model.kind}</span></td><td>{run.split}</td><td>{run.samples}</td><td>{pct(run.field_extraction.macro_normalized_exact_match)}</td><td>{pct(run.tamper_detection.f1)}</td><td>{pct(run.tamper_type.macro_f1)}</td><td>{run.efficiency.median_latency_ms.toFixed(1)} ms</td></tr>)}</tbody>
    </table></div>
    {runs.map((run) => <div className="card" style={{marginTop: 18}} key={`${run.model.id}-${run.run_name}`}>
      <div className="eyebrow">{run.model.display_name}</div>
      <div className="modelMeta">
        <span><b>Mode</b>{run.model.mode}</span><span><b>Quantization</b>{run.model.quantization}</span>
        <span><b>Dataset</b>v{run.dataset_version}</span><span><b>Split</b>{run.split}</span>
        <span><b>Samples</b>{run.samples}</span><span><b>Prompt</b>{run.prompt_version}</span>
      </div>
      {run.small_sample_warning && <p className="callout">Small diagnostic run: interpret these estimates cautiously.</p>}
      <h3>{run.split.replace("_", " ")} · field extraction</h3>
      {Object.entries(run.field_extraction.per_field).map(([field, scores]) => <Metric key={field} label={field.replaceAll("_", " ")} value={scores.normalized_exact_match} />)}
      <div className="grid">
        <div><span className="muted">Localization mean IoU</span><h3>{run.localization.mean_iou === null ? "N/A" : pct(run.localization.mean_iou)}</h3></div>
        <div><span className="muted">JSON parse success</span><h3>{pct(run.efficiency.parse_success_rate)}</h3></div>
        <div><span className="muted">Held-out digit-edit recall</span><h3>{run.held_out_digit_edit ? `${pct(run.held_out_digit_edit.recall)} — ${run.held_out_digit_edit.support} samples` : "N/A"}</h3></div>
      </div>
      <h3>Clean versus degraded</h3>
      <div className="tableWrap"><table className="dataTable"><thead><tr><th>Clean field EM</th><th>Clean support</th><th>Degraded field EM</th><th>Degraded support</th><th>Performance drop</th></tr></thead><tbody><tr><td>{nullablePct(run.robustness.clean_field_em)}</td><td>{run.robustness.clean_support}</td><td>{nullablePct(run.robustness.degraded_field_em)}</td><td>{run.robustness.degraded_support}</td><td>{nullablePct(run.robustness.performance_drop)}</td></tr></tbody></table></div>
      <p className="muted">Confusion matrix [TN, FP] / [FN, TP]: {JSON.stringify(run.tamper_detection.confusion_matrix)}</p>
    </div>)}
    <p className="callout" style={{marginTop:24}}>The fixed template makes region localization and OCR comparatively easy. Tamper-type generalization remains substantially harder, especially for the held-out digit-edit intervention.</p>
    {diagnostics?.status === "completed" && <section className="section">
      <div className="eyebrow">Research diagnostics · v{diagnostics.diagnostic_version}</div>
      <h2>Odd-looking does not necessarily mean tampered.</h2>
      <p className="sectionIntro">Hard negatives and causal pairs expose behavior hidden by aggregate F1. All values below are measured from image-only OCR/RF predictions.</p>
      <div className="grid">
        <div className="card stat"><strong>{pct(diagnostics.hard_negatives.false_positive_rate)}</strong><span>hard-negative false positives · {diagnostics.hard_negatives.samples} samples</span></div>
        <div className="card stat"><strong>{pct(diagnostics.counterfactual_pairs.correct_verdict_flip_rate)}</strong><span>correct causal verdict flips · {diagnostics.counterfactual_pairs.pairs} pairs</span></div>
        <div className="card stat"><strong>{diagnostics.calibration.ece.toFixed(3)}</strong><span>expected calibration error · {diagnostics.calibration.samples} decisions</span></div>
      </div>
      <div className="grid">
        <div className="card"><h3>F1 under hard negatives</h3><Metric label="Before" value={diagnostics.hard_negatives.tamper_f1_before} /><Metric label="After" value={diagnostics.hard_negatives.tamper_f1_after} /></div>
        <div className="card"><h3>Pairwise intervention</h3><p>Mean tamper-probability change: <b>{diagnostics.counterfactual_pairs.pairwise_tamper_sensitivity.toFixed(3)}</b></p><p>Outside-field extraction stability: <b>{pct(diagnostics.counterfactual_pairs.outside_field_extraction_stability)}</b></p></div>
        <div className="card"><h3>Uncertainty</h3><p>Brier score: <b>{diagnostics.calibration.brier_score.toFixed(3)}</b></p>{diagnostics.calibration.selective_operating_points.map((point) => <p key={point.target_review_rate}>{pct(point.target_review_rate)} review → {pct(point.selective_accuracy)} selective accuracy; {point.errors_avoided} errors avoided</p>)}</div>
      </div>
      <h3>Hard-negative false-positive rate by condition</h3>
      <div className="card">{Object.entries(diagnostics.hard_negatives.by_type).map(([kind, metric]) => <Metric key={kind} label={`${kind.replaceAll("_", " ")} · n=${metric.support}`} value={metric.false_positive_rate} />)}</div>
      <h3>Reliability diagram data</h3>
      <div className="card">{diagnostics.calibration.bins.map((bin) => <div className="reliabilityRow" key={bin.lower}><span>{bin.lower.toFixed(1)}–{bin.upper.toFixed(1)} · n={bin.support}</span><div><i style={{width:`${bin.mean_confidence * 100}%`}}/><em style={{left:`${bin.accuracy * 100}%`}} title={`Observed accuracy ${pct(bin.accuracy)}`} /></div><b>{pct(bin.accuracy)}</b></div>)}</div>
    </section>}
    <section className="section"><div className="eyebrow">Failure analysis</div><h2>Where image-only systems break</h2><div className="failureGrid">{failures.map((failure) => <article className="card" key={`${failure.doc_id}-${failure.failure_category}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img className="failureImage" src={`/failures/${failure.doc_id}.jpg`} alt={`Failure example ${failure.doc_id}`} />
      <p><span className="tag">{failure.failure_category}</span><span className="tag">{failure.tamper_type}</span></p>
      <h3>{failure.doc_id}</h3><p>{failure.reason}</p>
      <details><summary>Prediction versus ground truth</summary><pre className="miniJson">{JSON.stringify({truth: failure.ground_truth.tamper_type, prediction: failure.prediction?.tamper_type ?? "parse failure"}, null, 2)}</pre></details>
    </article>)}</div></section>
  </>;
}

function pct(value: number) { return `${(value * 100).toFixed(1)}%`; }
function nullablePct(value: number | null) { return value === null ? "N/A" : pct(value); }

type FailureExample = {
  doc_id: string;
  image_url: string;
  tamper_type: string;
  failure_category: string;
  reason: string;
  ground_truth: { tamper_type: string };
  prediction: { tamper_type: string } | null;
};

type DiagnosticSummary = {
  status: string;
  diagnostic_version: string;
  hard_negatives: {
    samples: number; false_positive_rate: number; tamper_f1_before: number; tamper_f1_after: number;
    by_type: Record<string, {false_positive_rate: number; support: number}>;
  };
  counterfactual_pairs: {
    pairs: number; pairwise_tamper_sensitivity: number; correct_verdict_flip_rate: number;
    outside_field_extraction_stability: number;
  };
  calibration: {
    samples: number; brier_score: number; ece: number;
    bins: {lower:number; upper:number; support:number; accuracy:number; mean_confidence:number}[];
    selective_operating_points: {target_review_rate:number; selective_accuracy:number; errors_avoided:number}[];
  };
};
