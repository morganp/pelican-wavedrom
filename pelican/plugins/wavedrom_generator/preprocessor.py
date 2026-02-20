from __future__ import annotations
import hashlib, logging, os, re, subprocess, tempfile
from markdown import Extension
from markdown.preprocessors import Preprocessor
from pelican.plugins.wavedrom_generator import _settings

logger = logging.getLogger(__name__)

WAVEDROM_FENCE_RE = re.compile(
    r'^(?P<fence>`{3,}|~{3,})[ \t]*wavedrom[ \t]*\n'
    r'(?P<json>.*?)'
    r'^(?P=fence)[ \t]*$',
    re.MULTILINE | re.DOTALL
)

class WaveDromPreprocessor(Preprocessor):
    def run(self, lines):
        text = '\n'.join(lines)
        return WAVEDROM_FENCE_RE.sub(self._replace, text).split('\n')

    def _replace(self, match):
        return _render_or_cached(match.group('json').strip())

class WaveDromExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(WaveDromPreprocessor(md), 'wavedrom_block', 27)

def makeExtension(**kwargs):
    return WaveDromExtension(**kwargs)

def _render_or_cached(json_content):
    content_path = _settings.get('CONTENT_PATH', 'content')
    cli = _settings.get('WAVEDROM_CLI', 'wavedrom-cli')
    h = hashlib.md5(json_content.encode()).hexdigest()
    filename = f'wavedrom_{h}.svg'
    svg_path = os.path.join(content_path, 'images', 'wavedrom', filename)

    if os.path.exists(svg_path):
        return _img_ref(filename)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            tmp_path = f.name
        r = subprocess.run(
            [cli, '-i', tmp_path, '-s', svg_path],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            logger.warning('wavedrom: CLI failed: %s', r.stderr.strip())
            return _fallback(json_content)
        logger.info('wavedrom: rendered %s', filename)
        return _img_ref(filename)
    except FileNotFoundError:
        logger.warning('wavedrom: wavedrom-cli not found. Install with: npm install -g wavedrom-cli')
        return _fallback(json_content)
    except subprocess.TimeoutExpired:
        logger.warning('wavedrom: timed out')
        return _fallback(json_content)
    finally:
        if tmp_path:
            try: os.unlink(tmp_path)
            except OSError: pass

def _img_ref(filename):
    return f'![WaveDrom timing diagram]({{static}}/images/wavedrom/{filename})'

def _fallback(json_content):
    return f'```json\n{json_content}\n```'
