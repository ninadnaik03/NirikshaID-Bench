import { ResultsExplorer } from "@/components/ResultsExplorer";

export default function ResultsPage() {
  return <div className="wrap"><div className="pageHead"><div className="eyebrow">Benchmark results</div><h1>Seen and unseen failures stay separate.</h1><p className="sectionIntro">Normalized exact match preserves meaningful characters. Held-out recall is reported independently, and missing localization predictions are not silently scored as successes.</p></div><ResultsExplorer /></div>;
}

