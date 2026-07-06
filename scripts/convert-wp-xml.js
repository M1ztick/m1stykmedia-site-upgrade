/**
 * WordPress XML to Astro Markdown Converter
 * 
 * Usage: node scripts/convert-wp-xml.js
 * Requires: npm install fast-xml-parser
 */

import { XMLParser } from 'fast-xml-parser';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// WordPress category → Astro section mapping
const CATEGORY_MAP = {
  // The Dispatch (politics, investigation, analysis, essay)
  'politics': 'dispatch',
  'op-ed': 'dispatch',
  'op-ed-politics': 'dispatch',
  'op-ed-politics-2': 'dispatch',
  'breaking-news': 'dispatch',
  'news': 'dispatch',
  'world-news': 'dispatch',
  'international-news': 'dispatch',
  'investigation': 'dispatch',
  'analysis': 'dispatch',
  'essay': 'dispatch',
  'war-crimes': 'dispatch',
  'government-overreach': 'dispatch',
  'bureaucratic-corruption': 'dispatch',
  
  // AI/tech posts also live in Dispatch now
  'artificial-intelligence': 'dispatch',
  'ai': 'dispatch',
  'chat-gpt': 'dispatch',
  'chatgpt': 'dispatch',
  'claude': 'dispatch',
  'anthropic': 'dispatch',
  'deep-mind': 'dispatch',
  'gen-ai': 'dispatch',
  'technology': 'dispatch',
  'chatbot': 'dispatch',
  'chatbots': 'dispatch',
  'cloudflare': 'dispatch',
  'insertabot': 'dispatch',
  'custom-chatbots': 'dispatch',
  'developers': 'dispatch',
  'innovation': 'dispatch',
  'online-services': 'dispatch',
  'online-advertising': 'dispatch',

  // The Inner Journey (consciousness, esotericism, spirituality)
  'esotericism': 'journey',
  'mysticism': 'journey',
  'spirituality': 'journey',
  'spirituality-religion': 'journey',
  'hinduism': 'journey',
  'religion': 'journey',
};

// Note: music-related posts (original-music, hip-hop, etc.) are no longer
// imported into a dedicated section. If re-running this script against new
// WordPress content that includes music posts, either skip those items or
// route them to 'dispatch'/'journey' manually — there is no music collection
// in the current site structure. See /links for music/dev outbound links.

function stripCDATA(str) {
  if (!str) return '';
  if (typeof str === 'object' && str.__cdata !== undefined) return String(str.__cdata);
  if (typeof str !== 'string') return String(str);
  return str
    .replace(/<!\[CDATA\[/g, '')
    .replace(/\]\]>/g, '');
}

