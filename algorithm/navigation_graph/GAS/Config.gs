/**
 * gas-url-sync 스킬로 자동 동기화된 Cloud Run URL
 * 런타임에서는 PropertiesService('PYTHON_SERVER_URL')이 최우선이며,
 * 최초 미설정 상태일 때 code.gs의 getPythonServerUrl_()가 본 URL을 PropertiesService에 1회 자동 등록합니다.
 */
var SYNCED_CLOUD_RUN_URL = 'https://navigation-graph-kftopmxfma-ew.a.run.app';
