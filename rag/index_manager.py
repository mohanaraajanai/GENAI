import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

class IndexManifest:
    """Tracks PDF hashes so unchanged PDFs do not need unnecessary re-indexing."""
    def __init__(self, path='data/faiss_index/manifest.json'):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        return json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}

    def save(self, data):
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    @staticmethod
    def sha256(path):
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        return h.hexdigest()

    def scan(self, pdf_dir='downloads'):
        old = self.load().get('files', {})
        current = {}
        for pdf in sorted(Path(pdf_dir).glob('*.pdf')):
            current[pdf.name] = {
                'sha256': self.sha256(pdf),
                'size': pdf.stat().st_size,
                'modified': datetime.fromtimestamp(pdf.stat().st_mtime, tz=timezone.utc).isoformat()
            }
        changed = [n for n in current if old.get(n, {}).get('sha256') != current[n]['sha256']]
        removed = [n for n in old if n not in current]
        unchanged = [n for n in current if n not in changed]
        self.save({'updated_at': datetime.now(timezone.utc).isoformat(), 'files': current})
        return {'added_or_changed': changed, 'removed': removed, 'unchanged': unchanged}