function cleanHTML(html) {
  if (!html) return '';
  return html
    .replace(/<p>/g, '\n\n')
    .replace(/<\/p>/g, '')
    .replace(/<br\s*\/?>/g, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#8217;/g, "'")
    .replace(/&#8220;/g, '"')
    .replace(/&#8221;/g, '"')
    .replace(/&#8211;/g, '-')
    .replace(/&#8212;/g, '--')
    .replace(/&#8230;/g, '...')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function slugify(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

function determineSection(categories, tags) {
  const allTerms = [...(categories || []), ...(tags || [])]
    .map(t => typeof t === 'string' ? t.toLowerCase() : t?.toLowerCase())
    .filter(Boolean);
  
  for (const term of allTerms) {
    if (CATEGORY_MAP[term]) return CATEGORY_MAP[term];
  }
  
  return 'dispatch'; // default
}

function determineCategory(tags) {
  const tagList = Array.isArray(tags) ? tags : tags ? [tags] : [];
  const tagStrings = tagList.map(t => typeof t === 'string' ? t.toLowerCase() : '').filter(Boolean);
  
  if (tagStrings.some(t => t.includes('politics'))) return 'politics';
  if (tagStrings.some(t => t.includes('investigation') || t.includes('coverup'))) return 'investigation';
  if (tagStrings.some(t => t.includes('analysis'))) return 'analysis';
  if (tagStrings.some(t => t.includes('essay') || t.includes('op-ed'))) return 'essay';
  
  return 'essay';
}

async function convertXML() {
  const xmlPath = path.join(__dirname, '..', 'mistykmedia.WordPress.2026-06-03.xml');
  // amazonq-ignore-next-line
  const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
  
  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: '@_',
    cdataPropName: '__cdata',
    parseTagValue: false,
  });
  
  const data = parser.parse(xmlContent);
  const items = data.rss.channel.item;
  
  console.log(`Found ${items.length} items in WordPress export`);
  
  const posts = [];
  const pages = [];
  
  for (const item of items) {
    const postType = stripCDATA(item['wp:post_type']);
    
    if (postType === 'post') {
      posts.push(item);
    } else if (postType === 'page') {
      pages.push(item);
    }
  }
  
  console.log(`Posts: ${posts.length}, Pages: ${pages.length}`);
  
  let dispatchCount = 0;
  let journeyCount = 0;
  
  // Convert posts
  for (const post of posts) {
    const title = stripCDATA(post.title);
    const content = stripCDATA(post['content:encoded'] || '');
    const excerpt = stripCDATA(post['excerpt:encoded'] || '');
    const pubDate = new Date(post.pubDate);
    const status = stripCDATA(post['wp:status']);
    
    if (status !== 'publish') {
      console.log(`Skipping draft: ${title}`);
      continue;
    }
    
    // Extract categories and tags
    const categories = [];
    const tags = [];
    
    const categoryData = post.category;
    if (categoryData) {
      const catArray = Array.isArray(categoryData) ? categoryData : [categoryData];
      for (const cat of catArray) {
        if (typeof cat === 'string') {
          if (!['uncategorized', 'blog'].includes(cat.toLowerCase())) {
            categories.push(cat);
          }
        } else if (cat['@_domain'] === 'category') {
          if (!['uncategorized', 'blog'].includes(cat['@_nicename'])) {
            categories.push(cat['@_nicename']);
          }
        } else if (cat['@_domain'] === 'post_tag') {
          tags.push(cat['@_nicename'] || cat['@_']);
        }
      }
    }
    
    const section = determineSection(categories, tags);
    const category = determineCategory(tags);
    
    // Clean and convert content
    let markdownContent = cleanHTML(content);
    
    // Build frontmatter
    const frontmatter = {
      title,
      description: excerpt || markdownContent.substring(0, 150).replace(/\n/g, ' ') + '...',
      pubDate: pubDate.toISOString().split('T')[0],
      tags: [...new Set([...categories, ...tags])].slice(0, 10),
      category,
      featured: false,
    };
    
    const slug = slugify(title) || `post-${Date.now()}`;
    const outputDir = path.resolve(__dirname, '..', 'src', 'content', section);
    const outputPath = path.resolve(outputDir, `${slug}.md`);

    if (!outputPath.startsWith(outputDir + path.sep)) {
      console.warn(`Path traversal detected, skipping: ${slug}`);
      continue;
    }

    // Ensure directory exists
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Check for duplicates
    if (fs.existsSync(outputPath)) {
      console.warn(`Duplicate slug, skipping: ${slug}`);
      continue;
    }
    
    const fileContent = `---\n${Object.entries(frontmatter)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}:\n${value.map(v => `  - ${v}`).join('\n')}`;
        }
        return `${key}: ${typeof value === 'string' && value.includes(':') ? `"${value}"` : value}`;
      })
      .join('\n')}\n---\n\n${markdownContent}`;
    
    // amazonq-ignore-next-line
    fs.writeFileSync(outputPath, fileContent);
    
    if (section === 'dispatch') dispatchCount++;
    else if (section === 'journey') journeyCount++;
    
    console.log(`✓ [${section}] ${title}`);
  }
  
  console.log('\n--- Conversion Complete ---');
  console.log(`Dispatch (politics/writing/AI/tech): ${dispatchCount}`);
  console.log(`Journey (esoteric/spiritual): ${journeyCount}`);
  console.log(`\nTotal: ${dispatchCount + journeyCount} posts converted`);
}

convertXML().catch(err => {
  console.error('Conversion failed:', err);
  process.exit(1);
});
