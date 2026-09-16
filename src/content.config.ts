import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { SUBJECT_SLUGS } from './lib/dispatch';

const articleSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.date(),
  updatedDate: z.date().optional(),
  category: z.string().optional(),
  subject: z.enum(SUBJECT_SLUGS).optional(),
  tags: z.array(z.string()).optional(),
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
