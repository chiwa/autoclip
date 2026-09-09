const jobId = location.pathname.match(/^\/jobs\/([^/]+)\/preview$/)?.[1];
const formatBytes = value => value < 1024 ? `${value} B` : `${(value / 1024).toFixed(1)} KB`;
(async () => {
  try {
    const response = await fetch(`/api/jobs/${jobId}`); const job = await response.json();
    if (!response.ok) throw job.detail;
    if (job.status !== 'COMPLETED') { location.replace(`/jobs/${jobId}`); return; }
    const metadata = job.metadata || {}, vm = metadata.videoMetadata || {title:'-', description:'-', hashtags:''};
    const video = document.querySelector('#video');
    video.src = `/api/jobs/${jobId}/video`;
    video.onloadedmetadata = () => {
      if (video.videoWidth > video.videoHeight) {
        video.style.aspectRatio = '16/9';
        video.style.width = 'min(860px, 100%)';
      }
    };
    document.querySelector('#download').href = `/api/jobs/${jobId}/video`;
    document.querySelector('#projectTitle').textContent = metadata.projectTitle || '-';
    const summary = document.querySelector('#metadata'); summary.textContent = `Duration: ${Number(metadata.durationSeconds || 0).toFixed(1)}s · Resolution: ${metadata.resolution || '-'} · Scenes: ${metadata.sceneCount || '-'}`; summary.style.display = 'block'; summary.style.textAlign = 'center'; summary.style.padding = '12px 16px'; summary.style.margin = '14px auto 20px';
    const card = document.createElement('section'); card.className = 'tool-card video-metadata';
    const heading = document.createElement('h2'); heading.textContent = 'Video Metadata';
    const titleLabel = document.createElement('label'); titleLabel.textContent = 'Title';
    const title = document.createElement('input'); title.type = 'text'; title.maxLength = 100; title.value = vm.title || '-'; title.style.display = 'block'; title.style.width = '100%';
    const copyTitle = document.createElement('button'); copyTitle.type = 'button'; copyTitle.className = 'button secondary'; copyTitle.textContent = 'Copy Title'; copyTitle.onclick = async () => { await navigator.clipboard.writeText(title.value); status.textContent = 'คัดลอก Title แล้ว'; }; titleLabel.append(title, copyTitle);
    const descLabel = document.createElement('label'); descLabel.textContent = 'Description';
    const description = document.createElement('textarea'); description.rows = 8; description.value = vm.description || '-'; description.style.display = 'block';
    const copyDescription = document.createElement('button'); copyDescription.type = 'button'; copyDescription.className = 'button secondary'; copyDescription.textContent = 'Copy Description'; copyDescription.onclick = async () => { await navigator.clipboard.writeText(description.value); status.textContent = 'คัดลอก Description แล้ว'; }; descLabel.append(description, copyDescription);
    const hashtagsLabel = document.createElement('label'); hashtagsLabel.textContent = 'Hashtags';
    const hashtags = document.createElement('textarea'); hashtags.rows = 3; hashtags.style.minHeight = '90px'; hashtags.value = vm.hashtags || ''; hashtags.style.display = 'block';
    const copyHashtags = document.createElement('button'); copyHashtags.type = 'button'; copyHashtags.className = 'button secondary'; copyHashtags.textContent = 'Copy Hashtags'; copyHashtags.onclick = async () => { await navigator.clipboard.writeText(hashtags.value); status.textContent = 'คัดลอก Hashtags แล้ว'; }; hashtagsLabel.append(hashtags, copyHashtags);
    const save = document.createElement('button'); save.className = 'button secondary'; save.textContent = 'Save Metadata';
    const status = document.createElement('p'); status.className = 'muted';
    card.append(heading, titleLabel, descLabel, hashtagsLabel, save, status); document.querySelector('#metadata').after(card);
    save.onclick = async () => { save.disabled = true; const r = await fetch(`/api/jobs/${jobId}/video-metadata`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({title:title.value, description:description.value, hashtags:hashtags.value})}); status.textContent = r.ok ? 'บันทึก Metadata แล้ว' : 'บันทึกไม่สำเร็จ'; save.disabled = false; };
    document.querySelector('#previewLoading').hidden = true; document.querySelector('#previewContent').hidden = false;
  } catch (e) { const box = document.querySelector('#previewError'); box.textContent = `${e?.code || 'INTERNAL_ERROR'}: ${e?.message || 'Preview unavailable'}`; box.hidden = false; }
})();
