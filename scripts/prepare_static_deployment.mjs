import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const dataDir = join(root, "frontend", "src", "data");
const publicDir = join(root, "frontend", "public");

await mkdir(dataDir, { recursive: true });
await mkdir(join(publicDir, "demo"), { recursive: true });
await mkdir(join(publicDir, "failures"), { recursive: true });

const copies = [
  ["data/generated/manifests/stats.json", "frontend/src/data/stats.json"],
  ["data/results/summary.json", "frontend/src/data/summary.json"],
  [
    "data/diagnostics/results/template-aware-tesseract-ocr/metrics.json",
    "frontend/src/data/diagnostics.json",
  ],
  [
    "data/diagnostics/results/template-aware-tesseract-ocr/failures.json",
    "frontend/src/data/diagnostic-failures.json",
  ],
];

for (const [source, destination] of copies) {
  const target = join(root, destination);
  await mkdir(dirname(target), { recursive: true });
  await copyFile(join(root, source), target);
}

const lines = (await readFile(
  join(root, "data", "generated", "manifests", "demo_gallery.jsonl"),
  "utf8",
))
  .trim()
  .split(/\r?\n/)
  .slice(0, 8);

const items = [];
for (const line of lines) {
  const label = JSON.parse(line);
  const imageName = `${label.doc_id}.jpg`;
  await copyFile(
    join(root, "data", "generated", "images", imageName),
    join(publicDir, "demo", imageName),
  );
  items.push({
    doc_id: label.doc_id,
    image_url: `/demo/${imageName}`,
    split: label.split,
    tampered: label.tampered,
    tamper_type: label.tamper_type,
    degradations: label.degradations,
    ground_truth: label,
    predictions: [{
      latency_ms: 0,
      parser_repaired: false,
      prediction: {
        fields: label.displayed_fields,
        tampered: label.tampered,
        tamper_type: label.tamper_type,
        tampered_field: label.tampered_field,
        tamper_bbox: label.tamper_bbox,
        confidence: 1,
        reason: "Precomputed label-derived Demo Stub output for interface walkthrough only.",
      },
    }],
  });
}
await writeFile(
  join(dataDir, "demo-gallery.json"),
  `${JSON.stringify({ items, total: items.length }, null, 2)}\n`,
  "utf8",
);

const failures = JSON.parse(
  await readFile(
    join(
      root,
      "data",
      "diagnostics",
      "results",
      "template-aware-tesseract-ocr",
      "failures.json",
    ),
    "utf8",
  ),
).slice(0, 12);

for (const failure of failures) {
  const source = join(
    root,
    "data",
    "diagnostics",
    failure.image_url.includes("/pairs/") ? "pairs" : "hard_negatives",
    `${failure.doc_id}.jpg`,
  );
  const destination = join(publicDir, "failures", `${failure.doc_id}.jpg`);
  try {
    await copyFile(source, destination);
  } catch {
    // A missing optional image remains a documented failure without a thumbnail.
  }
}

console.log(`Prepared ${items.length} demo samples and ${failures.length} failure records.`);
