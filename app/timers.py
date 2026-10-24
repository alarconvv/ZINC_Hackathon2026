"""Client-only optional timers: no Streamlit callbacks or completion records."""
import streamlit.components.v1 as components


def countdown(seconds, label):
    # Only fixed labels and bounded integer durations are passed by the UI.
    import html
    seconds = max(1, min(300, int(seconds)))
    components.html("""<!doctype html><html lang="en"><meta charset="utf-8"><style>
body{font:16px system-ui;color:#12365b;background:#f4faff;margin:0;padding:16px;border-radius:20px}
.row{display:flex;align-items:center;gap:16px;flex-wrap:wrap}.ring{border:4px solid #126bc5;border-radius:50%;width:72px;height:72px;display:grid;place-items:center;font-size:24px;font-variant-numeric:tabular-nums}
button{min-height:48px;padding:8px 18px;border:1px solid #126bc5;background:white;border-radius:24px;color:#12365b;font:inherit;cursor:pointer}button:focus-visible{outline:3px solid #12365b;outline-offset:2px}p{font-size:13px}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style><strong>""" + html.escape(label) + """</strong><div class="row"><output class="ring" aria-label="Time remaining"></output><button id="toggle">Start</button><button id="reset">Reset</button></div><p role="status" id="status">Optional timer. Nothing is recorded.</p><script>
const total=""" + str(seconds) + """;
let remaining=total,running=false,last=0;
const clock=document.querySelector('output'),toggle=document.querySelector('#toggle'),status=document.querySelector('#status');
function render(){clock.textContent=Math.floor(remaining/60)+':'+String(remaining%60).padStart(2,'0');toggle.textContent=running?'Pause':remaining===0?'Start again':'Start'}
toggle.onclick=()=>{if(remaining===0)remaining=total;running=!running;last=Date.now();render()};
document.querySelector('#reset').onclick=()=>{remaining=total;running=false;status.textContent='Optional timer. Nothing is recorded.';render()};
setInterval(()=>{if(running){const elapsed=Math.floor((Date.now()-last)/1000);if(elapsed){remaining=Math.max(0,remaining-elapsed);last+=elapsed*1000;if(remaining===0){running=false;status.textContent='Timer finished. Completion is still your choice.'}render()}}},200);render();
</script></html>""", height=190)
