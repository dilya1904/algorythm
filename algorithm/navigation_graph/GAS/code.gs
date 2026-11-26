/**
 * DijkstraLab Navigation Graph GAS Web App Controller
 * - $gas-python-startup-link: PropertiesService('PYTHON_SERVER_URL') 기반 자동/수동 연결 제어
 * - $gas-empty-initial-state: 하드코딩된 샘플/더미 데이터 없음
 * - $gas-url-sync: 배포된 Cloud Run URL을 초기 1회 PropertiesService에 안전하게 시드할 수 있는 훅 지원
 */

function doGet() {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('DijkstraLab — 다익스트라 네비게이션 길찾기 시각화')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * PropertiesService(PYTHON_SERVER_URL)에서 Python 서버 URL을 읽습니다.
 * 초기 미설정 상태에서 Config.gs에 동기화된 URL이 있으면 1회 PropertiesService에 자동 반영합니다.
 * @returns {string}
 */
function getPythonServerUrl_() {
  const props = PropertiesService.getScriptProperties();
  let url = props.getProperty('PYTHON_SERVER_URL');
  if (!url && typeof SYNCED_CLOUD_RUN_URL === 'string' && SYNCED_CLOUD_RUN_URL.trim()) {
    url = SYNCED_CLOUD_RUN_URL.trim().replace(/\/+$/, '');
    props.setProperty('PYTHON_SERVER_URL', url);
  }
  return url ? url.trim().replace(/\/+$/, '') : '';
}

function getPythonServerUrl() {
  return getPythonServerUrl_();
}

function setPythonServerUrl(url) {
  try {
    const cleaned = (url || '').trim().replace(/\/+$/, '');
    const props = PropertiesService.getScriptProperties();
    if (!cleaned) {
      props.deleteProperty('PYTHON_SERVER_URL');
      return { success: true, url: '' };
    }
    props.setProperty('PYTHON_SERVER_URL', cleaned);
    return { success: true, url: cleaned };
  } catch (err) {
    return { success: false, error: err && err.message ? err.message : String(err) };
  }
}

function connectPythonServer() {
  const baseUrl = getPythonServerUrl_();
  const startedAt = Date.now();

  if (!baseUrl) {
    return {
      connected: false,
      status: 'unconfigured',
      message: 'PYTHON_SERVER_URL 스크립트 속성이 설정되지 않았습니다.',
      latencyMs: 0
    };
  }

  try {
    const endpoint = baseUrl + '/health';
    const res = UrlFetchApp.fetch(endpoint, {
      method: 'get',
      muteHttpExceptions: true,
      followRedirects: true
    });
    const code = res.getResponseCode();
    const latencyMs = Date.now() - startedAt;
    const isOk = code >= 200 && code < 300;

    return {
      connected: isOk,
      status: isOk ? 'connected' : 'error',
      httpStatus: code,
      message: isOk ? 'Python 서버 연결됨' : '응답 코드 ' + code,
      latencyMs: latencyMs
    };
  } catch (err) {
    return {
      connected: false,
      status: 'unreachable',
      message: err && err.message ? err.message : 'Python 서버 연결 실패',
      latencyMs: Date.now() - startedAt
    };
  }
}

function disconnectPythonServer() {
  return {
    connected: false,
    status: 'disconnected',
    message: 'Python 서버 연결이 끊어졌습니다.',
    latencyMs: 0
  };
}

function fetchGraphPresetsFromBackend() {
  const baseUrl = getPythonServerUrl_();
  if (!baseUrl) {
    return { success: false, error: 'PYTHON_SERVER_URL 스크립트 속성이 설정되지 않았습니다.' };
  }
  try {
    const res = UrlFetchApp.fetch(baseUrl + '/graph/presets', {
      method: 'get',
      muteHttpExceptions: true,
      followRedirects: true
    });
    const code = res.getResponseCode();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(res.getContentText()) };
    }
    return { success: false, error: 'HTTP ' + code + ': ' + res.getContentText() };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + (err && err.message ? err.message : String(err)) };
  }
}

function generateGraphFromBackend(nodeCount) {
  const baseUrl = getPythonServerUrl_();
  if (!baseUrl) {
    return { success: false, error: 'PYTHON_SERVER_URL 스크립트 속성이 설정되지 않았습니다.' };
  }
  try {
    const res = UrlFetchApp.fetch(baseUrl + '/graph/generate', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ node_count: nodeCount || 7 }),
      muteHttpExceptions: true,
      followRedirects: true
    });
    const code = res.getResponseCode();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(res.getContentText()) };
    }
    return { success: false, error: 'HTTP ' + code + ': ' + res.getContentText() };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + (err && err.message ? err.message : String(err)) };
  }
}

function solveDijkstraFromBackend(requestPayload) {
  const baseUrl = getPythonServerUrl_();
  if (!baseUrl) {
    return { success: false, error: 'PYTHON_SERVER_URL 스크립트 속성이 설정되지 않았습니다.' };
  }
  if (!requestPayload || (!requestPayload.nodes && !requestPayload.preset_id)) {
    return { success: false, error: '탐색할 그래프 데이터가 없습니다.' };
  }
  try {
    const res = UrlFetchApp.fetch(baseUrl + '/dijkstra/solve', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(requestPayload),
      muteHttpExceptions: true,
      followRedirects: true
    });
    const code = res.getResponseCode();
    const text = res.getContentText();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(text) };
    }
    return { success: false, error: 'Backend HTTP ' + code + ': ' + text };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + (err && err.message ? err.message : String(err)) };
  }
}
