const stages = [
  ["Generate", "Seeded fictional names, dates, identifiers, and procedural avatars."],
  ["Render", "One original landscape layout with stored field bounding boxes."],
  ["Tamper", "Font swap, copy/paste splice, or one-character digit edit."],
  ["Degrade", "Blur, Gaussian noise, and JPEG compression applied after tampering."],
  ["Infer", "A versioned prompt and common model-adapter contract."],
  ["Evaluate", "Extraction, detection, type, localization, robustness, and efficiency."],
];

export default function MethodologyPage() {
  return <div className="wrap">
    <div className="pageHead"><div className="eyebrow">Research methodology</div><h1>Controlled interventions. Auditable labels.</h1><p className="sectionIntro">The benchmark is designed around deterministic replay, strict schema validation, and an explicit held-out generalization test.</p></div>
    <div className="grid">{stages.map(([title, text], index) => <div className="card" key={title}><div className="eyebrow">0{index + 1}</div><h3>{title}</h3><p>{text}</p></div>)}</div>
    <section className="section"><h2>Strict label contract</h2><div className="terminal"><div className="json">{`{\n  "doc_id": "nid_000501",\n  "fields": { "...": "clean source values" },\n  "displayed_fields": { "...": "visible values" },\n  "tamper_type": "digit_edit",\n  "tamper_bbox": [x1, y1, x2, y2],\n  "split": "eval_unseen",\n  "seed": 20261224\n}`}</div></div></section>
    <section className="section"><h2>Held-out design</h2><p className="sectionIntro">The schema rejects any <code>digit_edit</code> example in train or validation. The validator independently checks manifests and requires digit edits in <code>eval_unseen</code>. Seen and unseen results are saved in separate artifacts.</p></section>
    <section className="section"><div className="eyebrow">Diagnostic v1.1</div><h2>Test the causal intervention, not just the class label.</h2><div className="grid"><div className="card"><h3>Counterfactual pairs</h3><p>Thirty pairs share identity, avatar, layout, and degradation seed. Only the tamper intervention changes, isolating verdict sensitivity and extraction spillover.</p></div><div className="card"><h3>Hard negatives</h3><p>Forty genuine cards contain suspicious but legitimate rendering conditions. False-positive rates reveal whether unusual appearance is being mistaken for manipulation.</p></div><div className="card"><h3>Selective review</h3><p>ECE, Brier score, reliability bins, and risk–coverage curves test whether low-confidence cases can be escalated instead of forcing a verdict.</p></div></div></section>
    <section className="section"><h2>Metrics</h2><div className="grid"><div className="card"><h3>Extraction</h3><p>Exact match, normalized exact match, character error rate, and fuzzy similarity per field.</p></div><div className="card"><h3>Tamper + pairs</h3><p>F1, false-positive rate, pairwise probability change, correct verdict flips, and outside-field stability.</p></div><div className="card"><h3>Uncertainty</h3><p>Expected Calibration Error, Brier score, reliability bins, abstentions, and selective accuracy at review thresholds.</p></div></div></section>
    <section className="section"><h2>Safeguards</h2><div className="callout">No official symbols, seals, signatures, QR codes, layouts, or real identities are used. Cards are visibly marked synthetic and are unsuitable for identification.</div></section>
  </div>;
}
