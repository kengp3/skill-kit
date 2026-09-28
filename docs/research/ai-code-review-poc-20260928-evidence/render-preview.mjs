import fs from 'node:fs';
import path from 'node:path';
import { marked } from '/Users/kengp3/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked/lib/marked.esm.js';
const root = '/Users/kengp3/Workspaces/mine/simple-skills';
for (const name of process.argv.slice(2)) {
  const source = path.join(root, 'docs/research', name);
  let html = marked.parse(fs.readFileSync(source, 'utf8'));
  html = html.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, '<pre class="mermaid">$1</pre>');
  html = html.replace(/<(h[1-6])>([\s\S]*?)<\/h[1-6]>/g, (_, tag, body) => `<${tag} id="${body.replace(/<[^>]*>/g, '').toLowerCase().replace(/[^\p{L}\p{N}_\-\s]/gu, '').replace(/\s/g, '-')}">${body}</${tag}>`);
  html = html.replace(/href="([^"]+)"/g, (original, href) => {
    if (href.startsWith('#') || /^[a-z]+:/i.test(href)) return original;
    const target = href.startsWith('/') ? href : path.resolve(path.dirname(source), href);
    return target.startsWith(root + '/') ? `href="${target.slice(root.length).replace(/:\d+(?=#|$)/, '')}"` : original;
  });
  const output = path.join(root, 'docs/research/ai-code-review-poc-20260928-evidence', name + '.html');
  fs.writeFileSync(output, `<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${name}</title><style>
body{font:16px/1.65 system-ui,sans-serif;color:#222;background:#fff;margin:0}main{max-width:1080px;margin:auto;padding:28px 36px}h1{font-size:28px}h2{font-size:22px;margin-top:40px;border-bottom:1px solid #ddd}h3{font-size:19px}a{color:#125aa6}table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0}th,td{border:1px solid #ddd;padding:9px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#f3f5f7}pre{font:14px/1.5 ui-monospace,monospace;overflow:auto;background:#f6f8fa;padding:16px}code{font-family:ui-monospace,monospace}li{margin:5px 0}svg{max-width:100%;height:auto}.mermaid{background:#fff;text-align:center}@media(max-width:800px){main{padding:16px}table{font-size:13px}}
</style><main>${html}</main><script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';mermaid.initialize({startOnLoad:false,theme:'neutral',securityLevel:'strict'});try{await mermaid.run();document.documentElement.dataset.mermaid='ready'}catch(e){document.documentElement.dataset.mermaid='error';console.error(e)}</script></html>`);
  console.log(output);
}
