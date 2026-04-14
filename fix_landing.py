
import re

css_to_add = '''
    /* ═══════════════════════════════════════
       RESTORED LAYOUT CLASSES
    ═══════════════════════════════════════ */
    .grid-2 {
        display:grid; grid-template-columns:1fr 1fr;
        gap: clamp(3rem,5vw,5rem); align-items:center;
    }
    
    .btn-group {
        display:flex; flex-wrap:wrap; gap:1rem; 
        justify-content:center; margin-top:3rem; 
    }
    
    /* Reveal Animations */
    .reveal {
        opacity:0; transform:translateY(30px);
        transition: opacity .8s ease, transform .8s ease;
    }
    .reveal.active, .reveal.visible { opacity:1; transform:translateY(0); }
    .reveal-delay-1 { transition-delay:.15s; }
    .reveal-delay-2 { transition-delay:.3s; }
    .reveal-delay-3 { transition-delay:.45s; }
    .reveal-delay-4 { transition-delay:.6s; }
    
    /* Stats Strip */
    .stats-strip {
        background: var(--bg-primary);
        margin-top: -2.5rem; position: relative; z-index: 10;
        border-radius: 20px; box-shadow: var(--shadow-soft);
        padding: 2rem 0;
    }
    
    /* Feature Icons */
    .feat { display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 2rem; }
    .feat-icon {
        width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        transition: transform .3s;
    }
    .feat:hover .feat-icon { transform: scale(1.12); }
    .feat-icon.blue { background: rgba(59,130,246,.12); color: var(--status-info); }
    .feat-icon.red  { background: rgba(239,68,68,.12); color: var(--status-danger); }
    .feat-icon.gold { background: rgba(245,158,11,.12); color: var(--accent-color); }
    
    @media(max-width: 991px) {
        .grid-2 { grid-template-columns: 1fr; }
        .stats-inner { flex-direction: column; align-items: center; gap: 2rem; }
    }
'''

with open('templates/landing.html', 'r', encoding='utf8') as f:
    text = f.read()

# Replace colors
replacements = {
    'var(--cream)': 'var(--bg-primary)',
    'var(--cream-mid)': 'var(--bg-secondary)',
    'var(--blue-dark)': 'var(--brand-color)',
    'var(--blue-light)': 'var(--brand-light)',
    'var(--red)': 'var(--status-danger)',
    'var(--gold)': 'var(--accent-color)',
    'var(--orange)': 'var(--status-warning)',
    'var(--text-sec)': 'var(--text-secondary)',
    'var(--text-pri)': 'var(--text-primary)'
}
for old, new in replacements.items():
    text = text.replace(old, new)

# Inject CSS block if not there
if '.grid-2 {' not in text:
    text = text.replace('    /* ═══════════════════════════════════════\n       DETAIL SECTIONS\n    ═══════════════════════════════════════ */', css_to_add + '\n    /* ═══════════════════════════════════════\n       DETAIL SECTIONS\n    ═══════════════════════════════════════ */')

with open('templates/landing.html', 'w', encoding='utf8') as f:
    f.write(text)

print('Done fixing colors and injecting css.')

