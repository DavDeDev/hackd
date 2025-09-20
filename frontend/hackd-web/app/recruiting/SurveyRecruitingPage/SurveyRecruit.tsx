"use client";

import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import './SurveyRecruit.css';

// Define animations
const fadeIn = keyframes`
  0% { opacity: 0; visibility: hidden; transform: translateY(10px); }
  100% { opacity: 1; visibility: visible; transform: translateY(0); }
`;

const glow = keyframes`
  0% { box-shadow: 0 0 5px #fc823e; }
  50% { box-shadow: 0 0 20px #fc823e, 0 0 30px #fcae61; }
  100% { box-shadow: 0 0 5px #fc823e; }
`;

const float = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
`;

// Styled components
const Container = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f6f1e7, #f1e7d8);
  padding: 2rem;
  opacity: 0;
  animation: ${fadeIn} 1.5s ease-in-out forwards;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  opacity: 0;
  visibility: hidden;
  animation: ${fadeIn} 1.8s ease-in-out forwards 0.5s;
`;

const Title = styled.h1`
  font-size: 4.5rem;
  font-weight: bold;
  color: #707853;
  margin-bottom: 1rem;
  letter-spacing: 2px;
  animation: ${float} 4s ease-in-out infinite;
`;

const Subtitle = styled.p`
  font-size: 1.5rem;
  color: #7f5747;
  font-style: italic;
  opacity: 0;
  visibility: hidden;
  animation: ${fadeIn} 1.8s ease-in-out forwards 1s;
`;

const JobDescriptionSection = styled.div`
  position: relative;
  margin-bottom: 4rem;
  opacity: 0;
  visibility: hidden;
  animation: ${fadeIn} 2s ease-in-out forwards 1.2s;
`;

const TopBar = styled.div`
  background-color: #a57d57;
  height: 6px;
  width: 100%;
  position: absolute;
  top: -12px;
  border-radius: 4px;
  animation: ${glow} 2s infinite alternate;
`;

const JobDescriptionBox = styled.div`
  background: linear-gradient(145deg, #fff, #f9f9f9);
  padding: 2rem;
  border-radius: 2rem;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  animation: ${fadeIn} 2s ease-in-out forwards 1.5s;
`;

const JobDescriptionTextarea = styled.textarea`
  width: 100%;
  padding: 1.5rem;
  border: 2px solid #ddd;
  border-radius: 1rem;
  font-size: 1.2rem;
  transition: all 0.3s ease;
  &:focus {
    outline: none;
    border-color: #fc823e;
    box-shadow: 0 0 12px rgba(252, 130, 62, 0.4);
  }
`;

// Submit Button with hover effect
const SubmitButton = styled.button`
  background: linear-gradient(145deg, #fc823e, #fcae61);
  color: white;
  font-size: 1.5rem;
  padding: 1rem 2rem;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  margin-top: 2rem;
  opacity: 1;
  transition: all 0.3s ease;
  min-width: 200px;
  
  &:hover:not(:disabled) {
    transform: translateY(-5px);
    box-shadow: 0 0 12px rgba(252, 130, 62, 0.6);
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const ErrorMessage = styled.div`
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  text-align: center;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

const RecruitingPage = () => {
  const [jobDescription, setJobDescription] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      console.log('🚀 Submitting job description for analysis...');
      
      // Sample candidate pool for demo - in production this would come from your database
      const sampleCandidates = [
        'octocat', 'torvalds', 'gaearon', 'tj', 'sindresorhus', 
        'addyosmani', 'paulirish', 'getify', 'feross', 'substack'
      ];
      
      const requestBody = {
        job_description: jobDescription,
        candidates: sampleCandidates,
        include_debug: true
      };
      
      console.log('📤 Request payload:', requestBody);
      
      const res = await fetch('http://localhost:5000/api/analyze-job-description', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      console.log('📥 Response status:', res.status);
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || `HTTP ${res.status}: ${res.statusText}`);
      }
      
      const data = await res.json();
      console.log('✅ Job analysis successful:', data);
      
      // Store results in sessionStorage for the results page
      sessionStorage.setItem('hackd_job_analysis', JSON.stringify({
        jobDescription,
        analysisResults: data,
        timestamp: Date.now()
      }));
      
      console.log('🔄 Redirecting to results page...');
      window.location.href = '/recruitMatching';
      
    } catch (error) {
      console.error('❌ Error analyzing job description:', error);
      setError(error instanceof Error ? error.message : 'An error occurred while analyzing the job description');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <Header>
        <Title>Let’s find your match!</Title>
        <Subtitle>It's more than just matching, it's magic ✨</Subtitle>
      </Header>

      <JobDescriptionSection>
        <TopBar />
        <JobDescriptionBox>
          <h2 className="text-4xl font-bold text-[#707853] mb-4">Recruiter Job Description</h2>
          <p className="text-lg text-gray-700 mb-4">
            Are you looking to hire talented engineers? Please fill in your job description here so we can find the right match for you!
          </p>
          <JobDescriptionTextarea
            rows={6}
            placeholder="Enter job description..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </JobDescriptionBox>
      </JobDescriptionSection>

      <SubmitButton onClick={handleSubmit} disabled={isLoading || !jobDescription.trim()}>
        {isLoading ? (
          <>
            <LoadingSpinner /> Analyzing Job Description...
          </>
        ) : (
          'Find My Perfect Matches'
        )}
      </SubmitButton>
      
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </Container>
  );
};

export default RecruitingPage;
