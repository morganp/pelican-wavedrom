import logging
import os
from pelican import signals

logger = logging.getLogger(__name__)
_settings = {}

def _initialized(pelican):
    _settings['CONTENT_PATH'] = pelican.settings.get('PATH', 'content')
    _settings['WAVEDROM_CLI'] = pelican.settings.get('WAVEDROM_CLI', 'wavedrom-cli')

    img_dir = os.path.join(_settings['CONTENT_PATH'], 'images', 'wavedrom')
    os.makedirs(img_dir, exist_ok=True)

    # Inject Markdown extension — fires before MarkdownReader is constructed
    md = pelican.settings.setdefault('MARKDOWN', {})
    md.setdefault('extensions', [])
    ext = 'pelican.plugins.wavedrom_generator.preprocessor'
    if ext not in md['extensions']:
        md['extensions'].append(ext)

def register():
    signals.initialized.connect(_initialized)
