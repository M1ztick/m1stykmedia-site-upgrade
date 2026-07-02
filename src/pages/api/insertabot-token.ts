// src/pages/api/insertabot-token.ts
//
// Mints a short-lived, single-use, HMAC-signed "ephemeral token" that proves
// to the Insertabot Worker (https://insertabot.io) that this request came
// from a trusted server holding the real API key — without ever sending the
// API key itself to the browser.
//
// This is the non-WordPress equivalent of insertabot's `rest.php`
// (`GET /wp-json/insertabot/v1/widget-token`). The token format and signing
// scheme exactly match what `handleWidgetTokenExchange()` in the Insertabot
// Worker (`worker/src/index.ts`) expects for the "v1" (legacy, no
// customer_id) token shape:
//
//   base64url( "<unix_ts>:<16-hex nonce>:<hmac_sha256_hex(ts:nonce, api_key)>" )
//
// The browser never sees INSERTABOT_API_KEY. It only ever receives this
// ephemeral token, which:
//   - expires in 5 minutes (WIDGET_TOKEN_TTL, matched to the Worker's TTL)
//   - can only be redeemed once (the Worker tracks nonces in KV and rejects
//     replays)
//   - is useless without the real API key, since forging a valid HMAC
//     requires knowing the secret
//
// The secret itself lives only in a Cloudflare Pages secret
// (`wrangler pages secret put INSERTABOT_API_KEY`), read here via the
// Cloudflare Workers runtime `env` import — the officially supported way to
// access bindings/vars from a custom route under @astrojs/cloudflare v13+
// (Astro v6 removed `Astro.locals.runtime.env` in favor of this).
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';

export const prerender = false;

// How long an ephemeral token remains valid, in seconds. Must be <= the
// Insertabot Worker's own WIDGET_TOKEN_TTL (currently 300s / 5 min) or every
// token minted here will already look expired to the Worker.
const TOKEN_TTL_SECONDS = 300;

/**
 * Base64url-encode a UTF-8 string (RFC 4648 §5, no padding).
 * Mirrors the decode side implemented in the Insertabot Worker.
 */
function base64urlEncode(input: string): string {
  const base64 = btoa(input);
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/** Generate a random 16-hex-character nonce (8 random bytes). */
function generateNonce(): string {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/** HMAC-SHA256 over `message` using `secret`, returned as lowercase hex. */
async function hmacSha256Hex(message: string, secret: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(message));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

const NO_STORE_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
} as const;

export const GET: APIRoute = async () => {
  const apiKey = (env as Record<string, string | undefined>).INSERTABOT_API_KEY;

  if (!apiKey) {
    // Widget is simply not configured yet (e.g. secret not set in this
    // environment). Fail closed and quietly — the client-side bridge script
    // treats any non-200 as "don't show the widget" rather than erroring
    // loudly in front of visitors.
    return new Response(
      JSON.stringify({ error: 'Widget not configured' }),
      { status: 503, headers: NO_STORE_HEADERS },
    );
  }

  const timestamp = Math.floor(Date.now() / 1000);
  const nonce = generateNonce();
  const payload = `${timestamp}:${nonce}`;
  const hmac = await hmacSha256Hex(payload, apiKey);
  const rawToken = `${payload}:${hmac}`;
  const token = base64urlEncode(rawToken);

  return new Response(
    JSON.stringify({ token, expires_at: timestamp + TOKEN_TTL_SECONDS }),
    { status: 200, headers: NO_STORE_HEADERS },
  );
};
