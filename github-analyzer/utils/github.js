// utils/github.js

import axios from 'axios';

const token = process.env.GITHUB_TOKEN;

export async function fetchUserRepositories(username) {
  const url = `https://api.github.com/users/${username}/repos?per_page=100`;

  try {
    const response = await axios.get(url, {
      headers: {
        Authorization: `token ${token}`,
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error fetching repositories:', error.response.data);
    throw error;
  }
}
// utils/github.js

export async function fetchCodeFiles(owner, repoName, path = '') {
    const url = `https://api.github.com/repos/${owner}/${repoName}/contents/${path}`;
  
    try {
      const response = await axios.get(url, {
        headers: {
          Authorization: `token ${token}`,
        },
      });
  
      const contents = response.data;
      let codeFiles = [];
  
      for (const item of contents) {
        if (item.type === 'file') {
          // Filter code files by extension
          if (['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.cs'].some((ext) => item.name.endsWith(ext))) {
            codeFiles.push(item.download_url);
          }
        } else if (item.type === 'dir') {
          const subFiles = await fetchCodeFiles(owner, repoName, item.path);
          codeFiles = codeFiles.concat(subFiles);
        }
      }
  
      return codeFiles;
    } catch (error) {
      console.error(`Error fetching code files from ${owner}/${repoName}:`, error.response.data);
      throw error;
    }
  }
  
  export async function downloadCodeFile(url) {
    try {
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error('Error downloading code file:', error.response.data);
      throw error;
    }
  }
  