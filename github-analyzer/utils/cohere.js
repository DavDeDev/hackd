// utils/cohere.js

import cohere from 'cohere-ai';

cohere.init(process.env.COHERE_API_KEY);

export async function analyzeCodeWithCohere(codeSnippet) {
  const prompt = `Analyze the following code and provide a brief summary, identify any potential issues, and suggest improvements.

Code:
${codeSnippet}

Analysis:`;

  try {
    const response = await cohere.generate({
      model: 'command-r-plus',
      prompt,
      max_tokens: 200,
      temperature: 0.7,
    });

    return response.body.generations[0].text.trim();
  } catch (error) {
    console.error('Error using Cohere Generate API:', error);
    throw error;
  }
}

// utils/cohere.js

export async function getCodeEmbeddings(codeSnippets) {
    try {
      const response = await cohere.embed({
        texts: codeSnippets,
        model: 'embed-english-v2.0',
      });
  
      return response.body.embeddings;
    } catch (error) {
      console.error('Error using Cohere Embed API:', error);
      throw error;
    }
  }
// utils/cohere.js

const examples = [
    { text: 'def add(a, b): return a + b', label: 'High Quality' },
    { text: 'def add(a,b):return a+b', label: 'Medium Quality' },
    { text: 'def add(a,b): a+b', label: 'Low Quality' },
    // Add more examples
  ];
  
export async function classifyCodeSnippet(codeSnippet) {
    try {
      const response = await cohere.classify({
        inputs: [codeSnippet],
        examples,
        model: 'large',
      });
  
      return response.body.classifications[0].prediction;
    } catch (error) {
      console.error('Error using Cohere Classify API:', error);
      throw error;
    }
  }
    
