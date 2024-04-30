import { OpenAIClient, AzureKeyCredential } from '@azure/openai';
import dotenv from 'dotenv';

dotenv.config();

const endpoint = process.env.AZURE_OPENAI_ENDPOINT || '';
const azureApiKey = process.env.AZURE_OPENAI_KEY || '';

const prompt = ['What is Azure OpenAI?'];


// Configure your Azure OpenAI client
const client = new OpenAIClient({
    endpoint: endpoint,
    credential: new AzureKeyCredential(azureApiKey),
    apiVersion: "2024-03-01-preview"  // Make sure this matches the API version you intend to use
});

// Set the model you want to use
const modelName = "gpt-4-1106";
