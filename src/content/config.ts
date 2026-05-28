import { defineCollection, z } from 'astro:content';

const dispatchCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    updatedDate: z.date().optional(),
    tags: z.array(z.string()).optional(),
    category: z.enum(['politics', 'investigation', 'analysis', 'essay']).optional(),
    featured: z.boolean().default(false),
  }),
});

const archiveCollection = defineCollection({
  type: 'data',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    releaseDate: z.date(),
    genre: z.array(z.string()).optional(),
    url: z.string().url(),
    coverImage: z.string().optional(),
    duration: z.string().optional(),
  }),
});

const workbenchCollection = defineCollection({
  type: 'data',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    status: z.enum(['active', 'archived', 'concept']),
    tech: z.array(z.string()),
    repository: z.string().url().optional(),
    demo: z.string().url().optional(),
    thumbnail: z.string().optional(),
    startedDate: z.date(),
    lastUpdated: z.date().optional(),
  }),
});

export const collections = {
  'dispatch': dispatchCollection,
  'archive': archiveCollection,
  'workbench': workbenchCollection,
};