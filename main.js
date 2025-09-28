// This is a note: you should run 'npm install dotenv' and 'npm install ollama' in your terminal.
// SETUP: npm install dotenv ollama

// Import necessary packages
import { Ollama } from 'ollama';
import dotenv from 'dotenv';

// Load environment variables from your .env file
dotenv.config();

// Retrieve the API key from the environment
const apiKey = process.env.OLLAMA_API_KEY;

// Ensure the API key is available
if (!apiKey) {
    throw new Error("OLLAMA_API_KEY not found. Make sure it is set in your .env file.");
}

// Create a custom Ollama client with the host and Authorization header
const client = new Ollama({
    host: 'https://ollama.com',
    headers: {
        'Authorization': `Bearer ${apiKey}`,
    },
});

// Define an async function to run the web search
async function runWebSearch() {
    try {
        console.log("Searching for 'what is ollama?'...");
        const results = await client.webSearch({ query: "what is ollama?" });
        console.log(JSON.stringify(results, null, 2));
    } catch (error) {
        console.error("An error occurred during the web search:", error);
    }
}

// Execute the function
runWebSearch();