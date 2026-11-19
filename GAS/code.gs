/**
 * Google Apps Script Web App Controller for BFS vs DFS Maze Escape Visualizer
 * - Serves index.html via HtmlService
 * - Proxies REST API requests to FastAPI backend (server/main.py) via UrlFetchApp
 * - Stores Backend URL in PropertiesService (no hardcoded secrets/URLs)
 * - Optional benchmark logging to Google Sheets via SpreadsheetApp
 */

function doGet() {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('미로탈출 알고리즘 랩 : BFS(Queue) vs DFS(Stack)')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Script Properties에서 저장된 FastAPI 백엔드 URL을 조회합니다.
 * 미설정 시 Config.gs에 자동 등록된 Cloud Run URL을 기본값으로 반환합니다.
 * @returns {string}
 */
function getApiBaseUrl() {
  var propUrl = PropertiesService.getScriptProperties().getProperty('API_BASE_URL');
  if (propUrl) {
    return propUrl;
  }
  return (typeof CONFIG !== 'undefined' && CONFIG.DEFAULT_API_BASE_URL) ? CONFIG.DEFAULT_API_BASE_URL : '';
}

/**
 * Script Properties에 FastAPI 백엔드 URL을 저장합니다.
 * @param {string} url
 * @returns {object}
 */
function setApiBaseUrl(url) {
  try {
    var cleaned = (url || '').trim().replace(/\/+$/, '');
    PropertiesService.getScriptProperties().setProperty('API_BASE_URL', cleaned);
    return { success: true, url: cleaned };
  } catch (err) {
    return { success: false, error: err.toString() };
  }
}

/**
 * 내부 URL 해석 헬퍼 (인자 우선, 없으면 Script Properties 사용)
 * @param {string} backendUrl
 * @returns {string}
 */
function resolveBaseUrl_(backendUrl) {
  var raw = (backendUrl || getApiBaseUrl() || '').trim();
  return raw.replace(/\/+$/, '');
}

/**
 * FastAPI 백엔드 헬스체크 (GET /health)
 * @param {string} backendUrl
 * @returns {object}
 */
function checkBackendHealth(backendUrl) {
  try {
    var baseUrl = resolveBaseUrl_(backendUrl);
    if (!baseUrl) {
      return { connected: false, message: 'API_BASE_URL 미설정 (로컬 시뮬레이션 모드 사용 가능)' };
    }
    var response = UrlFetchApp.fetch(baseUrl + '/health', {
      method: 'get',
      muteHttpExceptions: true
    });
    var code = response.getResponseCode();
    if (code >= 200 && code < 300) {
      return {
        connected: true,
        url: baseUrl,
        data: JSON.parse(response.getContentText()),
        message: 'FastAPI 백엔드 정상 연결 (HTTP ' + code + ')'
      };
    }
    return { connected: false, message: 'HTTP 오류 (' + code + ')' };
  } catch (err) {
    return { connected: false, message: '연결 실패: ' + err.toString() };
  }
}

/**
 * 백엔드 프리셋 미로 목록 조회 (GET /maze/presets)
 * @param {string} backendUrl
 * @returns {object}
 */
function fetchMazePresetsFromBackend(backendUrl) {
  try {
    var baseUrl = resolveBaseUrl_(backendUrl);
    if (!baseUrl) {
      return { success: false, error: '백엔드 URL이 설정되지 않았습니다.' };
    }
    var response = UrlFetchApp.fetch(baseUrl + '/maze/presets', {
      method: 'get',
      muteHttpExceptions: true
    });
    var code = response.getResponseCode();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(response.getContentText()) };
    }
    return { success: false, error: 'HTTP ' + code + ': ' + response.getContentText() };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + err.toString() };
  }
}

/**
 * 백엔드 랜덤 다중경로 미로 생성 (POST /maze/generate)
 * @param {string} backendUrl
 * @param {number} rows
 * @param {number} cols
 * @returns {object}
 */
function generateMazeFromBackend(backendUrl, rows, cols) {
  try {
    var baseUrl = resolveBaseUrl_(backendUrl);
    if (!baseUrl) {
      return { success: false, error: '백엔드 URL이 설정되지 않았습니다.' };
    }
    var payload = {
      rows: rows || 11,
      cols: cols || 11,
      braid_ratio: 0.24
    };
    var response = UrlFetchApp.fetch(baseUrl + '/maze/generate', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
    var code = response.getResponseCode();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(response.getContentText()) };
    }
    return { success: false, error: 'HTTP ' + code + ': ' + response.getContentText() };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + err.toString() };
  }
}

/**
 * BFS vs DFS 미로 탐색 실행 및 단계별 히스토그램 스냅샷 수신 (POST /solve)
 * @param {string} backendUrl
 * @param {object} requestPayload - { preset_id?, maze_name?, grid?, start?, goal? }
 * @returns {object}
 */
function solveMazeFromBackend(backendUrl, requestPayload) {
  try {
    var baseUrl = resolveBaseUrl_(backendUrl);
    if (!baseUrl) {
      return { success: false, error: '백엔드 URL이 설정되지 않았습니다.' };
    }
    var response = UrlFetchApp.fetch(baseUrl + '/solve', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(requestPayload || { preset_id: 'classic_branch' }),
      muteHttpExceptions: true
    });
    var code = response.getResponseCode();
    var text = response.getContentText();
    if (code >= 200 && code < 300) {
      return { success: true, data: JSON.parse(text) };
    }
    return { success: false, error: 'Backend HTTP ' + code + ': ' + text };
  } catch (err) {
    return { success: false, error: 'GAS Proxy Error: ' + err.toString() };
  }
}

/**
 * BFS vs DFS 비교 결과를 연결된 Google Spreadsheet에 기록합니다.
 * @param {object} record
 * @returns {object}
 */
function logBenchmarkToSheet(record) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) {
      return {
        success: false,
        error: '독립 실행형(Standalone) 웹앱에는 연결된 스프레드시트가 없습니다.'
      };
    }
    var sheet = ss.getActiveSheet();
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        '기록시각',
        '미로명',
        '크기',
        'BFS_경로길이',
        'BFS_방문칸수',
        'BFS_최대Queue',
        'BFS_소요시간(ms)',
        'DFS_경로길이',
        'DFS_방문칸수',
        'DFS_최대Stack',
        'DFS_백트래킹',
        'DFS_소요시간(ms)'
      ]);
    }
    sheet.appendRow([
      new Date(),
      record.mazeName || 'Unknown',
      record.size || '',
      record.bfsPath || 0,
      record.bfsVisited || 0,
      record.bfsMaxQueue || 0,
      record.bfsTimeMs || 0,
      record.dfsPath || 0,
      record.dfsVisited || 0,
      record.dfsMaxStack || 0,
      record.dfsBacktracks || 0,
      record.dfsTimeMs || 0
    ]);
    return { success: true, message: 'Google Sheets에 비교 결과가 저장되었습니다.' };
  } catch (err) {
    return { success: false, error: 'Sheets 저장 실패: ' + err.toString() };
  }
}
