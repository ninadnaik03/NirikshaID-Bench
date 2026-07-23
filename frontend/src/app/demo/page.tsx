import { DemoExplorer } from "@/components/DemoExplorer";

export default function DemoPage() {
  return <div className="wrap">
    <div className="pageHead"><div className="eyebrow">Interactive demo</div><h1>Inspect evidence, not just verdicts.</h1><p className="sectionIntro">Compare the displayed fields, ground-truth tamper region, structured prediction, parser state, and recorded latency.</p></div>
    <DemoExplorer />
  </div>;
}

