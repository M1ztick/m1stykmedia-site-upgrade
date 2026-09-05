#!/usr/bin/env node
/**
 * Audit dispatch article dates against the WordPress export.
 *
 * Usage:
 *   node scripts/audit-dispatch-dates.mjs
 *
 * Outputs:
 *   scripts/dispatch-date-audit.csv
 *   scripts/dispatch-date-audit.json
 *   scripts/dispatch-date-audit-unmatched.json
 */

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, '..');

const WP_XML_PATH = resolve(repoRoot, 'mistykmedia.WordPress.2026-06-03.xml');
const DISPATCH_DIR = resolve(repoRoot, 'src/content/dispatch');

// ---------- Helpers ----------

function cleanTitle(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function parseFrontmatter(content) {
  const match = content.match(/^---[\s\S]*?\n---/);
  if (!match) return {};
  const lines = match[0].replace(/---/g, '').trim().split('\n');
  const fm = {};
  let key = null;
  for (let line of lines) {
    if (line.startsWith('- ')) {
      if (key && !fm[key]) fm[key] = [];
      if (key) fm[key].push(line.replace('- ', '').trim().replace(/^["']|["']$/g, ''));
      continue;
    }
    const colonIndex = line.indexOf(':');
    if (colonIndex === -1) continue;
    key = line.slice(0, colonIndex).trim();
    let value = line.slice(colonIndex + 1).trim();
    // Remove surrounding quotes
    value = value.replace(/^["']|["']$/g, '');
    fm[key] = value;
  }
  return fm;
}

function extractWordPressItems(xml) {
  const items = [];
  const itemRegex = /<item>[\s\S]*?<\/item>/g;
  const titleRegex = /<title><!\[CDATA\[(.*?)\]\]><\/title>/;
  const dateRegex = /<wp:post_date><!\[CDATA\[(.*?)\]\]><\/wp:post_date>/;
  const statusRegex = /<wp:status><!\[CDATA\[(.*?)\]\]><\/wp:status>/;
  const typeRegex = /<wp:post_type><!\[CDATA\[(.*?)\]\]><\/wp:post_type>/;

  let match;
  while ((match = itemRegex.exec(xml)) !== null) {
    const itemXml = match[0];
    const type = (itemXml.match(typeRegex)?.[1] || '').toLowerCase();
    if (type !== 'post') continue;

    const title = itemXml.match(titleRegex)?.[1]?.trim() || '';
    const wpDate = itemXml.match(dateRegex)?.[1]?.trim() || '';
    const status = itemXml.match(statusRegex)?.[1]?.toLowerCase() || '';

    if (status === 'trash') continue;
    if (!title || !wpDate) continue;

    items.push({ title, wpDate: wpDate.slice(0, 10) });
  }
  return items;
}

function levenshtein(a, b) {
  const matrix = Array.from({ length: a.length + 1 }, (_, i) =>
    Array.from({ length: b.length + 1 }, (_, j) => (i === 0 ? j : j === 0 ? i : 0))
  );
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      matrix[i][j] =
        a[i - 1] === b[j - 1]
          ? matrix[i - 1][j - 1]
          : Math.min(
              matrix[i - 1][j] + 1,
              matrix[i][j - 1] + 1,
              matrix[i - 1][j - 1] + 1
            );
    }
  }
  return matrix[a.length][b.length];
}

function findBestMatch(mdTitle, wpItems) {
  const target = cleanTitle(mdTitle);
  let best = null;
  let bestScore = Infinity;

  for (const wp of wpItems) {
    const candidate = cleanTitle(wp.title);
    if (!candidate) continue;

    // Exact clean match
    if (candidate === target) {
      return { wpTitle: wp.title, wpDate: wp.wpDate, score: 0 };
    }

    const dist = levenshtein(target, candidate);
    const maxLen = Math.max(target.length, candidate.length);
    const normalized = maxLen > 0 ? dist / maxLen : 1;

    if (normalized < bestScore) {
      bestScore = normalized;
      best = { wpTitle: wp.title, wpDate: wp.wpDate, score: normalized };
    }
  }

  // Only accept fuzzy matches below a threshold
  if (bestScore > 0.45) return null;
  return best;
}

// ---------- Main ----------

const xml = readFileSync(WP_XML_PATH, 'utf-8');
const wpItems = extractWordPressItems(xml);

const mdFiles = readdirSync(DISPATCH_DIR).filter((f) => f.endsWith('.md'));

const rows = [];
const unmatchedMd = [];
let matched = 0;
let mismatched = 0;

for (const filename of mdFiles) {
  const content = readFileSync(resolve(DISPATCH_DIR, filename), 'utf-8');
  const fm = parseFrontmatter(content);
  const mdTitle = fm.title || '';
  const mdDate = fm.pubDate || '';

  const match = findBestMatch(mdTitle, wpItems);

  if (!match) {
    unmatchedMd.push({ filename, mdTitle, mdDate });
    continue;
  }

  matched++;
  const dateDiffers = match.wpDate !== String(mdDate).slice(0, 10);
  if (dateDiffers) mismatched++;

  rows.push({
    filename,
    mdTitle: mdTitle.replace(/"/g, '""'),
    wpTitle: match.wpTitle.replace(/"/g, '""'),
    currentPubDate: mdDate,
    wordpressDate: match.wpDate,
    dateDiffers,
    suggestedPubDate: match.wpDate,
    matchConfidence: match.score === 0 ? 'exact' : `${(1 - match.score).toFixed(2)}`,
  });
}

// ---------- Output CSV ----------

const csvHeader = [
  'filename',
  'mdTitle',
  'wpTitle',
  'currentPubDate',
  'wordpressDate',
  'dateDiffers',
  'suggestedPubDate',
  'matchConfidence',
].join(',');

const csvRows = rows.map((r) =>
  [
    r.filename,
    `"${r.mdTitle}"`,
    `"${r.wpTitle}"`,
    r.currentPubDate,
    r.wordpressDate,
    r.dateDiffers,
    r.suggestedPubDate,
    r.matchConfidence,
  ].join(',')
);

const csvContent = [csvHeader, ...csvRows].join('\n');
writeFileSync(resolve(__dirname, 'dispatch-date-audit.csv'), csvContent);

// ---------- Output JSON ----------

writeFileSync(
  resolve(__dirname, 'dispatch-date-audit.json'),
  JSON.stringify(
    {
      summary: {
        totalMdFiles: mdFiles.length,
        matchedWordPressPosts: matched,
        dateMismatches: mismatched,
        unmatchedMdFiles: unmatchedMd.length,
      },
      matches: rows,
      unmatched: unmatchedMd,
    },
    null,
    2
  )
);

writeFileSync(
  resolve(__dirname, 'dispatch-date-audit-unmatched.json'),
  JSON.stringify(unmatchedMd, null, 2)
);

console.log('Dispatch date audit complete.');
console.log(`  Total Markdown files: ${mdFiles.length}`);
console.log(`  Matched to WordPress: ${matched}`);
console.log(`  Date mismatches:      ${mismatched}`);
console.log(`  Unmatched files:      ${unmatchedMd.length}`);
console.log('');
console.log('Outputs:');
console.log('  scripts/dispatch-date-audit.csv');
console.log('  scripts/dispatch-date-audit.json');
console.log('  scripts/dispatch-date-audit-unmatched.json');
