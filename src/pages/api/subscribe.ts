// src/pages/api/subscribe.ts
//
// Backs the "Stay in the Loop" form in ArticleLayout.astro. Writes to the
// `mistykmedia-subscribers` D1 database via the SUBSCRIBERS_DB binding
// declared in wrangler.jsonc.
//
// Bindings are read from the Cloudflare Workers runtime `env` import — the
// supported way to reach them from a custom route under @astrojs/cloudflare
// v13+ (Astro v6 removed `Astro.locals.runtime.env`). Same pattern as
// insertabot-token.ts.
import type { APIRoute } from 'astro';
import { env } from 'cloudflare:workers';

export const prerender = false;

const JSON_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-store',
} as const;

/**
 * Deliberately loose: the goal is to reject obvious junk, not to adjudicate
 * RFC 5322. Anything that survives this still has to bounce a real email.
 */
const EMAIL_RE = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/;
const MAX_EMAIL_LENGTH = 254; // RFC 5321 limit on a forward-path

function json(body: unknown, status: number): Response {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}

export const POST: APIRoute = async ({ request }) => {
  const db = (env as { SUBSCRIBERS_DB?: D1Database }).SUBSCRIBERS_DB;

  if (!db) {
    // Binding missing (e.g. running `astro dev` without the Cloudflare
    // runtime, or the binding was dropped from wrangler.jsonc).
    return json({ error: 'Subscriptions are not configured' }, 503);
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return json({ error: 'Expected a JSON body' }, 400);
  }

  const { email, source } = (payload ?? {}) as { email?: unknown; source?: unknown };

  if (typeof email !== 'string') {
    return json({ error: 'Email is required' }, 400);
  }

  const normalized = email.trim().toLowerCase();

  if (normalized.length > MAX_EMAIL_LENGTH || !EMAIL_RE.test(normalized)) {
    return json({ error: 'That email address does not look right' }, 400);
  }

  // Where the signup came from, for attribution. Trust the client's hint only
  // as a fallback to the Referer, and cap it so a crafted body can't stuff the
  // column.
  const referer = request.headers.get('referer');
  const rawSource = typeof source === 'string' && source ? source : referer;
  const trackedSource = rawSource ? rawSource.slice(0, 512) : null;

  try {
    // Re-subscribing is idempotent: an existing row is reactivated rather than
    // duplicated (the UNIQUE index on email is what makes the upsert fire),
    // and created_at is preserved so we keep the original signup date.
    await db
      .prepare(
        `INSERT INTO subscribers (email, status, source)
         VALUES (?1, 'active', ?2)
         ON CONFLICT (email) DO UPDATE SET
           status     = 'active',
           source     = COALESCE(subscribers.source, excluded.source),
           updated_at = datetime('now')`,
      )
      .bind(normalized, trackedSource)
      .run();
  } catch (err) {
    console.error('Subscribe failed', err);
    return json({ error: 'Could not save your subscription' }, 500);
  }

  // Always the same response whether the address was new or already on the
  // list — otherwise this endpoint doubles as an oracle for "is this person
  // subscribed?".
  return json({ ok: true }, 200);
};
