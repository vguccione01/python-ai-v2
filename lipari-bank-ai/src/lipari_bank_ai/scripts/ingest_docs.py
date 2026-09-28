import asyncio
from pathlib import Path

import httpx


async def main() -> None:
    docs_dir = Path("data/docs")
    # rglob è ricorsivo: i documenti nelle sottocartelle (es. compliance_only/)
    # prendono la visibility dal nome della cartella che li contiene.
    paths = await asyncio.to_thread(lambda: sorted(docs_dir.rglob("*.md")))

    print(f"Paths: {paths}")
    async with httpx.AsyncClient(timeout=60.0) as client:
        for path in paths:
            content = await asyncio.to_thread(path.read_text)
            relative_parent = path.parent.relative_to(docs_dir)
            visibility = relative_parent.name if str(relative_parent) != "." else "public"
            response = await client.post(
                "http://localhost:8000/api/ai/documents/ingest",
                json={
                    "document_id": path.stem,
                    "content": content,
                    "visibility": visibility,
                    "metadata": {"source": str(path), "title": path.stem.replace("_", " ")},
                },
            )
            # chunk_count == 0 => il documento era già presente ed è stato saltato.
            stato = "SKIP (gia' presente)" if response.json()["chunk_count"] == 0 else "OK"
            print(f"{path.name}: {stato} - {response.json()}")


if __name__ == "__main__":
    asyncio.run(main())
