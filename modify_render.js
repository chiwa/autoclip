const fs = require('fs');
let code = fs.readFileSync('temp_render.js', 'utf8');

// We want to add Topic/Description for quick-reel
const injection = `
    info.append(jobBadge, publishBadge, title, meta);
    
    if (p.project_type === 'quick-reel' && p.latestJob?.metadata?.videoMetadata) {
        const vm = p.latestJob.metadata.videoMetadata;
        
        const qMetaDiv = document.createElement('div');
        qMetaDiv.style.marginTop = '16px';
        qMetaDiv.style.padding = '12px';
        qMetaDiv.style.background = 'rgba(0,0,0,0.3)';
        qMetaDiv.style.borderRadius = '8px';
        qMetaDiv.style.border = '1px solid var(--line)';
        
        const qTitleRow = document.createElement('div');
        qTitleRow.style.display = 'flex';
        qTitleRow.style.justifyContent = 'space-between';
        qTitleRow.style.alignItems = 'flex-start';
        qTitleRow.style.marginBottom = '8px';
        const qTitle = document.createElement('h4');
        qTitle.textContent = vm.title || '-';
        qTitle.style.margin = '0';
        qTitle.style.fontSize = '14px';
        qTitle.style.color = 'var(--cyan)';
        
        const qCopyTitle = document.createElement('button');
        qCopyTitle.className = 'button small secondary';
        qCopyTitle.textContent = 'Copy Title';
        qCopyTitle.onclick = () => { navigator.clipboard.writeText(vm.title || ''); qCopyTitle.textContent='Copied!'; setTimeout(()=>qCopyTitle.textContent='Copy Title', 2000); };
        qTitleRow.append(qTitle, qCopyTitle);
        
        const qDescRow = document.createElement('div');
        qDescRow.style.display = 'flex';
        qDescRow.style.justifyContent = 'space-between';
        qDescRow.style.alignItems = 'flex-end';
        qDescRow.style.marginTop = '8px';
        const qDescPre = document.createElement('pre');
        qDescPre.style.margin = '0';
        qDescPre.style.whiteSpace = 'pre-wrap';
        qDescPre.style.fontSize = '13px';
        qDescPre.style.color = 'var(--soft)';
        qDescPre.textContent = vm.description || '-';
        
        const qCopyDesc = document.createElement('button');
        qCopyDesc.className = 'button small secondary';
        qCopyDesc.textContent = 'Copy Caption';
        qCopyDesc.onclick = () => { navigator.clipboard.writeText(vm.description || ''); qCopyDesc.textContent='Copied!'; setTimeout(()=>qCopyDesc.textContent='Copy Caption', 2000); };
        qDescRow.append(qDescPre, qCopyDesc);
        
        qMetaDiv.append(qTitleRow, qDescRow);
        info.append(qMetaDiv);
    }
`;

code = code.replace('info.append(jobBadge, publishBadge, title, meta);', injection);

fs.writeFileSync('temp_render.js', code);

// Minify roughly by removing line breaks and extra spaces
const minified = code.replace(/\n/g, '').replace(/\s{2,}/g, ' ');
console.log(minified);
