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
    const channelStatus = document.querySelector('#channelStatus');
    const channelResponse = await fetch(`/api/jobs/${jobId}/channel`);
    if (channelResponse.ok) {
      const currentChannel = await channelResponse.json();
      const channelSelect = await AutoClipChannels.mount('#previewChannelPicker', {id: 'contentChannel', selected: currentChannel.channelId});
      const saveChannel = document.querySelector('#saveChannel');
      channelStatus.textContent = `ปัจจุบัน: ${currentChannel.channelName}`;
      saveChannel.onclick = async () => {
        saveChannel.disabled = true;
        channelStatus.textContent = 'กำลังบันทึก Channel…';
        const response = await fetch(`/api/jobs/${jobId}/channel`, {method:'PATCH', headers:{'Content-Type':'application/json'}, body:JSON.stringify({channelId:channelSelect.value})});
        const result = await response.json().catch(() => ({}));
        channelStatus.textContent = response.ok ? `บันทึกแล้ว: ${result.channelName}` : (result.detail?.message || 'บันทึก Channel ไม่สำเร็จ');
        saveChannel.disabled = false;
      };
    } else {
      document.querySelector('#channelCard').hidden = true;
    }
    const publicationCard = document.querySelector('#publicationCard');
    const publicationStatus = document.querySelector('#publicationStatus');
    const publicationToggle = document.querySelector('#publicationToggle');
    let published = false;
    const renderPublication = () => {
      publicationStatus.textContent = published ? 'เผยแพร่แล้ว' : 'ยังไม่เผยแพร่';
      publicationStatus.className = `publish-state${published ? ' published' : ''}`;
      publicationToggle.textContent = published ? 'เปลี่ยนเป็นยังไม่เผยแพร่' : 'มาร์กว่า Publish แล้ว';
      publicationToggle.disabled = false;
    };
    const publicationResponse = await fetch(`/api/jobs/${jobId}/publication`);
    if (publicationResponse.ok) {
      const publication = await publicationResponse.json();
      published = Boolean(publication.published);
      renderPublication();
      publicationToggle.onclick = async () => {
        publicationToggle.disabled = true;
        publicationStatus.textContent = 'กำลังบันทึกสถานะ…';
        const updateResponse = await fetch(`/api/jobs/${jobId}/publication`, {
          method: 'PATCH',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({published: !published}),
        });
        const update = await updateResponse.json().catch(() => ({}));
        if (!updateResponse.ok) {
          publicationStatus.textContent = update.detail?.message || 'บันทึกสถานะไม่สำเร็จ';
          publicationToggle.disabled = false;
          return;
        }
        published = Boolean(update.published);
        renderPublication();
      };
    } else {
      publicationCard.hidden = true;
    }
    const englishAudio = metadata.englishAudio || {};
    if (englishAudio.requested) {
      const englishCard = document.createElement('section'); englishCard.className = 'tool-card';
      const englishHeading = document.createElement('h2'); englishHeading.textContent = 'English Audio Track';
      const englishStatus = document.createElement('p'); englishStatus.className = 'muted';
      const englishActions = document.createElement('div'); englishActions.className = 'actions';
      englishCard.append(englishHeading, englishStatus, englishActions);
      summary.after(englishCard);

      const renderEnglishState = state => {
        englishActions.replaceChildren();
        if (state.available) {
          englishStatus.textContent = `พร้อมแล้ว · ${Number(state.durationSeconds || metadata.durationSeconds || 0).toFixed(1)} วินาที`;
          const player = document.createElement('audio'); player.controls = true; player.preload = 'metadata'; player.src = `/api/jobs/${jobId}/english-audio`;
          const downloadEnglish = document.createElement('a'); downloadEnglish.className = 'button secondary'; downloadEnglish.href = `/api/jobs/${jobId}/english-audio`; downloadEnglish.download = ''; downloadEnglish.textContent = 'ดาวน์โหลด English WAV';
          englishActions.append(player, downloadEnglish);
        } else if (state.status === 'retrying') {
          englishStatus.textContent = 'กำลัง Retry เฉพาะส่วน English audio ที่ไม่สำเร็จ…';
        } else {
          const failedChunks = state.failedChunkIndexes?.length ? ` · failed chunk: ${state.failedChunkIndexes.map(i => i + 1).join(', ')}` : '';
          englishStatus.textContent = `${state.error?.message || 'English audio ยังไม่พร้อม'}${failedChunks}`;
          const retryEnglish = document.createElement('button'); retryEnglish.type = 'button'; retryEnglish.className = 'button secondary'; retryEnglish.textContent = 'Retry English Audio';
          retryEnglish.onclick = async () => {
            retryEnglish.disabled = true;
            const retryResponse = await fetch(`/api/jobs/${jobId}/english-audio/retry`, {method: 'POST'});
            const retryData = await retryResponse.json().catch(() => ({}));
            if (!retryResponse.ok) {
              englishStatus.textContent = `${retryData.detail?.code || 'RETRY_FAILED'}: ${retryData.detail?.message || 'เริ่ม Retry ไม่สำเร็จ'}`;
              retryEnglish.disabled = false;
              return;
            }
            renderEnglishState({status: 'retrying'});
            pollEnglishAudio();
          };
          englishActions.append(retryEnglish);
        }
      };
      let englishPollTimer = null;
      const pollEnglishAudio = () => {
        if (englishPollTimer) return;
        englishPollTimer = setInterval(async () => {
          const currentResponse = await fetch(`/api/jobs/${jobId}`);
          if (!currentResponse.ok) return;
          const current = await currentResponse.json();
          const state = current.metadata?.englishAudio || {};
          renderEnglishState(state);
          if (state.status !== 'retrying') {
            clearInterval(englishPollTimer);
            englishPollTimer = null;
          }
        }, 3000);
      };
      renderEnglishState(englishAudio);
      if (englishAudio.status === 'retrying') pollEnglishAudio();
    }
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
