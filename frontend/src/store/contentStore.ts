// --- START OF REFACTORED FILE frontend/src/store/contentStore.ts ---
import { create } from 'zustand';

// --- Polling Helper ---
const pollProphecy = (taskId: string, onComplete: (result: any) => void, onError: (error: any) => void) => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;
  const interval = setInterval(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/prophesy/status/${taskId}`);
      if (!res.ok) throw new Error("Failed to get prophecy status.");
      const data = await res.json();
      if (data.status === 'SUCCESS') {
        clearInterval(interval);
        if (data.result?.error) onError(data.result);
        else onComplete(data.result);
      } else if (data.status === 'FAILURE') {
        clearInterval(interval);
        onError(data.result || { error: "Prophecy failed without a reason." });
      }
    } catch (err) {
      clearInterval(interval);
      onError({ error: "Network error while checking prophecy status.", details: err });
    }
  }, 4000);
};

// --- State Types ---
type ContentSagaType = 'sparks' | 'social_post' | 'comment' | 'blog_post';
type LoomStatus = 'idle' | 'awaiting_spark_topic' | 'weaving_sparks' | 'sparks_revealed' | 'crossroads_revealed' | 'awaiting_tone' | 'awaiting_realm' | 'awaiting_length' | 'weaving_social_post' | 'awaiting_echo' | 'weaving_comment' | 'weaving_blog' | 'social_post_woven' | 'comment_woven' | 'blog_woven';
interface ContentSpark { id: string; title: string; description: string; format_suggestion: string; }
interface FinalContent { [key: string]: any; }

interface ContentSagaState {
  status: LoomStatus;
  error: string | null;
  ritualPromise: Promise<any> | null;
  
  // This will hold the full context from the main strategy
  strategyContext: any | null; 
  tacticalInterest: string;
  sparksResult: { sparks: ContentSpark[] } & any | null;
  chosenSpark: ContentSpark | null;
  chosenContentType: 'Social Post' | 'Comment' | 'Blog Post' | null;
  chosenTone: string | null;
  chosenRealm: string | null;
  finalContent: FinalContent | null;

  // Rites of the Loom
  beginWeaving: (strategyData: any, initialTacticalInterest: string) => void;
  generateSparks: (sessionId: string) => void;
  chooseSpark: (sparkId: string) => void;
  chooseContentType: (type: 'Social Post' | 'Comment' | 'Blog Post', sessionId: string) => void;
  chooseTone: (tone: string) => void;
  chooseRealm: (realm: string) => void;
  chooseLength: (length: string, sessionId: string) => void;
  submitPostToCommentOn: (postContent: string, sessionId: string) => void;
  regenerate: (sessionId: string) => void;
  resetLoom: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_SAGA_API_URL;

export const useContentStore = create<ContentSagaState>((set, get) => ({
  status: 'idle', error: null, ritualPromise: null,
  strategyContext: null, tacticalInterest: '',
  sparksResult: null, chosenSpark: null, 
  chosenContentType: null, chosenTone: null, chosenRealm: null,
  finalContent: null,
  
  // --- MODIFIED RITE ---
  beginWeaving: (strategyData, initialTacticalInterest) => {
    set({ 
      status: 'awaiting_spark_topic', 
      strategyContext: strategyData, // Store the context
      tacticalInterest: initialTacticalInterest, 
      error: null 
    });
  },

  generateSparks: (sessionId) => {
    if (!sessionId) return set({ error: "Session ID missing."});
    const { tacticalInterest, strategyContext } = get();
    set({ status: 'weaving_sparks', error: null });

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/content-saga`, {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: sessionId, content_type: 'sparks', 
                tactical_interest: tacticalInterest, 
                retrieved_histories: strategyContext?.retrieved_histories
              })
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                set({ status: 'sparks_revealed', sparksResult: result });
                resolve(result);
              },
              (error) => {
                const msg = error.details || error.error;
                set({ status: 'awaiting_spark_topic', error: msg });
                reject(new Error(msg));
              }
            );
        } catch(err: any) {
            set({ status: 'awaiting_spark_topic', error: err.message });
            reject(err);
        }
    });
    set({ ritualPromise: promise });
  },

  chooseSpark: (sparkId) => {
    const chosen = get().sparksResult?.sparks.find(s => s.id === sparkId);
    if (chosen) {
      set({ status: 'crossroads_revealed', chosenSpark: chosen });
    }
  },

  chooseContentType: (type, sessionId) => {
     // @ts-ignore
    set({ chosenContentType: type });
    if (type === 'Social Post') set({ status: 'awaiting_tone' });
    else if (type === 'Comment') set({ status: 'awaiting_echo' });
    else if (type === 'Blog Post') {
       // @ts-ignore
      get()._forgeContent('blog_post', {}, sessionId);
    }
  },

  chooseTone: (tone) => set({ status: 'awaiting_realm', chosenTone: tone }),
  chooseRealm: (realm) => set({ status: 'awaiting_length', chosenRealm: realm }),
  chooseLength: (length, sessionId) => get()._forgeContent('social_post', { length, platform: get().chosenRealm }, sessionId),
  submitPostToCommentOn: (postContent, sessionId) => get()._forgeContent('comment', { post_to_comment_on: postContent }, sessionId),

  _forgeContent: function(type: ContentSagaType, details: any, sessionId: string) {
    if (!sessionId) return set({ error: "Session ID missing."});
    const { chosenSpark } = get();
    if (!chosenSpark) return set({ error: "No content spark was chosen." });

    const nextStatus = `weaving_${type}` as LoomStatus;
    set({ status: nextStatus, error: null });

    const promise = new Promise(async (resolve, reject) => {
        try {
            const res = await fetch(`${API_BASE_URL}/prophesy/content-saga`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId, content_type: type, spark: chosenSpark, ...details
                })
            });
            if (!res.ok) { const err = await res.json(); throw new Error(err.detail); }
            const { task_id } = await res.json();
      
            pollProphecy(task_id,
              (result) => {
                const finalStatus = `${type}_woven` as LoomStatus;
                set({ status: finalStatus, finalContent: result });
                resolve(result);
              },
              (error) => {
                const msg = error.details || error.error;
                set({ status: 'crossroads_revealed', error: msg });
                reject(new Error(msg));
              }
            );
        } catch(err: any) {
            set({ status: 'crossroads_revealed', error: err.message });
            reject(err);
        }
    });
    set({ ritualPromise: promise });
  } as any,
  
  regenerate: (sessionId) => {
    console.warn("Regeneration needs to be re-triggered from the component.");
  },

  resetLoom: () => {
    const { strategyContext, tacticalInterest } = get();
    // Keep initial context but reset the rest of the workflow
    set({ status: 'awaiting_spark_topic', error: null, ritualPromise: null, sparksResult: null, chosenSpark: null, finalContent: null, strategyContext, tacticalInterest });
  },
}));
// --- END OF REFACTORED FILE frontend/src/store/contentStore.ts ---