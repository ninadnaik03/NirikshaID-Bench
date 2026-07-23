import Link from "next/link";
import Image from "next/image";
import { LiveOverview } from "@/components/LiveOverview";

const pipeline = [
  ["01", "Synthetic Generator"], ["02", "Clean Card"], ["03", "Tamper Injection"], ["04", "Image Degradation"],
  ["05", "Model Inference"], ["06", "Structured Parsing"], ["07", "Evaluation"], ["08", "Failure Analysis"],
];

export default function Home() {
  return <div className="wrap">
    <section className="hero">
      <div>
        <div className="eyebrow">Open · Local-first · Reproducible</div>
        <h1>Inspect models.<br/><span>Expose failures.</span></h1>
        <p className="lead">NirikshaID Bench is a controlled synthetic testbed for identity-document extraction, tamper detection, localization, and robustness under visual degradation.</p>
        <div className="actions">
          <Link className="button" href="/demo">Open interactive demo →</Link>
          <Link className="button secondary" href="/results">View measured results</Link>
        </div>
        <p className="muted">One original layout. Five structured fields. Held-out digit-edit evaluation.</p>
      </div>
      <div className="terminal">
        <div className="terminalBar">LOCAL EVALUATION / STRUCTURED OUTPUT</div>
        <div className="json">{`{\n  "identity_number": "QBO820010I",\n  "tampered": true,\n  "tamper_type": "font_swap",\n  "tamper_bbox": [300, 429, 472, 461],\n  "evaluation": "held-out aware"\n}`}</div>
      </div>
    </section>

    <section className="section">
      <div className="eyebrow">Why this benchmark</div>
      <h2>Privacy constraints should not make evaluation opaque.</h2>
      <p className="sectionIntro">Real identity documents are sensitive and difficult to release. Controlled synthetic data makes labels, perturbations, and split logic auditable—but does not erase the synthetic-to-real domain gap.</p>
      <div className="grid">
        <div className="card"><h3>Extraction</h3><p>Measures whether visible names, dates, and identifiers survive structured parsing.</p></div>
        <div className="card"><h3>Tamper detection</h3><p>Separately measures whether a model identifies visual inconsistency and its type.</p></div>
        <div className="card"><h3>Generalization</h3><p>Excludes digit edits from tuning splits, then reports their recall independently.</p></div>
      </div>
    </section>

    <section className="section">
      <div className="eyebrow">Pipeline</div><h2>Every transformation is traceable.</h2>
      <div className="pipeline">{pipeline.map(([n, label]) => <div className="step" key={n}>{label}<small>{n} / deterministic stage</small></div>)}</div>
    </section>

    <section className="section">
      <div className="eyebrow">Dataset + results</div><h2>Numbers loaded from real local artifacts.</h2>
      <LiveOverview />
    </section>

    <section className="section">
      <div className="eyebrow">Methodology</div><h2>Designed to make leakage difficult.</h2>
      <div className="grid">
        <div className="card"><h3>Seeded generation</h3><p>Every label records the document seed and generator version for replay.</p></div>
        <div className="card"><h3>Schema enforcement</h3><p>Pydantic validates tamper state, identity format, boxes, images, and split membership.</p></div>
        <div className="card"><h3>Common contract</h3><p>Adapters emit the same strict JSON structure with parser and latency metadata.</p></div>
      </div>
      <p className="callout" style={{marginTop:24}}>NirikshaID Bench evaluates extraction and forgery classification alongside paired intervention sensitivity, hard-negative false positives, held-out tamper generalization, and uncertainty calibration.</p>
    </section>

    <section className="section">
      <div className="eyebrow">Limitations</div><h2>Useful evidence, bounded claims.</h2>
      <div className="callout">This benchmark does not establish production fraud-detection performance. It covers one synthetic layout, English fields, and a limited tamper taxonomy. VLM explanations may not be faithful.</div>
      <div className="grid">
        <div className="card"><h3>Domain gap</h3><p>Synthetic cards cannot represent the full distribution of real capture conditions.</p></div>
        <div className="card"><h3>Roadmap</h3><p>Multiple layouts, multilingual text, screen recapture, subtler forgeries, and private validation.</p></div>
        <div className="card"><h3>Optional tuning</h3><p>QLoRA configuration is isolated from the critical evaluation path and never sees digit edits.</p></div>
      </div>
    </section>

    <section className="section author">
      <Image className="authorPhoto" src="/profile.jpg" width={192} height={192} sizes="(max-width: 600px) 112px, 128px" alt="Portrait of Ninad Naik" priority />
      <div><div className="eyebrow">Author</div><h2 style={{margin:"8px 0"}}>Ninad Naik</h2><p className="muted">CS Student | AI/ML Research and Engineering</p><p>Interested in large language models, multimodal learning, document intelligence, computer vision, and reproducible AI evaluation.</p></div>
    </section>
  </div>;
}
