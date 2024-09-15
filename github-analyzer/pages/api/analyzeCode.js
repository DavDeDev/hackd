import { CohereClient, CohereError, CohereTimeoutError } from "cohere-ai";

// Initialize the Cohere client with your API key
const cohere = new CohereClient({
    token: COHERE_API_KEY,
});

// Function to identify weaknesses for each user
async function identifyWeakness(summary) {
    try {
        // Call the Cohere API to generate text
        const chat = await cohere.chat({
            model: "command",
            message: `${summary}\n\nIdentify the user's weaknesses and areas for improvement.`,
        });
        
        return chat.text;
    } catch (err) {
        // Handle errors gracefully
        if (err instanceof CohereTimeoutError) {
            console.log("Request timed out", err);
        } else if (err instanceof CohereError) {
            console.log("API Error:", err.statusCode);
            console.log(err.message);
            console.log(err.body);
        } else {
            console.log("Unexpected Error:", err);
        }
    }
}

// Example usage for streaming text generation
(async () => {
    const summary = "User savolai is proficient in C++ (66.74%), TypeScript (17.54%), etc.";
    
    // Use the streaming functionality to handle large text generation or long prompts
    const stream = await cohere.chatStream({
        model: "command",
        message: `${summary}\n\nIdentify the user's weaknesses and areas for improvement.`,
    });

    for await (const chat of stream) {
        if (chat.eventType === "text-generation") {
            process.stdout.write(chat.text);
        }
    }
})();

