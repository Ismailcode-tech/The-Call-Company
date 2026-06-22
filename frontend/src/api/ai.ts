import { apiFetch } from "./_base";

// Sends a chat prompt to the backend assistant and returns just the reply text.
export async function chat(message: string): Promise<string> {
    const data = await apiFetch<{ response: string }>(
        "/ai_assistant/chat",
        {
            method: "POST",
            body: JSON.stringify({message}),
        },

        
    )
    return data.response;
}
