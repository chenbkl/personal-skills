// ==UserScript==
// @name         CrapAPI 接口文档 · 过期自动重登
// @namespace    hisunpay.autotest.crapapi
// @version      1.0.0
// @description  CrapAPI 会话过期后自动登录，并进入 deb-api-rest 项目级接口搜索页。凭据由生成器从 .env 注入，请勿提交成品脚本。
// @match        https://test.95598pay.top:29943/crapapi/*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  const USERNAME = __CRAPAPI_USERNAME_JSON__;
  const PASSWORD = __CRAPAPI_PASSWORD_JSON__;

  const LOGIN_PATH = '/crapapi/loginOrRegister.do';
  const HOME_PATH = '/crapapi/home.do';
  const ADMIN_PATH = '/crapapi/admin.do';
  const LOGIN_HASH = '#/login';
  const TARGET_URL = 'https://test.95598pay.top:29943/crapapi/admin.do#/user/interface/list?pageName=%E6%8E%A5%E5%8F%A3&dataType=interface&menu_a=menu-project&menu_b=menu_interface&projectName=%E7%94%B5e%E5%AE%9D%E7%A7%BB%E5%8A%A8%E7%AB%AF%E6%8E%A5%E5%8F%A3%E6%9C%8D%E5%8A%A1%EF%BC%88deb-api-rest%EF%BC%89&projectId=156939461626807001127&moduleId=';
  const ACCOUNT_PLACEHOLDER = '用户名（6-20位）';
  const PASSWORD_PLACEHOLDER = '密码（不少于6位）';
  const LOGIN_BUTTON_TEXT = '登入';
  const MAX_ATTEMPTS = 3;
  const ATTEMPT_WINDOW_MS = 60000;
  const SUBMIT_LOCK_MS = 5000;
  const STORAGE_KEY = 'crapapi-auto-login-state-v1';
  const RETURN_PENDING_KEY = 'crapapi-auto-login-return-pending-v1';
  const TAG = '[crapapi-auto-login]';
  const RELOGIN_KEYWORDS = ['过期', '重新登录', '重新登陆', '失效', '超时', '会话', '未登录', '登录状态'];
  const LOGIN_ERROR_KEYWORDS = ['密码', '错误', '账号', '不存在', '禁用', '锁定', '失败'];

  let submittedForVisit = false;
  let lastLoginFormPresent = false;
  let aborted = false;

  function log(...args) { console.log(TAG, ...args); }
  function warn(...args) { console.warn(TAG, ...args); }

  function loadPersistentState() {
    try {
      const value = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '{}');
      return {
        attempts: Array.isArray(value.attempts) ? value.attempts : [],
        submitLockUntil: Number(value.submitLockUntil) || 0,
      };
    } catch (_) {
      return { attempts: [], submitLockUntil: 0 };
    }
  }

  function savePersistentState(value) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  }

  function loginFormPresent() {
    return !!document.querySelector('input[placeholder="' + ACCOUNT_PLACEHOLDER + '"]')
      && !!document.querySelector('input[placeholder="' + PASSWORD_PLACEHOLDER + '"]');
  }

  function setNativeValue(element, value) {
    const proto = Object.getPrototypeOf(element);
    const descriptor = Object.getOwnPropertyDescriptor(proto, 'value')
      || Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
    if (descriptor && descriptor.set) descriptor.set.call(element, value);
    else element.value = value;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function findLoginButton() {
    for (const button of document.querySelectorAll('button')) {
      if ((button.textContent || '').trim().startsWith(LOGIN_BUTTON_TEXT)) return button;
    }
    return null;
  }

  function detectLoginError() {
    const messages = document.querySelectorAll('.el-message, .el-message-box, .alert, .form-error, .help-block, [role="alert"]');
    for (const element of messages) {
      const text = (element.textContent || '').trim();
      const isLoginError = text && LOGIN_ERROR_KEYWORDS.some(function (keyword) { return text.includes(keyword); });
      const isSessionExpiry = text && RELOGIN_KEYWORDS.some(function (keyword) { return text.includes(keyword); });
      if (isLoginError && !isSessionExpiry) return text;
    }
    return null;
  }

  function dismissReloginPopup() {
    if (aborted) return;
    for (const box of document.querySelectorAll('.el-message-box')) {
      const text = (box.textContent || '').trim();
      if (!RELOGIN_KEYWORDS.some(function (keyword) { return text.includes(keyword); })) continue;
      const button = box.querySelector('.el-message-box__btns .el-button--primary')
        || box.querySelector('.el-message-box__btns button');
      if (button) {
        sessionStorage.setItem(RETURN_PENDING_KEY, '1');
        button.click();
        return;
      }
    }
  }

  function showManualBanner(reason) {
    if (document.getElementById('crapapi-auto-login-banner')) return;
    const banner = document.createElement('div');
    banner.id = 'crapapi-auto-login-banner';
    banner.textContent = TAG + ' 自动登录已停止，请手动处理。原因：' + reason;
    banner.style.cssText = [
      'position:fixed', 'top:0', 'left:0', 'right:0', 'z-index:99999',
      'background:#f56c6c', 'color:#fff', 'font-size:13px', 'line-height:32px',
      'text-align:center', 'padding:0 12px', 'font-family:sans-serif',
    ].join(';');
    (document.body || document.documentElement).appendChild(banner);
  }

  function removeManualBanner() {
    const banner = document.getElementById('crapapi-auto-login-banner');
    if (banner) banner.remove();
  }

  function withinRateLimit(state) {
    const now = Date.now();
    state.attempts = state.attempts.filter(function (timestamp) {
      return now - Number(timestamp) < ATTEMPT_WINDOW_MS;
    });
    return state.attempts.length < MAX_ATTEMPTS;
  }

  function fillAndSubmitLogin() {
    if (aborted || submittedForVisit || !loginFormPresent()) return;
    const error = detectLoginError();
    if (error) {
      aborted = true;
      showManualBanner(error);
      warn('检测到登录失败，停止自动重试。');
      return;
    }

    const state = loadPersistentState();
    if (Date.now() < state.submitLockUntil) return;
    if (!withinRateLimit(state)) {
      aborted = true;
      showManualBanner('一分钟内已达到最大重试次数');
      return;
    }

    const account = document.querySelector('input[placeholder="' + ACCOUNT_PLACEHOLDER + '"]');
    const password = document.querySelector('input[placeholder="' + PASSWORD_PLACEHOLDER + '"]');
    const button = findLoginButton();
    if (!account || !password || !button) return;

    setNativeValue(account, USERNAME);
    setNativeValue(password, PASSWORD);
    state.attempts.push(Date.now());
    state.submitLockUntil = Date.now() + SUBMIT_LOCK_MS;
    savePersistentState(state);
    sessionStorage.setItem(RETURN_PENDING_KEY, '1');
    submittedForVisit = true;
    setTimeout(function () {
      const currentButton = findLoginButton();
      if (currentButton) currentButton.click();
    }, 60);
  }

  function maybeNavigateToInterfaceList() {
    if (loginFormPresent()) return;
    const pending = sessionStorage.getItem(RETURN_PENDING_KEY) === '1';
    const onHome = location.pathname === HOME_PATH;
    const onPostLoginProjectList = location.pathname === ADMIN_PATH
      && location.hash.includes('/user/project/list');
    const onPostLoginRoute = pending && location.pathname === LOGIN_PATH
      && !location.hash.startsWith(LOGIN_HASH);
    if (onPostLoginRoute || onHome || onPostLoginProjectList) {
      sessionStorage.removeItem(RETURN_PENDING_KEY);
      if (location.href !== TARGET_URL) location.replace(TARGET_URL);
    }
  }

  function tick() {
    dismissReloginPopup();
    const present = loginFormPresent();
    if (present && !lastLoginFormPresent) {
      submittedForVisit = false;
      removeManualBanner();
    }
    if (!present && lastLoginFormPresent) removeManualBanner();
    lastLoginFormPresent = present;

    if (present || (location.pathname === LOGIN_PATH && location.hash.startsWith(LOGIN_HASH))) {
      fillAndSubmitLogin();
    } else {
      maybeNavigateToInterfaceList();
    }
  }

  const observer = new MutationObserver(tick);
  function boot() {
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('hashchange', tick);
    window.addEventListener('popstate', tick);
    log('已启动。');
    tick();
  }

  if (document.body) boot();
  else window.addEventListener('DOMContentLoaded', boot);
})();
