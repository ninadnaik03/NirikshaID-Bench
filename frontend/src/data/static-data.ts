import diagnosticFailuresJson from "./diagnostic-failures.json";
import diagnosticsJson from "./diagnostics.json";
import demoGalleryJson from "./demo-gallery.json";
import statsJson from "./stats.json";
import summaryJson from "./summary.json";
import type { BenchmarkRun, GalleryItem, Stats } from "@/lib/api";

export const staticStats = statsJson as Stats;
export const staticRuns = summaryJson.runs as BenchmarkRun[];
export const staticDemoItems = demoGalleryJson.items as GalleryItem[];
export const staticDiagnostics = diagnosticsJson;
export const staticDiagnosticFailures = diagnosticFailuresJson;
