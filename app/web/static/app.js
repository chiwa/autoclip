const $=selector=>document.querySelector(selector);
const providerSelect=$('#videoTtsProvider');
const renderEngine=$('#renderEngine'),renderEngineHelp=$('#renderEngineHelp');
const outputFormat=$('#outputFormat'),outputFormatHelp=$('#outputFormatHelp');
function describeOutputFormat(){if(!outputFormatHelp||!outputFormat)return;outputFormatHelp.textContent={use_json:'ใช้ค่า project.resolution ที่ระบุใน script.json',vertical:'บังคับสร้างเป็น 1080x1920',youtube:'บังคับสร้างเป็น 1920x1080 สำหรับ YouTube ปกติ'}[outputFormat.value]||'';}
outputFormat?.addEventListener('change',describeOutputFormat);describeOutputFormat();
function describeRenderEngine(){if(!renderEngineHelp||!renderEngine)return;renderEngineHelp.textContent=renderEngine.value==='wan2.2'||renderEngine.value==='ltx'?'โหมด Hybrid: ซีนที่มี ltx/wan ใช้ LTX Video (RunPod) ส่วนซีนที่ไม่มีใช้ FFmpeg แล้วรวมเสียง ซับ และ BGM ในขั้นสุดท้าย':'ใช้ FFmpeg Motion ทุกซีน แม้ใน JSON จะมีแผน AI motion อยู่ก็ตาม';}
renderEngine?.addEventListener('change',describeRenderEngine);describeRenderEngine();
const motionResolutionWrapper=$('#motionResolutionWrapper'),motionResolution=$('#motionResolution'),motionResolutionHelp=$('#motionResolutionHelp');
function updateMotionResolutionHelp(){if(!motionResolutionHelp||!motionResolution||!outputFormat)return;const fmt=outputFormat.value,res=motionResolution.value;if(fmt==='youtube'){motionResolutionHelp.textContent={'1080p':'1920x1080 (16:9 Full HD)','2k':'2560x1440 (16:9 2K QHD — คมชัดสูง)','4k':'3840x2160 (16:9 4K UHD — คมชัดสูงสุด)'}[res]||'';}else if(fmt==='vertical'){motionResolutionHelp.textContent={'1080p':'1080x1920 (9:16 Full HD)','2k':'1440x2560 (9:16 2K QHD — คมชัดสูง)','4k':'2160x3840 (9:16 4K UHD — คมชัดสูงสุด)'}[res]||'';}else{motionResolutionHelp.textContent={'1080p':'อิงตามขนาดใน script.json (ค่าเริ่มต้น 1080x1920)','2k':'ขยายเป็น 2K (1440x2560 แนวตั้ง / 2560x1440 แนวนอน)','4k':'ขยายเป็น 4K (2160x3840 แนวตั้ง / 3840x2160 แนวนอน)'}[res]||'';}}
motionResolution?.addEventListener('change',updateMotionResolutionHelp);
outputFormat?.addEventListener('change',updateMotionResolutionHelp);
updateMotionResolutionHelp();
function updateRenderEngineVisibility(){const isFfmpeg=(renderEngine?.value||'ffmpeg_motion')==='ffmpeg_motion';if(motionResolutionWrapper)motionResolutionWrapper.hidden=!isFfmpeg;}
renderEngine?.addEventListener('change',updateRenderEngineVisibility);
updateRenderEngineVisibility();
if(providerSelect){ providerSelect.replaceChildren(...[['google-gemini','Google Gemini TTS — Fenrir (Mamase default)'],['kokoro-thai','Wayu Kokoro Thai (ONNX — local)'],['local','Local — Vachana Thai'],['runpod-f5','RunPod — F5-TTS-THAI V2 (A40 GPU)']].map(([value,label])=>{const option=document.createElement('option');option.value=value;option.textContent=label;return option})); providerSelect.value='google-gemini'; }
if(providerSelect && !document.querySelector('#videoTtsVoice')){const voiceLabel=document.createElement('label');voiceLabel.htmlFor='videoTtsVoice';voiceLabel.textContent='เสียงพูด';const voiceSelect=document.createElement('select');voiceSelect.id='videoTtsVoice';voiceLabel.append(voiceSelect);providerSelect.closest('label')?.after(voiceLabel);}
if(providerSelect){const voiceLabel=document.querySelector('label[for="videoTtsVoice"]');const voiceSelect=$('#videoTtsVoice');const setVideoVoiceOptions=()=>{if(!voiceSelect)return;const provider=providerSelect.value;if(provider==='google-gemini'){const add=(label,items)=>{const group=document.createElement('optgroup');group.label=label;items.forEach(([value,text])=>{const option=document.createElement('option');option.value=value;option.textContent=text;group.append(option)});voiceSelect.append(group)};voiceSelect.replaceChildren();add('ชาย',['Fenrir|Fenrir · Mamase default','Enceladus|Enceladus','Alnilam|Alnilam','Charon|Charon','Iapetus|Iapetus','Orus|Orus'].map(x=>x.split('|')));add('หญิง',['Achernar|Achernar','Aoede|Aoede','Autonoe|Autonoe','Callirrhoe|Callirrhoe','Despina|Despina','Erinome|Erinome','Gacrux|Gacrux','Kore|Kore','Leda|Leda'].map(x=>x.split('|')));voiceSelect.value='Fenrir';if(voiceLabel)voiceLabel.childNodes[0].textContent='เสียง Google Gemini';return;}let options=[];if(provider==='kokoro-thai'){options=[['m_young_clear','ผู้ชายวัยหนุ่ม · ชัดเจน (แนะนำ)'],['m_mid_warm','ผู้ชายวัยกลางคน · อบอุ่น']];}else if(provider==='local'){options=[['thai-male-01','ผู้ชาย · Vachana Thai'],['thai-female-01','ผู้หญิง · Vachana Thai']];}else{options=[['thai-male-01','ใช้เสียง reference ของ RunPod F5']];}voiceSelect.replaceChildren(...options.map(([value,label])=>{const option=document.createElement('option');option.value=value;option.textContent=label;return option}));if(voiceLabel)voiceLabel.childNodes[0].textContent=provider==='kokoro-thai'?'เสียง Kokoro Thai':(provider==='local'?'เสียง Vachana Thai':'เสียง RunPod F5');};setVideoVoiceOptions();providerSelect.addEventListener('change',setVideoVoiceOptions);}
const ttsProviderLabel=document.querySelector('label[for="videoTtsProvider"]');
if(ttsProviderLabel)ttsProviderLabel.childNodes[0].textContent='ระบบสร้างเสียง';
const MAMASE_REEL_HOOK_STYLE=`Speak in an energetic, curious Thai male voice.

Deliver the opening question with immediate surprise and excitement, as if you have just discovered something unbelievable and need to tell a friend.

Use a slightly faster pace than normal.

Strongly emphasize the contrast between the surprising fact and the final mystery question.

Keep the delivery conversational, playful, and spontaneous.

Do not shout.
Do not sound like a commercial, movie trailer, news presenter, or exaggerated YouTuber.

The Hook is normally designed for the first 3–5 seconds.`;
const MAMASE_REEL_NORMAL_STYLE=`Speak like a charismatic Thai science storyteller with a playful personality.

Sound curious, friendly, warm, and conversational, as if telling an interesting science story to a friend.

Keep the delivery natural and connected, with light energy and genuine excitement when surprising facts appear.

Use small natural pauses for emphasis and comedic timing when appropriate.

Do not rush.
Do not over-dramatize.
Do not sound like a news anchor, lecturer, movie trailer, advertisement, or exaggerated YouTuber.

Keep the tone playful and engaging, but still clear enough for scientific explanations.`;
const REEL_TTS_STORAGE_KEY='autoclip.reelTtsDefaults.v2';
const BUILTIN_REEL_TTS={voice:'Fenrir',hook:{speed:1.10,style:MAMASE_REEL_HOOK_STYLE},normal:{speed:1.05,style:MAMASE_REEL_NORMAL_STYLE},outro:{enabled:true,image:'mamase-reels-end-scence.png',duration:2.0,bgm_fade_out:true}};
const cloneBuiltinReelTts=()=>JSON.parse(JSON.stringify(BUILTIN_REEL_TTS));
function loadSavedReelTts(){
  try{
    const current=JSON.parse(localStorage.getItem(REEL_TTS_STORAGE_KEY)||'null');
    if(current)return current;
    const legacy=JSON.parse(localStorage.getItem('autoclip.mamaseTts')||'null');
    if(legacy)return {voice:legacy.voice||'Fenrir',hook:{speed:Number(legacy.speed||1.10),style:legacy.style||MAMASE_REEL_HOOK_STYLE},normal:{speed:Number(legacy.speed||1.05),style:legacy.style||MAMASE_REEL_NORMAL_STYLE}};
  }catch(_error){}
  return cloneBuiltinReelTts();
}
let savedReelTts=loadSavedReelTts();
const ensureMamaseTtsControls=()=>{
  if($('#videoTtsHookSpeed'))return;
  const anchor=document.querySelector('label[for="videoTtsVoice"]')||ttsProviderLabel;
  if(!anchor)return;
  const makeSpeed=(id,label,value)=>{const wrapper=document.createElement('label');wrapper.htmlFor=id;wrapper.textContent=label+' ';const input=document.createElement('input');input.id=id;input.type='range';input.min='0.5';input.max='2';input.step='0.05';input.value=String(value);const output=document.createElement('output');output.id=id+'Value';output.textContent=Number(value).toFixed(2);input.addEventListener('input',()=>{output.textContent=Number(input.value).toFixed(2)});wrapper.append(input,output);return wrapper;};
  const makeStyle=(id,label,value)=>{const wrapper=document.createElement('label');wrapper.htmlFor=id;wrapper.textContent=label;const input=document.createElement('textarea');input.id=id;input.rows=7;input.value=value;wrapper.append(input);return wrapper;};
  const hookSpeed=makeSpeed('videoTtsHookSpeed','Hook Speed',savedReelTts.hook?.speed??1.10);
  const hookStyle=makeStyle('videoTtsHookStyle','Hook Style Prompt',savedReelTts.hook?.style||MAMASE_REEL_HOOK_STYLE);
  const normalSpeed=makeSpeed('videoTtsNormalSpeed','Normal Speed',savedReelTts.normal?.speed??1.05);
  const normalStyle=makeStyle('videoTtsNormalStyle','Normal Style Prompt',savedReelTts.normal?.style||MAMASE_REEL_NORMAL_STYLE);
  const outro=document.createElement('fieldset');outro.id='reelOutroControls';outro.innerHTML='<legend>Outro / End Card</legend><label><input id="reelOutroEnabled" type="checkbox" checked> Enable Outro</label><label for="reelOutroImage">Outro Image<input id="reelOutroImage" value="mamase-reels-end-scence.png"></label><label for="reelOutroDuration">Outro Duration <input id="reelOutroDuration" type="range" min="1.5" max="2.5" step="0.1" value="2.0"><output id="reelOutroDurationValue">2.0</output> วินาที</label><label><input id="reelOutroFade" type="checkbox" checked> Fade BGM Out</label>';
  outro.querySelector('#reelOutroDuration').addEventListener('input',event=>{$('#reelOutroDurationValue').textContent=Number(event.target.value).toFixed(1)});
  const controls=document.createElement('div');controls.id='mamaseTtsControls';controls.className='tts-preview-controls';controls.innerHTML='<button id="saveMamaseTts" type="button" class="secondary">บันทึกเป็นค่าเริ่มต้น</button><button id="resetMamaseTts" type="button" class="secondary">คืนค่า Mamase default</button><button id="previewMamaseHookTts" type="button" class="secondary">ฟัง Hook</button><button id="previewMamaseNormalTts" type="button" class="secondary">ฟัง Normal</button><audio id="mamaseTtsAudio" controls preload="none" hidden></audio><span id="mamaseTtsStatus" class="muted" role="status"></span>';
  anchor.after(hookSpeed,hookStyle,normalSpeed,normalStyle,outro,controls);
};
ensureMamaseTtsControls();
applyReelTtsControls(savedReelTts);
if(!$('#googleTtsConsoleLink')){const link=document.createElement('a');link.id='googleTtsConsoleLink';link.className='button secondary';link.target='_blank';link.rel='noopener';link.href='https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/metrics?project=project-b25038eb-bdea-4d70-b72';link.textContent='ดู Google Gemini TTS usage / quota';$('#mamaseTtsControls')?.append(link);}
function readReelTtsControls(){return {voice:$('#videoTtsVoice')?.value||'Fenrir',hook:{speed:Number($('#videoTtsHookSpeed')?.value||1.10),style:$('#videoTtsHookStyle')?.value?.trim()||$('#videoTtsNormalStyle')?.value?.trim()||MAMASE_REEL_NORMAL_STYLE},normal:{speed:Number($('#videoTtsNormalSpeed')?.value||1.05),style:$('#videoTtsNormalStyle')?.value?.trim()||MAMASE_REEL_NORMAL_STYLE},outro:{enabled:Boolean($('#reelOutroEnabled')?.checked),image:$('#reelOutroImage')?.value?.trim()||'mamase-reels-end-scence.png',duration:Number($('#reelOutroDuration')?.value||2),bgm_fade_out:Boolean($('#reelOutroFade')?.checked)}};}
function applyReelTtsControls(config){const merged={voice:config?.voice||savedReelTts.voice||'Fenrir',hook:{speed:config?.hook?.speed??savedReelTts.hook?.speed??1.10,style:config?.hook?.style||config?.normal?.style||savedReelTts.hook?.style||savedReelTts.normal?.style||MAMASE_REEL_HOOK_STYLE},normal:{speed:config?.normal?.speed??savedReelTts.normal?.speed??1.05,style:config?.normal?.style||savedReelTts.normal?.style||MAMASE_REEL_NORMAL_STYLE},outro:{enabled:config?.outro?.enabled??savedReelTts.outro?.enabled??true,image:config?.outro?.image||savedReelTts.outro?.image||'mamase-reels-end-scence.png',duration:config?.outro?.duration??savedReelTts.outro?.duration??2,bgm_fade_out:config?.outro?.bgm_fade_out??savedReelTts.outro?.bgm_fade_out??true}};if($('#videoTtsVoice'))$('#videoTtsVoice').value=merged.voice;for(const [id,value] of [['videoTtsHookSpeed',merged.hook.speed],['videoTtsNormalSpeed',merged.normal.speed]]){if($('#'+id))$('#'+id).value=String(value);if($('#'+id+'Value'))$('#'+id+'Value').textContent=Number(value).toFixed(2);}if($('#videoTtsHookStyle'))$('#videoTtsHookStyle').value=merged.hook.style;if($('#videoTtsNormalStyle'))$('#videoTtsNormalStyle').value=merged.normal.style;if($('#reelOutroEnabled'))$('#reelOutroEnabled').checked=merged.outro.enabled;if($('#reelOutroImage'))$('#reelOutroImage').value=merged.outro.image;if($('#reelOutroDuration'))$('#reelOutroDuration').value=String(merged.outro.duration);if($('#reelOutroDurationValue'))$('#reelOutroDurationValue').textContent=Number(merged.outro.duration).toFixed(1);if($('#reelOutroFade'))$('#reelOutroFade').checked=merged.outro.bgm_fade_out;}
$('#saveMamaseTts')?.addEventListener('click',()=>{savedReelTts=readReelTtsControls();localStorage.setItem(REEL_TTS_STORAGE_KEY,JSON.stringify(savedReelTts));$('#mamaseTtsStatus').textContent='บันทึกค่าเริ่มต้น Reel แล้ว';});
$('#resetMamaseTts')?.addEventListener('click',()=>{savedReelTts=cloneBuiltinReelTts();localStorage.setItem(REEL_TTS_STORAGE_KEY,JSON.stringify(savedReelTts));if(providerSelect){providerSelect.value='google-gemini';providerSelect.dispatchEvent(new Event('change'));}applyReelTtsControls(savedReelTts);$('#mamaseTtsStatus').textContent='คืนค่า Mamase Reel default แล้ว';});
async function previewReelTts(mode){const isHook=mode==='hook',button=$(isHook?'#previewMamaseHookTts':'#previewMamaseNormalTts'),status=$('#mamaseTtsStatus'),audio=$('#mamaseTtsAudio'),config=readReelTtsControls(),selected=config[mode];button.disabled=true;status.textContent='กำลังสร้างเสียงตัวอย่าง…';try{const body=new FormData();body.append('text',isHook?'ถ้าดาวอังคารเคยมีทะเลจริง! แล้วน้ำทั้งดาว…หายไปไหนหมด?':'เมื่อหลายพันล้านปีก่อน ดาวอังคารไม่ได้แห้งแล้งแบบที่เราเห็นทุกวันนี้ครับ');body.append('provider',providerSelect?.value||'google-gemini');body.append('voice',config.voice);body.append('speed',String(selected.speed));body.append('style_prompt',selected.style);const response=await fetch('/api/tts',{method:'POST',body});if(!response.ok){const data=await response.json();throw data.detail||data}const blob=await response.blob();if(audio.dataset.objectUrl)URL.revokeObjectURL(audio.dataset.objectUrl);audio.dataset.objectUrl=URL.createObjectURL(blob);audio.src=audio.dataset.objectUrl;audio.hidden=false;await audio.play();status.textContent=`กำลังเล่นเสียง ${isHook?'Hook':'Normal'}`}catch(error){status.textContent=`${error?.code||'TTS_GENERATION_FAILED'}: ${error?.message||'สร้างเสียงไม่สำเร็จ'}`}finally{button.disabled=false}}
$('#previewMamaseHookTts')?.addEventListener('click',()=>previewReelTts('hook'));
$('#previewMamaseNormalTts')?.addEventListener('click',()=>previewReelTts('normal'));
(()=>{const card=document.querySelector('#uploadView .hero-card');if(!card)return;const group=(title,detail,items)=>{const section=document.createElement('section');section.className='workspace-section';section.innerHTML=`<h2>${title}</h2><p class="muted">${detail}</p>`;items.filter(Boolean).forEach(item=>section.append(item));card.append(section);};const byFor=id=>document.querySelector(`label[for="${id}"]`);group('1. ZIP และ Preview','อัปโหลด package ก่อน แล้วตรวจบทและภาพทีละซีน',[document.querySelector('.picker'),$('#fileInfo')]);group('2. ภาพและรูปแบบวิดีโอ','เลือกสัดส่วน ความละเอียด และวิธีทำ motion',[byFor('outputFormat'),$('#outputFormatHelp'),byFor('renderEngine'),$('#renderEngineHelp'),$('#motionResolutionWrapper')]);group('3. เสียง ซับ และเพลง','Google Gemini Fenrir คือค่าเริ่มต้นของ Mamase',[byFor('videoTtsProvider'),document.querySelector('label[for="videoTtsVoice"]'),byFor('videoSubtitleMode'),document.querySelector('.bgm-preview')]);const make=$('#generate');if(make)group('4. สร้างวิดีโอ','กดสร้างหลังตรวจ Preview เรียบร้อย',[make]);})();
const audioWorkspaceSection=[...document.querySelectorAll('#uploadView .workspace-section')].find(section=>section.querySelector('#videoTtsProvider'));
if(audioWorkspaceSection){[document.querySelector('label[for="videoTtsHookSpeed"]'),document.querySelector('label[for="videoTtsHookStyle"]'),document.querySelector('label[for="videoTtsNormalSpeed"]'),document.querySelector('label[for="videoTtsNormalStyle"]'),$('#reelOutroControls'),$('#mamaseTtsControls')].filter(Boolean).forEach(element=>audioWorkspaceSection.append(element));}
const bgmButton=$('#previewBgm'),bgmAudio=$('#bgmAudio'),bgmStatus=$('#bgmStatus');
bgmButton?.addEventListener('click',async()=>{bgmButton.disabled=true;bgmStatus.textContent='กำลังเตรียมเสียง BGM…';try{if(!bgmAudio.src)bgmAudio.src='/api/bgm-preview';bgmAudio.hidden=false;await bgmAudio.play();bgmStatus.textContent='กำลังเล่น BGM ระบบ';}catch(e){bgmStatus.textContent='ไม่สามารถเล่น BGM ได้';}finally{bgmButton.disabled=false}});
const uploadView=$('#uploadView'),progressView=$('#progressView'),file=$('#file'),generate=$('#generate'),info=$('#fileInfo');
const state=$('#state'),percent=$('#percent'),progress=$('#progress'),step=$('#step'),error=$('#error'),logs=$('#logs'),technicalLogs=$('#technicalLogs');
let source=null,lastFile=null,previewScript=null,previewDirty=false,manuallyScrolled=false,technicalManuallyScrolled=false;const logKeys=new Set(),technicalKeys=new Set();
document.addEventListener('change',event=>{if(event.target?.id==='videoTtsVoice'&&previewScript){previewScript.voice=previewScript.voice||{};previewScript.voice.voice=event.target.value;previewScript.reel_tts=previewScript.reel_tts||{};previewScript.reel_tts.voice=event.target.value}});
file.onchange=async()=>{lastFile=file.files[0]||null;info.textContent=lastFile?`${lastFile.name} · ${(lastFile.size/1024/1024).toFixed(2)} MB`:'No file selected';generate.disabled=true;if(!lastFile)return;const body=new FormData();body.append('file',lastFile);const box=$('#packagePreview'),list=$('#previewScenes'),errorBox=$('#previewError');box.hidden=false;list.textContent='กำลังอ่าน script.json และเตรียมภาพ Preview…';errorBox.hidden=true;try{const r=await fetch('/api/package-preview',{method:'POST',body}),data=await r.json();if(!r.ok)throw data.detail||data;previewScript=data.script;applyReelTtsControls(previewScript.reel_tts||savedReelTts);$('#previewProject').textContent=`${previewScript.project.title} · ${previewScript.scenes.length} scenes`;list.replaceChildren(...previewScript.scenes.map((scene,index)=>{const card=document.createElement('article');card.className='scene-card';const image=data.imagePreviews?.[scene.id];card.innerHTML=`<div class="scene-number">${String(index+1).padStart(2,'0')}</div><div class="scene-body"><h3>${scene.id}</h3>${image?`<img src="${image}" alt="${scene.id}">`:''}<label>Narration<textarea data-key="narration" rows="3">${scene.narration}</textarea></label><label>Subtitle<textarea data-key="subtitle" rows="2">${scene.subtitle||scene.narration}</textarea></label><div class="tts-options"><label>Motion<select data-key="motion"><option>none</option><option>slow_zoom_in</option><option>slow_zoom_out</option><option>pan_left_to_right</option><option>pan_right_to_left</option><option>pan_up</option><option>pan_down</option><option>cinematic_push_in</option><option>cinematic_pull_out</option><option>documentary_pan</option><option>gentle_float</option></select></label><label>Transition<input data-key="transition" value="${scene.transition||'fade'}"></label></div><div class="scene-tts-preview"><button type="button" class="button secondary scene-tts-button">ฟังเสียงฉากนี้ (${index===0?'Hook':'Normal'})</button><audio class="scene-tts-audio" controls preload="none" hidden></audio><span class="muted scene-tts-status" role="status"></span></div></div>`;card.querySelector('[data-key="motion"]').value=scene.motion;card.querySelectorAll('[data-key]').forEach(el=>el.oninput=()=>{scene[el.dataset.key]=el.value});const playButton=card.querySelector('.scene-tts-button'),audio=card.querySelector('.scene-tts-audio'),audioStatus=card.querySelector('.scene-tts-status');playButton.onclick=async()=>{const speechText=(scene.tts_text||scene.narration||'').trim();if(!speechText){audioStatus.textContent='ไม่มีข้อความสำหรับสร้างเสียง';return}playButton.disabled=true;audioStatus.textContent='กำลังสร้างเสียง…';try{const ttsBody=new FormData(),config=readReelTtsControls(),mode=index===0?'hook':'normal';ttsBody.append('text',speechText);ttsBody.append('provider',$('#videoTtsProvider')?.value||'google-gemini');ttsBody.append('voice',config.voice);ttsBody.append('speed',String(config[mode].speed));ttsBody.append('style_prompt',config[mode].style);const ttsResponse=await fetch('/api/tts',{method:'POST',body:ttsBody});if(!ttsResponse.ok){const errorData=await ttsResponse.json();throw errorData.detail||errorData}const blob=await ttsResponse.blob();if(audio.dataset.objectUrl)URL.revokeObjectURL(audio.dataset.objectUrl);const objectUrl=URL.createObjectURL(blob);audio.dataset.objectUrl=objectUrl;audio.src=objectUrl;audio.hidden=false;audioStatus.textContent='พร้อมฟังเสียง';await audio.play()}catch(error){audioStatus.textContent=`${error?.code||'TTS_GENERATION_FAILED'}: ${error?.message||'สร้างเสียงไม่สำเร็จ'}`}finally{playButton.disabled=false}};return card}));generate.disabled=false}catch(e){list.replaceChildren();errorBox.textContent=`${e.code||'PACKAGE_INVALID'}: ${e.message||'ไม่สามารถอ่าน ZIP ได้'}`;errorBox.hidden=false}}
document.addEventListener('input',event=>{if(event.target?.dataset?.key&&previewScript)previewDirty=true;if(event.target?.dataset?.key!=='subtitle'||!previewScript)return;const card=event.target.closest('.scene-card');const index=card?[...$('#previewScenes').children].indexOf(card):-1;if(index>=0)previewScript.scenes[index].show_subtitle=true});
function downloadPackageScriptJson(obj, filename) {
  const jsonStr = JSON.stringify(obj, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
const btnViewPackageJson = $('#btnViewPackageJson');
const btnExportPackageJson = $('#btnExportPackageJson');
const jsonViewDialog = $('#jsonViewDialog');
const jsonDialogCode = $('#jsonDialogCode');
const btnCopyJsonDialog = $('#btnCopyJsonDialog');
const btnDownloadJsonDialog = $('#btnDownloadJsonDialog');
const btnCloseJsonDialog = $('#btnCloseJsonDialog');
const btnCloseJsonDialogFooter = $('#btnCloseJsonDialogFooter');
if (btnViewPackageJson && jsonViewDialog) {
  const closePackageModal = () => {
    if (typeof jsonViewDialog.close === 'function') {
      try { jsonViewDialog.close(); } catch (_) {}
    }
    jsonViewDialog.removeAttribute('open');
    jsonViewDialog.style.display = 'none';
  };

  btnViewPackageJson.addEventListener('click', (e) => {
    e.preventDefault();
    if (!previewScript) {
      alert('ยังไม่ได้อัปโหลดหรือเปิดแพ็กเกจ');
      return;
    }
    if (jsonDialogCode) jsonDialogCode.textContent = JSON.stringify(previewScript, null, 2);
    jsonViewDialog.setAttribute('open', '');
    if (typeof jsonViewDialog.showModal === 'function') {
      try { jsonViewDialog.showModal(); } catch (_) {}
    }
    jsonViewDialog.style.display = 'block';
  });
  btnCloseJsonDialog?.addEventListener('click', closePackageModal);
  btnCloseJsonDialogFooter?.addEventListener('click', closePackageModal);
  jsonViewDialog.addEventListener('click', (e) => {
    if (e.target === jsonViewDialog) closePackageModal();
  });
  btnCopyJsonDialog?.addEventListener('click', async () => {
    if (!previewScript) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(previewScript, null, 2));
      const orig = btnCopyJsonDialog.textContent;
      btnCopyJsonDialog.textContent = '✓ คัดลอกแล้ว!';
      setTimeout(() => { btnCopyJsonDialog.textContent = orig; }, 2000);
    } catch (_) {
      alert('คัดลอกไม่สำเร็จ');
    }
  });
  btnDownloadJsonDialog?.addEventListener('click', () => {
    if (!previewScript) return;
    const titleName = previewScript.project?.title ? previewScript.project.title.replace(/[\\/*?:"<>|]/g, '').trim().replace(/\s+/g, '-') : 'script';
    downloadPackageScriptJson(previewScript, `${titleName || 'script'}.json`);
  });
}
if (btnExportPackageJson) {
  btnExportPackageJson.addEventListener('click', (e) => {
    e.preventDefault();
    if (!previewScript) {
      alert('ยังไม่ได้อัปโหลดหรือเปิดแพ็กเกจ');
      return;
    }
    const titleName = previewScript.project?.title ? previewScript.project.title.replace(/[\\/*?:"<>|]/g, '').trim().replace(/\s+/g, '-') : 'script';
    downloadPackageScriptJson(previewScript, `${titleName || 'script'}.json`);
  });
}
logs.addEventListener('scroll',()=>{manuallyScrolled=logs.scrollHeight-logs.scrollTop-logs.clientHeight>40});
technicalLogs?.addEventListener('scroll',()=>{technicalManuallyScrolled=technicalLogs.scrollHeight-technicalLogs.scrollTop-technicalLogs.clientHeight>40});
function updateSnapshot(job){state.textContent=job.status;percent.textContent=`${job.progress}%`;progress.value=job.progress;step.textContent=job.currentStep;appendTechnical({timestamp:new Date().toISOString(),level:'STATE',message:`${job.status} · ${job.progress}% · ${job.currentStep||''}`});if(job.logs)renderLogs(job.logs);if(job.status==='FAILED')showFailure(job.error,job.currentStep)}
function renderLogs(entries){logs.replaceChildren();logKeys.clear();entries.forEach(appendLog)}
function appendLog(entry){const key=`${entry.timestamp}|${entry.level}|${entry.message}`;if(logKeys.has(key))return;logKeys.add(key);const row=document.createElement('div');row.className=`log ${String(entry.level||'INFO').toLowerCase()}`;const time=new Date(entry.timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});row.textContent=`${time}  ${entry.message}`;logs.append(row);if(!manuallyScrolled)logs.scrollTop=logs.scrollHeight}
function appendTechnical(entry){if(!technicalLogs)return;const key=`${entry.timestamp}|${entry.level}|${entry.message}`;if(technicalKeys.has(key))return;technicalKeys.add(key);const row=document.createElement('div');row.className='log technical-entry';const time=new Date(entry.timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});row.textContent=`${time} [${entry.level||'INFO'}] ${entry.message}`;technicalLogs.append(row);if(!technicalManuallyScrolled)technicalLogs.scrollTop=technicalLogs.scrollHeight}
function showFailure(failure,currentStep){source?.close();$('#progressTitle').textContent='Generation Failed';step.textContent=currentStep||step.textContent;$('#errorCode').textContent=failure?.code||'INTERNAL_ERROR';$('#errorMessage').textContent=failure?.message||'Video generation failed';error.hidden=false}
async function restore(jobId){const response=await fetch(`/api/jobs/${jobId}`);if(!response.ok){location.href='/';return null}const job=await response.json();updateSnapshot(job);if(job.status==='COMPLETED'){location.replace(`/jobs/${jobId}/preview`);return null}return job}
function attachEventSource(jobId){source?.close();source=new EventSource(`/api/jobs/${jobId}/events`);source.addEventListener('progress',event=>{const data=JSON.parse(event.data);appendTechnical({timestamp:new Date().toISOString(),level:'PROGRESS',message:`${data.status} · ${data.progress}% · ${data.currentStep||''}`});updateSnapshot(data)});source.addEventListener('log',event=>{const data=JSON.parse(event.data);if(!data.technical)appendLog(data);appendTechnical(data)});source.addEventListener('completed',event=>{const data=JSON.parse(event.data);appendTechnical({timestamp:new Date().toISOString(),level:'COMPLETED',message:'Video generation completed'});source.close();try{sessionStorage.setItem('autoclip_notify_success','1');window.AutoClipSound?.playSuccess()}catch(_){}setTimeout(()=>{location.replace(data.previewUrl)},350)});source.addEventListener('failed',event=>{const data=JSON.parse(event.data);appendTechnical({timestamp:new Date().toISOString(),level:'FAILED',message:`${data.code||'INTERNAL_ERROR'} · ${data.message||''}`});try{window.AutoClipSound?.playError()}catch(_){}updateSnapshot(data);showFailure(data,data.currentStep)});source.onerror=()=>{appendTechnical({timestamp:new Date().toISOString(),level:'RECONNECT',message:'SSE connection interrupted; restoring state'});restore(jobId)}}
async function connect(jobId){uploadView.hidden=true;progressView.hidden=false;const job=await restore(jobId);if(!job||job.status==='FAILED')return;attachEventSource(jobId)}
async function submit(selected){generate.disabled=true;error.hidden=true;const body=new FormData();const selectedProvider=$('#videoTtsProvider').value;body.append('file',selected);body.append('tts_provider',selectedProvider);const curEngine=renderEngine?.value||'ffmpeg_motion';body.append('render_engine',curEngine);body.append('output_format',outputFormat?.value||'use_json');if(curEngine==='ffmpeg_motion'){const resTier=motionResolution?.value||'1080p';body.append('motion_resolution',resTier);if(previewScript&&resTier!=='1080p'){let curW=1080,curH=1920;if(previewScript.project?.resolution){const parts=previewScript.project.resolution.split('x').map(Number);if(parts.length===2&&!isNaN(parts[0])&&!isNaN(parts[1])){curW=parts[0];curH=parts[1];}}if(outputFormat?.value==='youtube'||(outputFormat?.value==='use_json'&&curW>curH)){previewScript.project.resolution=resTier==='2k'?'2560x1440':'3840x2160';}else{previewScript.project.resolution=resTier==='2k'?'1440x2560':'2160x3840';}}}if(previewScript){previewScript.voice=previewScript.voice||{};previewScript.voice.provider=selectedProvider;previewScript.voice.voice=$('#videoTtsVoice')?.value||previewScript.voice.voice||(selectedProvider==='kokoro-thai'?'m_young_clear':'thai-male-01');body.append('script_json',JSON.stringify(previewScript))}const subMode=$('#videoSubtitleMode')?.value;if(subMode)body.append('subtitle_mode',subMode);try{const response=await fetch('/api/jobs',{method:'POST',body});const data=await response.json();if(!response.ok)throw data.detail||data;history.pushState({},'',`/jobs/${data.jobId}`);await connect(data.jobId)}catch(e){uploadView.hidden=false;progressView.hidden=true;alert(`${e?.code||'INTERNAL_ERROR'}: ${e?.message||'Request failed'}`)}finally{generate.disabled=false}}
generate.onclick=()=>lastFile&&submit(lastFile);
$('#retry')?.addEventListener('click',async()=>{const m=location.pathname.match(/^\/jobs\/([^/]+)$/);const currentJobId=m?m[1]:null;if(!currentJobId){source?.close();location.href='/';return;}const btn=$('#retry');btn.disabled=true;try{error.hidden=true;$('#progressTitle').textContent='Generating video…';step.textContent='กำลังเริ่มประมวลผลใหม่อีกครั้ง...';const res=await fetch(`/api/jobs/${currentJobId}/retry`,{method:'POST'});const data=await res.json();if(!res.ok)throw data.detail||data;attachEventSource(currentJobId);}catch(e){showFailure(e,'ไม่สามารถเริ่มประมวลผลใหม่ได้');}finally{btn.disabled=false;}});
const match=location.pathname.match(/^\/jobs\/([^/]+)$/);if(match)connect(match[1]);
const toggleTechnical=$('#toggleTechnical'),technicalSection=$('#technicalLogSection');
toggleTechnical?.addEventListener('click',()=>{const open=technicalSection.hidden;technicalSection.hidden=!open;toggleTechnical.setAttribute('aria-expanded',String(open));toggleTechnical.textContent=open?'ซ่อน Live technical log':'แสดง Live technical log'});
function syncPreviewFields(){if(!previewScript)return;[...$('#previewScenes').children].forEach((card,index)=>{const scene=previewScript.scenes[index];if(!scene)return;card.querySelectorAll('[data-key]').forEach(el=>{const value=el.value;if(!(el.dataset.key==='motion'&&value===''))scene[el.dataset.key]=value});});}
generate.addEventListener('click',()=>{syncPreviewFields();if(!previewScript)return;const reelConfig=readReelTtsControls(),{outro,...reelTts}=reelConfig;previewScript.reel_tts=reelTts;previewScript.outro=outro;previewScript.voice=previewScript.voice||{};previewScript.voice.provider=providerSelect?.value||'google-gemini';previewScript.voice.voice=reelTts.voice;previewScript.voice.speed=reelTts.normal.speed;previewScript.voice.style_prompt=reelTts.normal.style;});
generate.onclick=()=>{syncPreviewFields();if(previewScript){const reelConfig=readReelTtsControls(),{outro,...reelTts}=reelConfig;previewScript.reel_tts=reelTts;previewScript.outro=outro;previewScript.voice=previewScript.voice||{};previewScript.voice.provider=providerSelect?.value||'google-gemini';previewScript.voice.voice=reelTts.voice;previewScript.voice.speed=reelTts.normal.speed;previewScript.voice.style_prompt=reelTts.normal.style;}if(lastFile)submit(lastFile);};
$('#generateFromPreview')?.addEventListener('click',()=>{syncPreviewFields();generate.click()});
const previewTabObserver=new MutationObserver(()=>{const list=$('#previewScenes'),tabs=$('#previewTabs');if(!list||!tabs||!list.children.length||tabs.dataset.ready==='1')return;tabs.dataset.ready='1';const cards=[...list.children];cards.forEach((card,index)=>{card.hidden=index!==0;const tab=document.createElement('button');tab.type='button';tab.className='preview-tab'+(index===0?' active':'');tab.textContent=`Scene ${index+1}`;tab.setAttribute('role','tab');tab.onclick=()=>{cards.forEach((item,i)=>item.hidden=i!==index);tabs.querySelectorAll('button').forEach((item,i)=>item.classList.toggle('active',i===index))};tabs.append(tab)})});
const previewResetObserver=new MutationObserver(()=>{if(previewScript&&document.activeElement?.dataset?.key==null)previewDirty=false});
const reelConfigObserver=new MutationObserver(()=>{const list=$('#previewScenes'),key=`${previewScript?.project?.id||''}:${previewScript?.scenes?.length||0}`;if(!previewScript||!list?.children.length||list.dataset.reelConfigProject===key)return;list.dataset.reelConfigProject=key;applyReelTtsControls({...savedReelTts,...(previewScript.reel_tts||{}),outro:previewScript.outro||savedReelTts.outro});});
const ttsTextObserver=new MutationObserver(()=>{if(!previewScript)return;[...($('#previewScenes')?.children||[])].forEach((card,i)=>{if(card.querySelector('[data-key="tts_text"]'))return;const scene=previewScript.scenes[i];if(!scene)return;const label=document.createElement('label');label.textContent='TTS Pronunciation';const input=document.createElement('textarea');input.rows=2;input.dataset.key='tts_text';input.value=scene.tts_text||'';input.oninput=()=>{scene.tts_text=input.value;previewDirty=true};label.append(input);card.querySelector('.scene-body')?.append(label)})});
ttsTextObserver.observe(document.body,{childList:true,subtree:true});
previewResetObserver.observe($('#previewScenes'),{childList:true});
reelConfigObserver.observe($('#previewScenes'),{childList:true});
const motionOptionObserver=new MutationObserver(()=>{const list=$('#previewScenes');if(!list||!previewScript)return;const motions=['none','auto','slow_zoom_in','slow_zoom_out','pan_left_to_right','pan_right_to_left','pan_up','pan_down','zoom_in','zoom_out','zoom_in_top_left','zoom_in_top_right','zoom_in_bottom_left','zoom_in_bottom_right','pan_left_to_right_zoom_in','pan_right_to_left_zoom_in','pan_up_zoom_in','pan_down_zoom_in','drift_top_left','drift_top_right','drift_bottom_left','drift_bottom_right','cinematic_push_in','cinematic_pull_out','gentle_float','documentary_pan'];list.querySelectorAll('select[data-key="motion"]').forEach((select,index)=>{const current=previewScript.scenes[index]?.motion;if(current&&!select.querySelector(`option[value="${current}"]`)){const option=document.createElement('option');option.value=current;option.textContent=current;select.append(option)}select.value=current||select.value})});
motionOptionObserver.observe($('#previewScenes'),{childList:true});
function addWanPreviewDetails(){const list=$('#previewScenes');if(!list||!previewScript)return;[...list.children].forEach((card,index)=>{const aiOpts=previewScript.scenes[index]?.ltx||previewScript.scenes[index]?.wan;if(!aiOpts||card.querySelector('.wan-details'))return;const details=document.createElement('details');details.className='wan-details';details.open=true;const summary=document.createElement('summary');summary.textContent='แผนสร้างภาพเคลื่อนไหว LTX Video (AI)';details.append(summary);const grid=document.createElement('div');grid.className='wan-editor';const addField=(label,input,update)=>{const field=document.createElement('label');field.textContent=label;field.append(input);input.addEventListener('input',()=>{update(input);previewDirty=true});input.addEventListener('change',()=>{update(input);previewDirty=true});grid.append(field)};const prompt=document.createElement('textarea');prompt.rows=4;prompt.value=aiOpts.prompt;addField('Prompt',prompt,input=>{aiOpts.prompt=input.value});const negative=document.createElement('textarea');negative.rows=3;negative.value=aiOpts.negative_prompt||'';addField('Negative prompt',negative,input=>{aiOpts.negative_prompt=input.value});const options=document.createElement('div');options.className='wan-options';const seed=document.createElement('input');seed.type='number';seed.min='0';seed.max='2147483647';seed.placeholder='อัตโนมัติ';seed.value=aiOpts.seed??'';const frames=document.createElement('input');frames.type='number';frames.min='9';frames.max='300';frames.step='1';frames.placeholder='อัตโนมัติ';frames.value=aiOpts.frames??'';const steps=document.createElement('input');steps.type='number';steps.min='1';steps.max='50';steps.placeholder='ค่าเริ่มต้น 8';steps.value=aiOpts.steps??'';const lip=document.createElement('input');lip.type='checkbox';lip.checked=Boolean(aiOpts.lip_sync);const character=document.createElement('input');character.type='text';character.maxLength=128;character.placeholder='—';character.value=aiOpts.character_id||'';const addOption=(label,input,update)=>{const field=document.createElement('label');field.textContent=label;field.append(input);input.addEventListener('input',()=>{update(input);previewDirty=true});input.addEventListener('change',()=>{update(input);previewDirty=true});options.append(field)};addOption('Seed',seed,input=>{aiOpts.seed=input.value===''?null:Number(input.value)});addOption('จำนวนเฟรม',frames,input=>{aiOpts.frames=input.value===''?null:Number(input.value)});addOption('Steps (ค่าเริ่มต้น 8)',steps,input=>{aiOpts.steps=input.value===''?null:Number(input.value)});addOption('ขยับปาก',lip,input=>{aiOpts.lip_sync=input.checked});addOption('ตัวละคร',character,input=>{aiOpts.character_id=input.value.trim()||null});grid.append(options);details.append(grid);card.querySelector('.scene-body')?.append(details)})}
const wanPreviewObserver=new MutationObserver(addWanPreviewDetails);
wanPreviewObserver.observe($('#previewScenes'),{childList:true,subtree:true});
previewTabObserver.observe($('#previewScenes'),{childList:true});

let ttsObjectUrl=null;
if($('#ttsGenerate')) $('#ttsGenerate').onclick=async()=>{
  const button=$('#ttsGenerate'),status=$('#ttsStatus'),result=$('#ttsResult');
  const text=$('#ttsText').value.trim();
  if(!text){status.textContent='กรุณาป้อนข้อความภาษาไทย';return}
  button.disabled=true;status.textContent='กำลังสร้างเสียง…';result.hidden=true;
  const body=new FormData();body.append('text',text);body.append('voice',$('#ttsVoice').value);body.append('speed',$('#ttsSpeed').value);
  try{
    const response=await fetch('/api/tts',{method:'POST',body});
    if(!response.ok){const data=await response.json();throw data.detail||data}
    const blob=await response.blob();if(ttsObjectUrl)URL.revokeObjectURL(ttsObjectUrl);ttsObjectUrl=URL.createObjectURL(blob);
    $('#ttsAudio').src=ttsObjectUrl;$('#ttsDownload').href=ttsObjectUrl;result.hidden=false;status.textContent='สร้างเสียงสำเร็จ';
  }catch(e){status.textContent=`${e?.code||'TTS_GENERATION_FAILED'}: ${e?.message||'สร้างเสียงไม่สำเร็จ'}`}
  finally{button.disabled=false}
};
