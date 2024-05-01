"use strict";
var __importDefault =
  (this && this.__importDefault) ||
  function (mod) {
    return mod && mod.__esModule ? mod : { default: mod };
  };
Object.defineProperty(exports, "__esModule", { value: true });
const openai_1 = require("@azure/openai");
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const endpoint = process.env.AZURE_OPENAI_ENDPOINT || "";
const azureApiKey = process.env.AZURE_OPENAI_KEY || "";
const prompt = ["What is Azure OpenAI?"];
// Configure your Azure OpenAI client
const client = new openai_1.OpenAIClient({
  endpoint: endpoint,
  credential: new openai_1.AzureKeyCredential(azureApiKey),
  apiVersion: "2024-03-01-preview", // Make sure this matches the API version you intend to use
});
// Set the model you want to use
const modelName = "gpt-4-1106";
