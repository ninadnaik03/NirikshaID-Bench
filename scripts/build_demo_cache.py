import json

from niriksha_bench.api.main import gallery
from niriksha_bench.utils.paths import resolve_project_path

destination = resolve_project_path("data/demo_gallery/gallery-cache.json")
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(gallery(), indent=2), encoding="utf-8")
print(destination)

