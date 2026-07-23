"use client";

import { useEffect, useState } from "react";
import { staticDemoItems } from "@/data/static-data";

export function DemoExplorer() {
  const items = staticDemoItems;
  const [selected, setSelected] = useState(0);
  const [showTruth, setShowTruth] = useState(true);
  const [analysisStage, setAnalysisStage] = useState(-1);
  useEffect(() => {
    if (analysisStage < 0 || analysisStage >= ANALYSIS_STEPS.length - 1) return;
    const timer = window.setTimeout(() => setAnalysisStage((stage) => stage + 1), 720);
    return () => window.clearTimeout(timer);
  }, [analysisStage]);
  if (!items.length) return <p className="muted">No deployment gallery samples are available.</p>;
  const item = items[selected];
  const prediction = item.predictions[0];
  const extractionMatches = Object.entries(item.ground_truth.displayed_fields).filter(
    ([field, value]) => prediction.prediction.fields[field] === value
  ).length;
  const extractionAgreement = extractionMatches / Object.keys(item.ground_truth.displayed_fields).length;
  const verdictCorrect = prediction.prediction.tampered === item.tampered;
  const typeCorrect = prediction.prediction.tamper_type === item.tamper_type;
  const bbox = showTruth ? item.ground_truth.tamper_bbox : prediction.prediction.tamper_bbox;
  const style = bbox ? {
    left: `${bbox[0] / 960 * 100}%`, top: `${bbox[1] / 600 * 100}%`,
    width: `${(bbox[2] - bbox[0]) / 960 * 100}%`, height: `${(bbox[3] - bbox[1]) / 600 * 100}%`,
  } : undefined;
  return <>
    <div className="demoLayout">
      <div className="sampleList" aria-label="Gallery samples">
        {items.map((sample, index) => <button className={`sample ${index === selected ? "active" : ""}`} onClick={() => { setSelected(index); setAnalysisStage(-1); }} key={sample.doc_id}>
          <b>{sample.doc_id}</b><br/><span className={sample.tampered ? "danger" : "muted"}>{sample.tamper_type}</span>
        </button>)}
      </div>
      <div>
        <div className="imageStage">
          {/* Intentionally using a plain image because backend URLs are runtime-configurable. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={item.image_url} alt={`Synthetic identity card ${item.doc_id}`} />
          {bbox && <div className="bbox" style={style} />}
        </div>
        <label className="toggle"><input type="checkbox" checked={showTruth} onChange={(event) => setShowTruth(event.target.checked)} /> Show ground-truth box (off = model box)</label>
        <div>{item.degradations.map((d) => <span className="tag" key={d.type}>{d.type} {d.severity}</span>)}</div>
      </div>
      <div className="card">
        <div className="eyebrow">Label-derived Demo Stub</div>
        <h3>{prediction.prediction.tampered ? "Tamper detected" : "No tamper detected"}</h3>
        <p><span className="tag">{prediction.prediction.tamper_type}</span> confidence {(prediction.prediction.confidence * 100).toFixed(1)}%</p>
        <div className="fieldList">{Object.entries(prediction.prediction.fields).map(([key, value]) => <div key={key}><span>{key}</span>{value}</div>)}</div>
        <p className="muted">{prediction.prediction.reason}</p>
        <p className="muted">{prediction.latency_ms.toFixed(1)} ms · parser {prediction.parser_repaired ? "repaired" : "valid first pass"}</p>
      </div>
    </div>
    <section className="analysisWalkthrough">
      <div>
        <div className="eyebrow">Preloaded research dataset</div>
        <h2>Trace one document through the evaluation pipeline.</h2>
        <p className="muted">Use the selected synthetic sample to replay how an image becomes a structured, scored prediction. This walkthrough uses the existing precomputed gallery output and clearly separates inference from ground-truth scoring.</p>
        <button className="button" onClick={() => setAnalysisStage(0)} disabled={analysisStage >= 0 && analysisStage < ANALYSIS_STEPS.length - 1}>
          {analysisStage === ANALYSIS_STEPS.length - 1 ? "Analyze again" : analysisStage >= 0 ? "Analysis running…" : "Analyze selected document"}
        </button>
      </div>
      <div className="analysisStagePanel" aria-live="polite">
        {analysisStage < ANALYSIS_STEPS.length - 1 ? <ol className="analysisSteps">
          {ANALYSIS_STEPS.map((step, index) => <li className={analysisStage >= index ? "complete" : ""} key={step.title}>
            <span>{index + 1}</span><div><b>{step.title}</b><p>{step.copy}</p></div>
          </li>)}
        </ol> : <div className="analysisResult">
          <div className="resultHeader"><div><div className="eyebrow">Analysis complete</div><h3>{verdictCorrect ? "Verdict agrees with the label" : "Review recommended"}</h3></div><span className={verdictCorrect ? "resultBadge good" : "resultBadge warning"}>{verdictCorrect ? "PASS" : "MISMATCH"}</span></div>
          <div className="resultMetrics">
            <div><span>Verdict</span><strong>{prediction.prediction.tampered ? "Tampered" : "Genuine"}</strong><small>Ground truth: {item.tampered ? "Tampered" : "Genuine"}</small></div>
            <div><span>Confidence</span><strong>{(prediction.prediction.confidence * 100).toFixed(1)}%</strong><small>Reported by adapter</small></div>
            <div><span>Field agreement</span><strong>{(extractionAgreement * 100).toFixed(0)}%</strong><small>{extractionMatches}/5 visible fields</small></div>
            <div><span>Latency</span><strong>{prediction.latency_ms.toFixed(1)} ms</strong><small>Saved inference record</small></div>
          </div>
          <div className="resultChecks">
            <p><span className={typeCorrect ? "check good" : "check warning"}>{typeCorrect ? "✓" : "!"}</span><span><b>Tamper type:</b> predicted {prediction.prediction.tamper_type}; expected {item.tamper_type}</span></p>
            <p><span className="check good">✓</span><span><b>Structured output:</b> {prediction.parser_repaired ? "accepted after parser repair" : "valid on the first pass"}</span></p>
            <p><span className={prediction.prediction.tamper_bbox ? "check good" : "check neutral"}>{prediction.prediction.tamper_bbox ? "✓" : "—"}</span><span><b>Localization:</b> {prediction.prediction.tamper_bbox ? "a predicted region is available for overlay review" : "no predicted region was returned"}</span></p>
          </div>
          <div className="resultInterpretation"><b>Research interpretation</b><p>{verdictCorrect && typeCorrect ? "The adapter preserved the visible fields and matched the injected tamper decision for this sample." : "At least one decision differs from the held-back label. Inspect the image and overlays to decide whether the failure is perceptual, classification-related, or localization-related."}</p></div>
        </div>}
      </div>
    </section>
    <div className="callout" style={{marginTop: 24}}>This gallery panel is a label-derived UI stub and is excluded from every benchmark result. Use the Results page for image-only OCR and Qwen runs.</div>
  </>;
}

const ANALYSIS_STEPS = [
  { title: "Load the document image", copy: "Read only the selected card pixels; no label or manifest enters inference." },
  { title: "Prepare visual evidence", copy: "Normalize the image and preserve text regions, degradation cues, and possible tamper boundaries." },
  { title: "Run the configured adapter", copy: "Transcribe fields and estimate the tamper verdict, type, confidence, and localization." },
  { title: "Validate structured output", copy: "Check the JSON contract and record malformed or missing values as failures." },
  { title: "Compare with held-back labels", copy: "Only after prediction, score extraction, verdict, type, confidence, and bounding-box overlap." },
  { title: "Surface the research finding", copy: "Show whether the error came from perception, reasoning, formatting, calibration, or localization." },
];
