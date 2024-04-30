import { OpenAIClient, AzureKeyCredential } from '@azure/openai';
import dotenv from 'dotenv';

dotenv.config();

const endpoint = process.env.AZURE_OPENAI_ENDPOINT || '';
const azureApiKey = process.env.AZURE_OPENAI_KEY || '';

const prompt = ['What is Azure OpenAI?'];

async function main() {
  console.log('=== Get completions Sample ===');
  const api_version="2024-03-01-preview";
  const deploymentName = 'gpt-4-1106';
  const client = new OpenAIClient(
    endpoint,
    new AzureKeyCredential(azureApiKey),
    api_version
    deploymentName,
  );
  const result = await client.getCompletions(deploymentName, prompt, {
    maxTokens: 200,
    temperature: 0.25
  });

  for (const choice of result.choices) {
    console.log(choice.text);
  }
}

main().catch((err) => {
  console.error('The sample encountered an error:', err);
});