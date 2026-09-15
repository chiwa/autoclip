const fs = require('fs');
const html = fs.readFileSync('app/web/static/history.html', 'utf8');
const lines = html.split('\n');
const line = lines[31]; // 0-indexed for line 32

const prettier = require('child_process').execSync;
fs.writeFileSync('temp_render.js', line);
prettier('npx prettier --write temp_render.js');
console.log(fs.readFileSync('temp_render.js', 'utf8'));
