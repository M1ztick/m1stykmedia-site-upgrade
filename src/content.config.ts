import { defineCollection, z } from 'astro:content';
import { file, glob } from 'astro/loaders';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.date(),
  updatedDate: z.date().optional(),
  tags: z.array(z.string()).optional(),
  category: z.string().optional(),
  featured: z.boolean().default(false),
});

const dispatchCollection = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/dispatch' }),
  schema: articleSchema,
});

const frequencyCollection = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/frequency' }),
  schema: articleSchema,
});

const currentCollection = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/current' }),
  schema: articleSchema,
});

const workbenchCollection = defineCollection({
  loader: file('./src/content/workbench/projects.json'),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    status: z.enum(['active', 'archived', 'concept']),
    tech: z.array(z.string()),
    repository: z.string().url().optional(),
    demo: z.string().url().optional(),
    thumbnail: z.string().optional(),
    startedDate: z.string(),
    lastUpdated: z.string().optional(),
  }),
});

export const collections = {
  'dispatch': dispatchCollection,
  'frequency': frequencyCollection,
  'current': currentCollection,
  'workbench': workbenchCollection,
};
