import Image from "next/image";

export default function AboutPage() {
  return <div className="wrap">
    <div className="pageHead"><div className="eyebrow">About the work</div><h1>A compact research-engineering system, end to end.</h1><p className="sectionIntro">NirikshaID Bench connects dataset construction, model contracts, evaluation artifacts, failure analysis, an API, and a recruiter-friendly research interface.</p></div>
    <div className="grid"><div className="card"><h3>Python core</h3><p>Pydantic, Pillow, NumPy, RapidFuzz, FastAPI, and reproducible configuration.</p></div><div className="card"><h3>Web system</h3><p>Next.js, strict TypeScript, responsive CSS, accessible controls, and typed API data.</p></div><div className="card"><h3>Deployment</h3><p>Dockerized backend and frontend with environment-based API and CORS configuration.</p></div></div>
    <section className="section"><div className="author"><Image className="authorPhoto" src="/profile.jpg" width={192} height={192} sizes="(max-width: 600px) 112px, 128px" alt="Portrait of Ninad Naik" priority /><div><div className="eyebrow">Author</div><h2>Ninad Naik</h2><p>CS Student | AI/ML Research and Engineering</p><p className="muted">Research interests: multimodal learning, document intelligence, computer vision, language models, and reproducible evaluation.</p><div className="actions"><a className="button" href="https://github.com/ninadnaik03">GitHub</a><a className="button secondary" href="https://www.linkedin.com/in/ninad-naik-274883262/">LinkedIn</a></div></div></div></section>
    <section className="section"><h2>Honest project status</h2><div className="callout">The local deterministic baseline and full evaluation path are operational. Qwen inference and QLoRA are compute-dependent optional modules; no external-model score is shown unless that model is actually run.</div></section>
  </div>;
}
