// pages/api/getRepoCode.js

import { fetchCodeFiles, downloadCodeFile } from '../../utils/github';

export default async function handler(req, res) {
  const { owner, repo } = req.query;

  if (!owner || !repo) {
    return res.status(400).json({ error: 'Owner and repo are required' });
  }

  try {
    const codeFileUrls = await fetchCodeFiles(owner, repo);
    let codeContents = [];

    for (const url of codeFileUrls) {
      const code = await downloadCodeFile(url);
      codeContents.push(code);
    }

    res.status(200).json({ codeContents });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch code contents' });
  }
}
