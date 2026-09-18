const jobId = location.pathname.match(/^\/jobs\/([^/]+)\/preview$/)?.[1];

try {
  if (sessionStorage.getItem('autoclip_notify_success')) {
    sessionStorage.removeItem('autoclip_notify_success');
    setTimeout(() => {
      window.AutoClipSound?.playSuccess();
    }, 200);
  }
} catch (_) {}

const formatBytes = value => {
  if (!value || value <= 0) return '-';
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
};

const setText = (sel, val) => {
  const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
  if (el) el.textContent = val ?? '';
  return el;
};

const setVal = (sel, val) => {
  const el = typeof sel === 'string' ? document.querySelector(sel) : sel;
  if (el) el.value = val ?? '';
  return el;
};

function setupCopyButton(btn, getValue) {
  if (!btn) return;
  btn.onclick = async () => {
    const text = getValue();
    try {
      await navigator.clipboard.writeText(text);
      const prev = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = prev;
        btn.classList.remove('copied');
      }, 2000);
    } catch (e) {
      alert(`ไม่สามารถคัดลอกได้: ${e.message}`);
    }
  };
}

async function initPreview() {
  if (!jobId) return;
  try {
    const response = await fetch(`/api/jobs/${jobId}`);
    const job = await response.json();
    if (!response.ok) throw (job.detail || job);
    if (job.status !== 'COMPLETED') {
      location.replace(`/jobs/${jobId}`);
      return;
    }

    const metadata = job.metadata || {};
    const vm = metadata.videoMetadata || {title: metadata.projectTitle || '-', description: '-', hashtags: ''};

    const video = document.querySelector('#video');
    if (video) {
      video.src = `/api/jobs/${jobId}/video`;
      video.onloadedmetadata = () => {
        if (video.videoWidth > video.videoHeight) {
          video.style.aspectRatio = '16/9';
        } else {
          video.style.aspectRatio = '9/16';
        }
      };
    }

    const downloadLinks = [document.querySelector('#download'), document.querySelector('#topDownloadBtn')];
    downloadLinks.forEach(a => { if (a) a.href = `/api/jobs/${jobId}/video`; });

    const titleText = metadata.projectTitle || vm.title || '-';
    setText('#projectTitle', titleText);
    document.title = `AutoClip · ${titleText}`;

    // Compatibility for legacy scripts
    setText('#metadata', `Duration: ${Number(metadata.durationSeconds || 0).toFixed(1)}s · Resolution: ${metadata.resolution || '-'} · Scenes: ${metadata.sceneCount || '-'}`);

    const isQuickReel = metadata.projectType === 'quick-reel' || Boolean(metadata.quickReel);
    const typeBadge = document.querySelector('#projectTypeBadge');
    if (typeBadge) {
      if (isQuickReel) {
        typeBadge.textContent = 'Quick Reel';
        typeBadge.className = 'studio-badge quick-reel';
        const qrHist = document.querySelector('#quickReelHistoryLink');
        const qrSep = document.querySelector('#quickReelHistorySep');
        if (qrHist) qrHist.hidden = false;
        if (qrSep) qrSep.hidden = false;
      } else {
        typeBadge.textContent = 'Standard Reel';
        typeBadge.className = 'studio-badge';
      }
    }

    // Technical specs
    setText('#specDuration', `${Number(metadata.durationSeconds || 0).toFixed(1)}s`);
    setText('#specResolution', metadata.resolution || '-');
    const count = metadata.sceneCount || 1;
    setText('#specScenes', `${count} Scene${count > 1 ? 's' : ''}`);
    setText('#specSize', formatBytes(metadata.fileSizeBytes));

    function updateVideoOrientation(resStr) {
      const playerCard = document.querySelector('.studio-player-card');
      if (!playerCard) return;
      let isLandscape = false;
      if (resStr && typeof resStr === 'string' && resStr.includes('x')) {
        const [w, h] = resStr.split('x').map(Number);
        isLandscape = w > h;
      } else if (video && video.videoWidth && video.videoHeight) {
        isLandscape = video.videoWidth > video.videoHeight;
      }
      playerCard.classList.toggle('is-landscape', isLandscape);
      playerCard.classList.toggle('is-portrait', !isLandscape);
      if (isLandscape) {
        playerCard.style.maxWidth = '100%';
      } else {
        playerCard.style.maxWidth = '440px';
      }
    }
    if (metadata.resolution) {
      updateVideoOrientation(metadata.resolution);
    }
    if (video) {
      video.addEventListener('loadedmetadata', () => {
        updateVideoOrientation(`${video.videoWidth}x${video.videoHeight}`);
      });
    }

    const MOTION_LABELS = {
      'gentle_float': '🌌 ลอยนุ่มนวลแบบอวกาศ (Gentle Float)',
      'cosmic_float': '🌌 ลอยนุ่มนวลแบบอวกาศ (Gentle Float)',
      'hook_punch_in': '💥 ซูมกระแทกเข้า 3 วิแรก แล้วลอยต่อ (Hook Punch-in)',
      'breathing_pulse': '🫁 หายใจเป็นจังหวะ ขยาย-หดนุ่มนวล (Breathing Pulse)',
      'cinematic_push_in': '🎬 ซูมเข้าอย่างสง่างาม (Cinematic Push-in)',
      'cinematic_pull_out': '🔭 ซูมออกเปิดเผยภาพกว้าง (Cinematic Pull-out)',
      'slow_zoom_in': '🔍 ซูมเข้าช้าๆ นุ่มนวล (Slow Zoom In)',
      'slow_zoom': '🔍 ซูมเข้าช้าๆ นุ่มนวล (Slow Zoom In)',
      'slow_zoom_out': '🔎 ซูมออกช้าๆ เห็นภาพกว้าง (Slow Zoom Out)',
      'pan_left_to_right': '➡️ เลื่อนจากซ้ายไปขวา (Pan Left to Right)',
      'pan_right_to_left': '⬅️ เลื่อนจากขวาไปซ้าย (Pan Right to Left)',
      'pan_up': '⬆️ เลื่อนขึ้นช้าๆ จากล่างสู่บน (Pan Up)',
      'pan_down': '⬇️ เลื่อนลงช้าๆ จากบนสู่ล่าง (Pan Down)',
      'none': '⏹️ ภาพนิ่งคงที่ (Static Frame)',
      'static': '⏹️ ภาพนิ่งคงที่ (Static Frame)',
    };
    const getMotionLabel = key => MOTION_LABELS[key] || (key ? `🎬 ${key}` : 'ภาพนิ่งคงที่');

    const curMotionKey = metadata.quickReel?.motion || (metadata.sceneCount === 1 ? 'gentle_float' : 'slideshow');
    setText('#specMotion', getMotionLabel(curMotionKey));

    // Fast Re-Motion Tool (Directly under video)
    const isSingleScene = (Number(metadata.sceneCount) === 1) || (Number(metadata.quickReel?.imageCount) === 1);
    const motionToolCard = document.querySelector('#motionToolCard');
    const motionPresetSelect = document.querySelector('#motionPresetSelect');
    const currentMotionPill = document.querySelector('#currentMotionPill');
    const btnApplyMotion = document.querySelector('#btnApplyMotion');
    const motionStatus = document.querySelector('#motionStatus');

    const remotionModal = document.querySelector('#remotionModal');
    const remotionSpinnerWrap = document.querySelector('#remotionSpinnerWrap');
    const remotionModalTitle = document.querySelector('#remotionModalTitle');
    const remotionModalDesc = document.querySelector('#remotionModalDesc');
    const remotionModalBadge = document.querySelector('#remotionModalBadge');
    const remotionModalActions = document.querySelector('#remotionModalActions');
    const btnRemotionModalClose = document.querySelector('#btnRemotionModalClose');

    if (btnRemotionModalClose) {
      btnRemotionModalClose.onclick = () => {
        if (remotionModal) remotionModal.hidden = true;
      };
    }

    if (isQuickReel && isSingleScene && motionToolCard) {
      motionToolCard.hidden = false;
      const initialMotion = metadata.quickReel?.motion || 'gentle_float';
      setText(currentMotionPill, initialMotion);
      setText('#currentMotionName', getMotionLabel(initialMotion));
      if (motionPresetSelect) {
        if (motionPresetSelect.querySelector(`option[value="${initialMotion}"]`)) {
          motionPresetSelect.value = initialMotion;
        }
      }

      if (btnApplyMotion) {
        btnApplyMotion.onclick = async () => {
          const selectedMotion = motionPresetSelect ? motionPresetSelect.value : initialMotion;
          btnApplyMotion.disabled = true;

          const clipDur = Number(metadata.durationSeconds || (video && video.duration) || 0);
          const estMin = Math.max(8, Math.round(clipDur * 0.5));
          const estMax = Math.max(15, Math.round(clipDur * 0.9));

          // Setup timer and stages
          let elapsedSec = 0;
          const remotionModalTimer = document.querySelector('#remotionModalTimer');
          const remotionModalStage = document.querySelector('#remotionModalStage');
          if (remotionModalTimer) remotionModalTimer.textContent = '⏱️ กำลังเรนเดอร์: 0 วินาที';
          if (remotionModalStage) remotionModalStage.textContent = '🚀 เริ่มต้นประมวลผลเฟรมวิดีโอ...';

          const timerInterval = setInterval(() => {
            elapsedSec++;
            if (remotionModalTimer) {
              remotionModalTimer.textContent = `⏱️ กำลังเรนเดอร์: ${elapsedSec} วินาที`;
            }
            if (remotionModalStage) {
              if (elapsedSec >= 4 && elapsedSec < 12) {
                remotionModalStage.textContent = '🎬 กำลังคำนวณการเคลื่อนไหวของภาพ (Motion Camera)...';
              } else if (elapsedSec >= 12 && elapsedSec < 28) {
                remotionModalStage.textContent = '📐 กำลังเรนเดอร์เฟรมความละเอียดสูง 1080x1920 30FPS...';
              } else if (elapsedSec >= 28 && elapsedSec < 50) {
                remotionModalStage.textContent = '🌊 กำลังประมวลผลการซูม/แพน และเชื่อมต่อซับไตเติล...';
              } else if (elapsedSec >= 50) {
                remotionModalStage.textContent = '🎵 กำลังประกอบแทร็กเสียงและบันทึกไฟล์ MP4...';
              }
            }
          }, 1000);

          // Show fullscreen blocking modal
          if (remotionModal) {
            if (remotionSpinnerWrap) remotionSpinnerWrap.innerHTML = '<div class="remotion-spinner"></div>';
            setText(remotionModalTitle, '⚡ กำลังเรนเดอร์ Motion ใหม่...');
            if (clipDur > 0) {
              setText(remotionModalDesc, `กำลังเรนเดอร์แบบ ${getMotionLabel(selectedMotion)} สำหรับคลิปยาว ${Math.round(clipDur)} วินาที (คาดว่าจะใช้เวลาประมาณ ${estMin}–${estMax} วินาที)`);
            } else {
              setText(remotionModalDesc, `ระบบกำลังเรนเดอร์แบบ ${getMotionLabel(selectedMotion)} ด้วย FFmpeg (ความเร็วขึ้นอยู่กับความยาวคลิป)`);
            }
            if (remotionModalBadge) {
              remotionModalBadge.className = 'remotion-modal-badge';
              remotionModalBadge.textContent = '✨ ไม่เสียโควต้า AI · ใช้เสียงบรรยายเดิม';
            }
            if (remotionModalActions) remotionModalActions.hidden = true;
            remotionModal.hidden = false;
          }

          if (motionStatus) {
            motionStatus.className = 'motion-feedback';
            motionStatus.textContent = '⚡ กำลังเรนเดอร์ Motion ใหม่... (กำลังประมวลผล ไม่เสียโควต้า AI)';
          }

          try {
            const remotionRes = await fetch(`/api/quick-reel/${jobId}/remotion`, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({motion: selectedMotion}),
            });
            const remotionData = await remotionRes.json();
            if (!remotionRes.ok) throw (remotionData.detail || remotionData);

            clearInterval(timerInterval);

            // Modal success animation
            window.AutoClipSound?.playSuccess();
            if (remotionModal) {
              if (remotionSpinnerWrap) remotionSpinnerWrap.innerHTML = '<div class="remotion-success-icon">✓</div>';
              setText(remotionModalTitle, 'เปลี่ยน Motion สำเร็จแล้ว!');
              setText(remotionModalDesc, `วิดีโอถูกอัปเดตเป็น ${getMotionLabel(remotionData.motion)} เรียบร้อยแล้ว`);
              if (remotionModalTimer) remotionModalTimer.textContent = `⚡ เสร็จสิ้นในเวลา ${elapsedSec} วินาที`;
              if (remotionModalStage) remotionModalStage.textContent = '✅ เรนเดอร์วิดีโอเรียบร้อยสมบูรณ์!';
              if (remotionModalBadge) remotionModalBadge.textContent = '🎉 พร้อมรับชมวิดีโอใหม่';
            }

            if (motionStatus) {
              motionStatus.className = 'motion-feedback success';
              motionStatus.textContent = `✓ ${remotionData.message || 'เปลี่ยน Motion สำเร็จแล้ว!'}`;
            }
            setText(currentMotionPill, remotionData.motion);
            setText('#currentMotionName', getMotionLabel(remotionData.motion));
            setText('#specMotion', getMotionLabel(remotionData.motion));
            if (remotionData.durationSeconds) {
              setText('#specDuration', `${Number(remotionData.durationSeconds).toFixed(1)}s`);
            }
            if (remotionData.resolution) {
              setText('#specResolution', remotionData.resolution);
              updateVideoOrientation(remotionData.resolution);
            }

            // Reload video with cache buster
            if (video) {
              const newSrc = `/api/jobs/${jobId}/video?t=${Date.now()}`;
              video.src = newSrc;
              downloadLinks.forEach(a => { if (a) a.href = newSrc; });
              video.load();
              video.play().catch(() => {});
            }

            // Automatically close modal after brief celebration
            setTimeout(() => {
              if (remotionModal) remotionModal.hidden = true;
            }, 1000);

          } catch (err) {
            clearInterval(timerInterval);
            window.AutoClipSound?.playError();
            if (remotionModal) {
              if (remotionSpinnerWrap) remotionSpinnerWrap.innerHTML = '<div style="font-size:48px; line-height:1;">❌</div>';
              setText(remotionModalTitle, 'เกิดข้อผิดพลาดในการเปลี่ยน Motion');
              setText(remotionModalDesc, err?.message || 'ไม่สามารถเรนเดอร์ Motion ใหม่ได้ โปรดลองอีกครั้ง');
              if (remotionModalBadge) {
                remotionModalBadge.className = 'remotion-modal-badge error';
                remotionModalBadge.textContent = 'การประมวลผลไม่สำเร็จ';
              }
              if (remotionModalActions) remotionModalActions.hidden = false;
            }

            if (motionStatus) {
              motionStatus.className = 'motion-feedback error';
              motionStatus.textContent = `❌ ${err?.message || 'เกิดข้อผิดพลาดในการเปลี่ยน Motion'}`;
            }
          } finally {
            clearInterval(timerInterval);
            btnApplyMotion.disabled = false;
          }
        };
      }
    } else if (motionToolCard) {
      motionToolCard.hidden = true;
    }


    // Metadata form inputs & copy buttons
    setVal('#metaTitle', vm.title || titleText);
    setVal('#metaDescription', vm.description || '-');
    setVal('#metaHashtags', vm.hashtags || '');

    setupCopyButton(document.querySelector('#btnCopyTitle'), () => document.querySelector('#metaTitle')?.value || '');
    setupCopyButton(document.querySelector('#btnCopyDesc'), () => document.querySelector('#metaDescription')?.value || '');
    setupCopyButton(document.querySelector('#btnCopyHashtags'), () => document.querySelector('#metaHashtags')?.value || '');

    const btnSaveMeta = document.querySelector('#btnSaveMeta');
    const saveMetaStatus = document.querySelector('#saveMetaStatus');
    if (btnSaveMeta) {
      btnSaveMeta.onclick = async () => {
        btnSaveMeta.disabled = true;
        setText(saveMetaStatus, 'กำลังบันทึก…');
        try {
          const r = await fetch(`/api/jobs/${jobId}/video-metadata`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
              title: document.querySelector('#metaTitle')?.value || '',
              description: document.querySelector('#metaDescription')?.value || '',
              hashtags: document.querySelector('#metaHashtags')?.value || '',
            }),
          });
          if (!r.ok) throw new Error('บันทึกไม่สำเร็จ');
          setText(saveMetaStatus, '✓ บันทึก Metadata แล้ว');
          setTimeout(() => { setText(saveMetaStatus, ''); }, 3000);
        } catch (err) {
          setText(saveMetaStatus, `❌ ${err.message}`);
        } finally {
          btnSaveMeta.disabled = false;
        }
      };
    }

    // Channel Picker
    const channelStatus = document.querySelector('#channelStatus');
    const channelResponse = await fetch(`/api/jobs/${jobId}/channel`);
    if (channelResponse.ok) {
      const currentChannel = await channelResponse.json();
      const channelSelect = await AutoClipChannels.mount('#previewChannelPicker', {id: 'contentChannel', selected: currentChannel.channelId});
      const saveChannel = document.querySelector('#saveChannel');
      setText(channelStatus, `ปัจจุบัน: ${currentChannel.channelName}`);
      if (saveChannel && channelSelect) {
        saveChannel.onclick = async () => {
          saveChannel.disabled = true;
          setText(channelStatus, 'กำลังบันทึก Channel…');
          const r = await fetch(`/api/jobs/${jobId}/channel`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({channelId: channelSelect.value}),
          });
          const result = await r.json().catch(() => ({}));
          setText(channelStatus, r.ok ? `✓ บันทึกแล้ว: ${result.channelName}` : (result.detail?.message || 'บันทึก Channel ไม่สำเร็จ'));
          saveChannel.disabled = false;
        };
      }
    } else {
      const chBox = document.querySelector('#channelBox');
      if (chBox) chBox.hidden = true;
    }

    // Publication Status
    const publicationStatus = document.querySelector('#publicationStatus');
    const publicationToggle = document.querySelector('#publicationToggle');
    let published = false;
    const renderPublication = () => {
      if (!publicationStatus || !publicationToggle) return;
      publicationStatus.textContent = published ? 'เผยแพร่แล้ว ✓' : 'ยังไม่เผยแพร่';
      publicationStatus.className = `publish-badge-large${published ? ' published' : ''}`;
      publicationToggle.textContent = published ? 'เปลี่ยนเป็นยังไม่เผยแพร่' : 'มาร์กว่า Publish แล้ว';
      publicationToggle.disabled = false;
    };

    const publicationResponse = await fetch(`/api/jobs/${jobId}/publication`);
    if (publicationResponse.ok) {
      const publication = await publicationResponse.json();
      published = Boolean(publication.published);
      renderPublication();
      if (publicationToggle) {
        publicationToggle.onclick = async () => {
          publicationToggle.disabled = true;
          setText(publicationStatus, 'กำลังบันทึกสถานะ…');
          const updateResponse = await fetch(`/api/jobs/${jobId}/publication`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({published: !published}),
          });
          const update = await updateResponse.json().catch(() => ({}));
          if (!updateResponse.ok) {
            setText(publicationStatus, update.detail?.message || 'บันทึกสถานะไม่สำเร็จ');
            publicationToggle.disabled = false;
            return;
          }
          published = Boolean(update.published);
          renderPublication();
        };
      }
    } else {
      const pbBox = document.querySelector('#publicationBox');
      if (pbBox) pbBox.hidden = true;
    }

    // English Audio Track (if present)
    const englishAudio = metadata.englishAudio || {};
    if (englishAudio.requested) {
      const container = document.querySelector('#englishTrackContainer');
      if (container) {
        const englishCard = document.createElement('section');
        englishCard.className = 'studio-panel';
        const englishHead = document.createElement('div');
        englishHead.className = 'studio-panel-head';
        englishHead.innerHTML = '<div><span class="eyebrow">SECONDARY AUDIO</span><h2>🎧 English Audio Track</h2></div>';
        const englishStatus = document.createElement('p');
        englishStatus.className = 'muted';
        englishStatus.style.margin = '10px 0';
        const englishActions = document.createElement('div');
        englishActions.className = 'actions';
        englishCard.append(englishHead, englishStatus, englishActions);
        container.append(englishCard);

        const renderEnglishState = state => {
          englishActions.replaceChildren();
          if (state.available) {
            englishStatus.textContent = `พร้อมแล้ว · ${Number(state.durationSeconds || metadata.durationSeconds || 0).toFixed(1)} วินาที`;
            const player = document.createElement('audio');
            player.controls = true;
            player.preload = 'metadata';
            player.src = `/api/jobs/${jobId}/english-audio`;
            const downloadEnglish = document.createElement('a');
            downloadEnglish.className = 'button secondary';
            downloadEnglish.href = `/api/jobs/${jobId}/english-audio`;
            downloadEnglish.download = '';
            downloadEnglish.textContent = 'ดาวน์โหลด English WAV';
            englishActions.append(player, downloadEnglish);
          } else if (state.status === 'retrying') {
            englishStatus.textContent = 'กำลัง Retry เฉพาะส่วน English audio ที่ไม่สำเร็จ…';
          } else {
            const failedChunks = state.failedChunkIndexes?.length ? ` · failed chunk: ${state.failedChunkIndexes.map(i => i + 1).join(', ')}` : '';
            englishStatus.textContent = `${state.error?.message || 'English audio ยังไม่พร้อม'}${failedChunks}`;
            const retryEnglish = document.createElement('button');
            retryEnglish.type = 'button';
            retryEnglish.className = 'button secondary';
            retryEnglish.textContent = 'Retry English Audio';
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
            const curRes = await fetch(`/api/jobs/${jobId}`);
            if (!curRes.ok) return;
            const cur = await curRes.json();
            const state = cur.metadata?.englishAudio || {};
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
    }

    const previewLoading = document.querySelector('#previewLoading');
    if (previewLoading) previewLoading.hidden = true;
    const previewContent = document.querySelector('#previewContent');
    if (previewContent) previewContent.hidden = false;
  } catch (e) {
    const box = document.querySelector('#previewError');
    if (box) {
      box.textContent = `${e?.code || 'INTERNAL_ERROR'}: ${e?.message || e || 'Preview unavailable'}`;
      box.hidden = false;
    }
    const previewLoading = document.querySelector('#previewLoading');
    if (previewLoading) previewLoading.hidden = true;
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPreview);
} else {
  initPreview();
}


