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
  opacity: 1;  /* Ensure button stays visible */
  transition: all 0.3s ease;
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 12px rgba(252, 130, 62, 0.6);  /* Glow effect on hover */
  }
`;

const RecruitingPage = () => {
  const [jobDescription, setJobDescription] = useState<string>('');
  const [response, setResponse] = useState<string>('');

  const handleSubmit = async () => {
    try {
      const res = await fetch('http://localhost:3000/analyze-sentiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: jobDescription })
      });
      const data = await res.json();
      setResponse(data.summary);
      window.location.href = 'http://localhost:3000/recruitMatching';
    } catch (error) {
      console.error('Error submitting job description:', error);
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

      <SubmitButton onClick={handleSubmit}>Submit</SubmitButton>
    </Container>
  );
};

export default RecruitingPage;
