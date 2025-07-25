// --- START OF FILE src/store/contentStore.ts ---
import { create } from 'zustand';

// SAGA PERSONA: Defining the many stages of the Weaver's Loom.
type LoomStatus =
  | 'idle'                // The Loom is quiet.
  | 'awaiting_spark_topic'// Awaiting the user's topic to generate sparks.
  | 'weaving_sparks'      // Ritual to generate content sparks.
  | 'sparks_revealed'     // The 5 Content Sparks are ready for the user to choose one.
  | 'crossroads_revealed' // A spark is chosen, now showing the 3 content type cards.
  
  // Social Post Path
  | 'awaiting_tone'       // Awaiting choice of writing style.
  | 'awaiting_realm'      // Awaiting choice of social platform.
  | 'awaiting_length'     // Awaiting choice of post length.
  | 'weaving_social_post' // Final ritual for the social post.
  | 'social_post_woven'   // The final social post is ready.

  // Comment Path
  | 'awaiting_echo'       // Awaiting the post to comment on.
  | 'weaving_comment'     // Ritual to generate the comment.
  | 'comment_woven'       // The final comment is ready.

  // Blog Post Path
  | 'weaving_blog'        // Ritual to generate the blog post.
  | 'blog_woven';         // The final blog post is ready.

// SAGA PERSONA: Defining the structures for the Weaver's prophecies.
interface ContentSpark { id: string; title: string; description: string; format_suggestion: string; }
interface FinalContent { [key: string]: any; }

interface ContentSagaState {
  status: LoomStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  // --- Memory of the Weaver ---
  grandStrategyData: any | null; // To hold the initial data from the main sagaStore
  tacticalInterest: string;
  sparks: ContentSpark[];
  chosenSpark: ContentSpark | null;
  chosenTone: string | null;
  chosenRealm: string | null;
  chosenLength: string | null;
  postToCommentOn: string | null;
  finalContent: FinalContent | null;

  // --- The Rites of the Loom ---
  beginWeaving: (grandStrategyData: any, tacticalInterest: string) => void;
  generateSparks: (topic: string) => Promise<void>;
  chooseSpark: (sparkId: string) => void;
  chooseContentType: (type: 'Social Post' | 'Comment' | 'Blog Post') => Promise<void>;
  chooseTone: (tone: string) => void;
  chooseRealm: (realm: string) => void;
  chooseLength: (length: string) => Promise<void>;
  submitPostToCommentOn: (post: string) => Promise<void>;
  regenerate: () => Promise<void>;
  resetLoom: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useContentStore = create<ContentSagaState>((set, get) => ({
  // --- Initial State ---
  status: 'idle', error: null, ritualPromise: null, grandStrategyData: null, tacticalInterest: '',
  sparks: [], chosenSpark: null, chosenTone: null, chosenRealm: null, 
  chosenLength: null, postToCommentOn: null, finalContent: null,

  // --- The Rites ---
  beginWeaving: (grandStrategyData, tacticalInterest) => {
    set({ status: 'awaiting_spark_topic', grandStrategyData, tacticalInterest, error: null, ritualPromise: null });
  },

  generateSparks: async (topic) => {
    // This API call doesn't exist yet, we simulate.
    const promise = new Promise(resolve => setTimeout(resolve, 3000));
    set({ status: 'weaving_sparks', error: null, ritualPromise: promise, tacticalInterest: topic });
    await promise; 
    const simulatedSparks: ContentSpark[] = Array(5).fill(0).map((_, i) => ({
      id: `spark_${i+1}`, title: `Generated Spark Title for '${topic}' ${i+1}`,
      description: 'A compelling description for this content idea.',
      format_suggestion: 'Listicle Blog Post'
    }));
    set({ status: 'sparks_revealed', sparks: simulatedSparks, ritualPromise: null });
  },

  chooseSpark: (sparkId) => {
    const chosen = get().sparks.find(s => s.id === sparkId);
    if (chosen) {
      set({ status: 'crossroads_revealed', chosenSpark: chosen });
    }
  },

  chooseContentType: async (type) => {
    if (type === 'Social Post') set({ status: 'awaiting_tone' });
    if (type === 'Comment') set({ status: 'awaiting_echo' });
    if (type === 'Blog Post') {
      const promise = new Promise(resolve => setTimeout(resolve, 3000));
      set({ status: 'weaving_blog', error: null, ritualPromise: promise });
      await promise;
      set({ status: 'blog_woven', finalContent: { title: get().chosenSpark?.title, body: "<p>Full blog post content...</p>" }, ritualPromise: null });
    }
  },

  chooseTone: (tone) => set({ status: 'awaiting_realm', chosenTone: tone }),
  chooseRealm: (realm) => set({ status: 'awaiting_length', chosenRealm: realm }),
  
  chooseLength: async (length) => {
    const promise = new Promise(resolve => setTimeout(resolve, 3000));
    set({ status: 'weaving_social_post', chosenLength: length, error: null, ritualPromise: promise });
    await promise;
    set({ status: 'social_post_woven', finalContent: { post_text: "Generated social post...", image_prompt: "...", video_prompt: "..." }, ritualPromise: null });
  },

  submitPostToCommentOn: async (post) => {
    const promise = new Promise(resolve => setTimeout(resolve, 3000));
    set({ status: 'weaving_comment', postToCommentOn: post, error: null, ritualPromise: promise });
    await promise;
    set({ status: 'comment_woven', finalContent: { comments: ["Generated comment 1...", "Generated comment 2..."] }, ritualPromise: null });
  },

  regenerate: async () => {
    const { status } = get();
    if (status === 'blog_woven') {
      await get().chooseContentType('Blog Post');
    } else if (status === 'social_post_woven') {
      await get().chooseLength(get().chosenLength!);
    } else if (status === 'comment_woven') {
      await get().submitPostToCommentOn(get().postToCommentOn!);
    }
  },

  resetLoom: () => {
    // This resets back to the list of sparks if they exist.
    if (get().sparks.length > 0) {
        set({
            status: 'sparks_revealed', error: null, chosenSpark: null, 
            chosenTone: null, chosenRealm: null, chosenLength: null, postToCommentOn: null, finalContent: null,
            ritualPromise: null
        });
    } else {
        set({
            status: 'awaiting_spark_topic', error: null, sparks: [], chosenSpark: null, 
            chosenTone: null, chosenRealm: null, chosenLength: null, postToCommentOn: null, finalContent: null,
            ritualPromise: null
        });
    }
  },
}));
// --- END OF FILE src/store/contentStore.ts ---