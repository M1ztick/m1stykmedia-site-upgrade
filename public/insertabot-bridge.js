/**
 * insertabot-bridge.js — Mistyk Media
 *
 * Loads the Insertabot chat widget site-wide without ever putting a raw API
 * key in the page. This is a non-WordPress port of the same two-step
 * token-exchange flow used by the official Insertabot WordPress plugin
 * (assets/widget-bridge.js), adapted to fetch its ephemeral token from this
 * site's own Cloudflare Pages Function instead of a WP REST route.
 *
 * Flow:
 *   1. GET  /api/insertabot-token          (same-origin, this site)
 *          -> { token, expires_at }         (ephemeral, HMAC-signed, 1-use)
 *   2. POST https://insertabot.io/v1/widget-token/exchange   { token }
 *          -> { session_token, expires_at } (short-lived widget session)
 *   3. Inject <script src="https://insertabot.io/widget.js"
 *              data-session-token="wt_...">  into <head>
 *
 * The real Insertabot API key never reaches the browser at any point.
 */
(function () {
  'use strict';

  var API_BASE = 'https://insertabot.io';
  var TOKEN_ENDPOINT = '/api/insertabot-token';
  var EXCHANGE_ENDPOINT = API_BASE + '/v1/widget-token/exchange';
  var SESSION_TOKEN_RE = /^wt_[0-9a-f]{48}$/;
  var WIDGET_ELEMENT_ID = 'insertabot-widget-script';

  function log(msg) {
    // Quiet by default; flip on with `window.__insertabotDebug = true` in
    // devtools if you need to troubleshoot the handshake.
    if (window.__insertabotDebug) {
      // eslint-disable-next-line no-console
      console.log('[insertabot-bridge] ' + msg);
    }
  }

  function warn(msg) {
    // eslint-disable-next-line no-console
    console.warn('[insertabot-bridge] ' + msg);
  }

  /** fetch() with an AbortController-based timeout. */
  function fetchWithTimeout(url, options, timeoutMs) {
    var controller = new AbortController();
    var timer = setTimeout(function () {
      controller.abort();
    }, timeoutMs);

    return fetch(
      url,
      Object.assign({}, options, { signal: controller.signal }),
    ).finally(function () {
      clearTimeout(timer);
    });
  }

  function isValidSessionToken(token) {
    return typeof token === 'string' && SESSION_TOKEN_RE.test(token);
  }

  function loadWidget(sessionToken) {
    if (!isValidSessionToken(sessionToken)) {
      warn('Refusing to load widget: malformed session token.');
      return;
    }
    if (document.getElementById(WIDGET_ELEMENT_ID)) {
      // Already loaded (e.g. client-side navigation re-ran this script).
      return;
    }

    var script = document.createElement('script');
    script.id = WIDGET_ELEMENT_ID;
    script.src = API_BASE + '/widget.js';
    script.async = true;
    script.setAttribute('data-session-token', sessionToken);
    script.setAttribute('data-api-base', API_BASE);
    document.head.appendChild(script);
    log('Widget loaded with session token.');
  }

  function init() {
    fetchWithTimeout(
      TOKEN_ENDPOINT + '?_=' + Date.now(),
      { credentials: 'same-origin', cache: 'no-store' },
      5000,
    )
      .then(function (res) {
        if (!res.ok) {
          throw new Error('Token endpoint returned ' + res.status);
        }
        return res.json();
      })
      .then(function (data) {
        if (!data || typeof data.token !== 'string') {
          throw new Error('Token endpoint returned an invalid payload.');
        }
        return fetchWithTimeout(
          EXCHANGE_ENDPOINT,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: data.token }),
          },
          8000,
        );
      })
      .then(function (res) {
        if (!res.ok) {
          throw new Error('Widget-token exchange returned ' + res.status);
        }
        return res.json();
      })
      .then(function (data) {
        if (!data || typeof data.session_token !== 'string') {
          throw new Error('Exchange endpoint returned an invalid payload.');
        }
        loadWidget(data.session_token);
      })
      .catch(function (err) {
        // Fail silently in production: a missing/broken chat widget should
        // never block or visually disrupt the rest of the site. Log for
        // debugging when explicitly requested.
        warn('Widget did not load: ' + (err && err.message ? err.message : err));
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
