// --- START OF FILE src/services/grimoireApi.ts ---

// This file centralizes all API calls related to the Grimoire.

const API_BASE_URL = 'http://localhost:8000/api/v10/grimoire';

// SAGA LOGIC: Define the structure of a Grimoire Page for TypeScript.
export interface GrimoirePage {
  id: string;
  title: string;
  slug: string;
  author: string;
  summary: string;
  content: string;
  tags: string[];
  created_at: string;
}

/**
 * Fetches all published scrolls from the Grimoire.
 */
export const getAllScrolls = async (): Promise<GrimoirePage[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/scrolls`);
    if (!response.ok) {
      throw new Error("The Grimoire's scrolls are currently sealed.");
    }
    return await response.json();
  } catch (error) {
    console.error("Failed to retrieve scrolls from the Grimoire:", error);
    return [];
  }
};

/**
 * Fetches a single scroll by its unique slug.
 */
export const getScrollBySlug = async (slug: string): Promise<GrimoirePage | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/scrolls/${slug}`);
    if (!response.ok) {
      throw new Error(`The scroll '${slug}' could not be found.`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to retrieve the scroll '${slug}':`, error);
    return null;
  }
};

// NEW: Function to inscribe a new scroll.
export const createScroll = async (
  pageData: { title: string; summary: string; content: string; tags: string[] },
  adminKey: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/inscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-admin-api-key': adminKey, // The sacred key.
      },
      body: JSON.stringify(pageData),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "The Oracle rejected the inscription.");
    }
    return { success: true, message: "The scroll has been successfully inscribed." };
  } catch (error: any) {
    console.error("Failed to inscribe the scroll:", error);
    return { success: false, message: error.message };
  }
};
// --- END OF FILE src/services/grimoireApi.ts ---