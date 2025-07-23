// --- START OF FILE src/store/sagaStore.ts ---
import { create } from 'zustand';

// SAGA LOGIC: Defining the different states our application can be in.
// 'idle': Waiting for the user to submit the form.
// 'divining': The Ritual Screen is active, waiting for the backend and ad timer.
// 'prophesied': The Grand Strategy has been received and we are showing the tactical stack cards.
type SagaStatus = 'idle' | 'divining' | 'prophesied';

// SAGA LOGIC: Defining the structure of the data we will receive from the backend.
// We will build this out more as we connect to the API.
interface GrandStrategyData {
  strategy_session_id: string;
  prophecy: any; // We'll define a more specific type for this later.
}

// SAGA LOGIC: Defining the complete state of our store.
interface SagaState {
  status: SagaStatus;
  error: string | null;
  strategyData: GrandStrategyData | null;
  
  // This is the main function that will trigger the entire process.
  beginDivination: (formData: any) => Promise<void>;
  
  // A function to reset the state and start a new consultation.
  resetSaga: () => void;
}

// SAGA LOGIC: Creating the store with Zustand.
export const useSagaStore = create<SagaState>((set, get) => ({
  status: 'idle',
  error: null,
  strategyData: null,

  beginDivination: async (formData) => {
    // 1. Set the status to 'divining' to show the RitualScreen.
    set({ status: 'divining', error: null });

    // 2. Create two promises: one for the API call and one for the 30-second ad timer.
    const apiCallPromise = fetch('http://localhost:8000/api/v10/prophesy/grand-strategy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    }).then(res => {
      if (!res.ok) {
        throw new Error('The Oracle did not respond. The connection may be disrupted.');
      }
      return res.json();
    });

    const adTimerPromise = new Promise(resolve => setTimeout(resolve, 30000)); // 30-second timer.

    try {
      // 3. Wait for BOTH the API call and the ad timer to complete.
      const [apiResponse] = await Promise.all([apiCallPromise, adTimerPromise]);

      // 4. If successful, update the state with the received data and set status to 'prophesied'.
      set({ 
        status: 'prophesied', 
        strategyData: apiResponse.data 
      });

    } catch (err: any) {
      // 5. If anything fails, set an error message and revert status to 'idle'.
      console.error("The divination ritual failed:", err);
      set({ status: 'idle', error: err.message || 'An unknown disturbance occurred.' });
    }
  },

  resetSaga: () => {
    // Resets the entire store to its initial state for a new consultation.
    set({
      status: 'idle',
      error: null,
      strategyData: null,
    });
  },
}));
// --- END OF FILE src/store/sagaStore.ts ---