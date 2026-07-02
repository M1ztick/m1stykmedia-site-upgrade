import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

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

const journeyCollection = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/journey' }),
  schema: articleSchema,
});

export const collections = {
  'dispatch': dispatchCollection,
  'journey': journeyCollection,
};
