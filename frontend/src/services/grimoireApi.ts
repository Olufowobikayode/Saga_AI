// --- START OF FILE src/services/grimoireApi.ts ---

const API_BASE_URL = 'http://localhost:8000/api/v10/grimoire';

// --- TYPE DEFINITIONS ---
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

export interface TitleConcept {
    title: string;
    slug: string;
}

export interface GeneratedContent {
    summary: string;
    content: string;
}

// --- PUBLIC FUNCTIONS (for displaying the blog) ---

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


// --- ADMIN FUNCTIONS (for managing the blog) ---

export const createScroll = async (
  pageData: { title: string; summary: string; content: string; tags: string[]; slug?: string },
  adminKey: string
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/inscribe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-admin-api-key': adminKey },
      body: JSON.stringify(pageData),
    });
    const data = await response.json();
    if (!response.ok) { throw new Error(data.detail || "The Oracle rejected the inscription."); }
    return { success: true, message: "The scroll has been successfully inscribed." };
  } catch (error: any) {
    console.error("Failed to inscribe the scroll:", error);
    return { success: false, message: error.message };
  }
};

export const updateScroll = async (
    id: string,
    pageData: { title?: string; summary?: string; content?: string; tags?: string[]; slug?: string },
    adminKey: string
  ): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/scrolls/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'x-admin-api-key': adminKey },
        body: JSON.stringify(pageData),
      });
      const data = await response.json();
      if (!response.ok) { throw new Error(data.detail || "The Oracle could not amend the scroll."); }
      return { success: true, message: "The scroll has been successfully updated." };
    } catch (error: any) {
      console.error("Failed to update the scroll:", error);
      return { success: false, message: error.message };
    }
  };

export const deleteScroll = async (id: string, adminKey: string): Promise<{ success: boolean; message: string }> => {
    try {
        const response = await fetch(`${API_BASE_URL}/scrolls/${id}`, {
            method: 'DELETE',
            headers: { 'x-admin-api-key': adminKey },
        });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "The Oracle refused to banish the scroll.");
        }
        return { success: true, message: "The scroll has been banished from the Grimoire." };
    } catch (error: any) {
        console.error("Failed to delete the scroll:", error);
        return { success: false, message: error.message };
    }
};

// --- ADMIN AI-POWERED FUNCTIONS ---

export const generateTitles = async (topic: string, adminKey: string): Promise<TitleConcept[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/generate-titles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-admin-api-key': adminKey },
            body: JSON.stringify({ topic }),
        });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Saga could not divine any titles.");
        }
        const data = await response.json();
        return data.concepts || [];
    } catch (error) {
        console.error("Failed to generate titles:", error);
        return [];
    }
};

export const generateContent = async (title: string, topic: string, adminKey: string): Promise<GeneratedContent | null> => {
    try {
        const response = await fetch(`${API_BASE_URL}/generate-content`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-admin-api-key': adminKey },
            body: JSON.stringify({ title, topic }),
        });
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Saga could not generate the scroll's content.");
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to generate content:", error);
        return null;
    }
};

// --- END OF FILE src/services/grimoireApi.ts ---