import json
import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure heavy data initializers in controllers are skipped in local runs
    os.environ.setdefault("SKIP_DATA_INIT", "1")

    # Add repo root to PYTHONPATH so `import app` works when executing directly
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from app.main import app

    openapi_schema = app.openapi()

    # Write to a deterministic location inside the repo so it can be served or consumed
    output_dir = Path(__file__).resolve().parent.parent / "app" / "static" / "docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "openapi.json"
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(openapi_schema, fp, indent=2)

    print(f"OpenAPI schema written to {output_path}")


if __name__ == "__main__":
    main()


