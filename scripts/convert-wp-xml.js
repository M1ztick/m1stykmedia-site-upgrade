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
  
  // The Archive (music)
  'original-music': 'archive',
  'covers': 'archive',
  'new-music': 'archive',
  'new-hip-hop': 'archive',
  'underground-hip-hop': 'archive',
  'hip-hop': 'archive',
  'grunge': 'archive',
  'karaoke': 'archive',
  'leonard-cohen': 'archive',
  'multi-genre': 'archive',
  
  // The Current (AI/tech, consciousness, esoteric)
  'artificial-intelligence': 'current',
  'ai': 'current',
  'chat-gpt': 'current',
  'chatgpt': 'current',
  'claude': 'current',
  'anthropic': 'current',
  'deep-mind': 'current',
  'gen-ai': 'current',
  'technology': 'current',
  'chatbot': 'current',
  'chatbots': 'current',
  'cloudflare': 'current',
  'esotericism': 'current',
  'mysticism': 'current',
  'spirituality': 'current',
  'spirituality-religion': 'current',
  'hinduism': 'current',
  
  // The Workbench (projects, code, tools)
  'insertabot': 'workbench',
  'custom-chatbots': 'workbench',
  'developers': 'workbench',
  'innovation': 'workbench',
  'online-services': 'workbench',
  'online-advertising': 'workbench',
};

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
  let archiveCount = 0;
  let currentCount = 0;
  let workbenchCount = 0;
  
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
    const outputDir = path.join(__dirname, '..', 'src', 'content', section);
    const outputPath = path.join(outputDir, `${slug}.md`);
    
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
    
    fs.writeFileSync(outputPath, fileContent);
    
    switch (section) {
      case 'dispatch': dispatchCount++; break;
      case 'archive': archiveCount++; break;
      case 'current': currentCount++; break;
      case 'workbench': workbenchCount++; break;
    }
    
    console.log(`✓ [${section}] ${title}`);
  }
  
  console.log('\n--- Conversion Complete ---');
  console.log(`Dispatch (politics/writing): ${dispatchCount}`);
  console.log(`Archive (music): ${archiveCount}`);
  console.log(`Current (AI/tech/esoteric): ${currentCount}`);
  console.log(`Workbench (projects): ${workbenchCount}`);
  console.log(`\nTotal: ${dispatchCount + archiveCount + currentCount + workbenchCount} posts converted`);
}

convertXML().catch(err => {
  console.error('Conversion failed:', err);
  process.exit(1);
});
