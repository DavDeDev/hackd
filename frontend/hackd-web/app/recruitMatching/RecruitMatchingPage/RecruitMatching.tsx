"use client";
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { GithubIcon, ArrowLeft, Star, Users, Code, Activity } from "lucide-react";
import Link from "next/link";
import styled, { keyframes } from "styled-components";

const MessageBox = styled.div`
  background-color: #f0f4f8;
  border: 1px solid #d1dce5;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
`;

const JobSummaryBox = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 30px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
`;

const NoDataMessage = styled.div`
  text-align: center;
  padding: 60px 20px;
  background: #f9fafb;
  border-radius: 12px;
  color: #6b7280;
  font-size: 1.1rem;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-radius: 50%;
  border-top-color: #3498db;
  animation: spin 1s ease-in-out infinite;
  margin: 20px auto;
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

interface JobAnalysisResults {
  jobDescription: string;
  analysisResults: {
    job_requirements: {
      technologies: string[];
      experience_level: string;
      team_size: string;
      work_style: string;
    };
    candidate_rankings: Array<{
      username: string;
      match_score: number;
      tech_overlap: string[];
      experience_level: number;
      collaboration_score: number;
      repository_count: number;
      top_technologies: string[];
      confidence: number;
      debug_info?: any;
    }>;
    processing_summary: {
      avg_match_score: number;
      top_match_score: number;
      failed_usernames: string[];
    };
  };
  timestamp: number;
}

export default function MatchingView() {
  const [analysisData, setAnalysisData] = useState<JobAnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [flippedStates, setFlippedStates] = useState<boolean[]>([]);
  const [allFlipped, setAllFlipped] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    console.log('🔄 Loading job analysis results...');
    
    try {
      const storedData = sessionStorage.getItem('hackd_job_analysis');
      
      if (!storedData) {
        console.log('⚠️ No analysis data found in sessionStorage');
        setError('No job analysis data found. Please submit a job description first.');
        setIsLoading(false);
        return;
      }
      
      const parsedData: JobAnalysisResults = JSON.parse(storedData);
      console.log('✅ Analysis data loaded:', parsedData);
      
      // Check if data is not too old (1 hour expiry)
      const oneHourAgo = Date.now() - (60 * 60 * 1000);
      if (parsedData.timestamp < oneHourAgo) {
        console.log('⏰ Analysis data expired');
        setError('Analysis data has expired. Please submit a new job description.');
        sessionStorage.removeItem('hackd_job_analysis');
        setIsLoading(false);
        return;
      }
      
      setAnalysisData(parsedData);
      setFlippedStates(new Array(parsedData.analysisResults.candidate_rankings.length).fill(false));
      
    } catch (err) {
      console.error('❌ Error loading analysis data:', err);
      setError('Error loading analysis data. Please try submitting a new job description.');
      sessionStorage.removeItem('hackd_job_analysis');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleFlip = (index: number) => {
    const newFlippedStates = [...flippedStates];
    newFlippedStates[index] = !newFlippedStates[index];
    setFlippedStates(newFlippedStates);
  };

  const handleFlipAll = () => {
    if (!analysisData) return;
    const newFlippedStates = new Array(analysisData.analysisResults.candidate_rankings.length).fill(!allFlipped);
    setFlippedStates(newFlippedStates);
    setAllFlipped(!allFlipped);
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return '#10b981';
    if (score >= 0.6) return '#f59e0b';
    if (score >= 0.4) return '#f97316';
    return '#ef4444';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    if (score >= 0.4) return 'Moderate Match';
    return 'Basic Match';
  };

  const getExperienceLevel = (complexity: number) => {
    if (complexity <= 4) return 'Junior';
    if (complexity <= 7) return 'Mid-level';
    return 'Senior';
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-4 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600">Loading job analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !analysisData) {
    return (
      <div className="container mx-auto p-4">
        <NoDataMessage>
          <h2 className="text-xl font-semibold mb-4">No Analysis Data Available</h2>
          <p className="mb-6">{error || 'No job analysis data found.'}</p>
          <Link href="/recruiting">
            <Button className="inline-flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Submit New Job Description
            </Button>
          </Link>
        </NoDataMessage>
      </div>
    );
  }

  const { analysisResults } = analysisData;
  const candidates = analysisResults.candidate_rankings || [];

  return (
    <div className="container mx-auto p-4 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link href="/recruiting">
          <Button variant="outline" className="inline-flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Job Description
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-800">Candidate Matches</h1>
        <div className="text-sm text-gray-500">
          {candidates.length} candidates analyzed
        </div>
      </div>

      {/* Job Requirements Summary */}
      <JobSummaryBox>
        <h2 className="text-2xl font-bold mb-4">Job Requirements Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <h3 className="font-semibold mb-2">Technologies</h3>
            <div className="flex flex-wrap gap-2">
              {analysisResults.job_requirements.technologies.map((tech, idx) => (
                <Badge key={idx} variant="secondary" className="bg-white/20 text-white">
                  {tech}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Experience Level</h3>
            <p className="text-white/90">{analysisResults.job_requirements.experience_level}</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Team Size</h3>
            <p className="text-white/90">{analysisResults.job_requirements.team_size}</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Work Style</h3>
            <p className="text-white/90">{analysisResults.job_requirements.work_style}</p>
          </div>
        </div>
      </JobSummaryBox>

      {/* Results Summary */}
      <MessageBox>
        <div className="flex items-center justify-center gap-8">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {(analysisResults.processing_summary.top_match_score * 100).toFixed(0)}%
            </div>
            <div className="text-sm">Top Match Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {(analysisResults.processing_summary.avg_match_score * 100).toFixed(0)}%
            </div>
            <div className="text-sm">Average Match</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{candidates.length}</div>
            <div className="text-sm">Candidates Found</div>
          </div>
        </div>
      </MessageBox>

      {/* Controls */}
      <div className="flex justify-between items-center">
        <Button onClick={handleFlipAll} variant="outline">
          {allFlipped ? "Show Profiles" : "Show Details"}
        </Button>
        <p className="text-sm text-gray-600">
          Click cards to flip between profile and detailed analysis
        </p>
      </div>

      {/* Candidate Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {candidates.map((candidate, index) => (
          <Card 
            key={candidate.username} 
            className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
              flippedStates[index] ? 'bg-gray-50' : ''
            }`}
            onClick={() => handleFlip(index)}
          >
            {!flippedStates[index] ? (
              // Front of card - Profile view
              <>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src={`https://github.com/${candidate.username}.png`} />
                        <AvatarFallback>{candidate.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-lg">{candidate.username}</CardTitle>
                        <p className="text-sm text-gray-600">
                          {getExperienceLevel(candidate.experience_level)} Developer
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div 
                        className="text-2xl font-bold mb-1"
                        style={{ color: getScoreColor(candidate.match_score) }}
                      >
                        {(candidate.match_score * 100).toFixed(0)}%
                      </div>
                      <Badge 
                        variant="secondary" 
                        style={{ backgroundColor: getScoreColor(candidate.match_score) + '20' }}
                      >
                        {getScoreLabel(candidate.match_score)}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-2">
                  <div className="space-y-3">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Top Technologies</h4>
                      <div className="flex flex-wrap gap-1">
                        {candidate.top_technologies.slice(0, 4).map((tech, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                        {candidate.top_technologies.length > 4 && (
                          <Badge variant="outline" className="text-xs">
                            +{candidate.top_technologies.length - 4} more
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        <span>Collab: {candidate.collaboration_score.toFixed(1)}/10</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Code className="w-3 h-3" />
                        <span>{candidate.repository_count} repos</span>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium mb-2">Tech Overlap</h4>
                      <div className="flex flex-wrap gap-1">
                        {candidate.tech_overlap.length > 0 ? (
                          candidate.tech_overlap.map((tech, idx) => (
                            <Badge key={idx} variant="default" className="text-xs bg-green-100 text-green-800">
                              {tech}
                            </Badge>
                          ))
                        ) : (
                          <span className="text-xs text-gray-500">No direct matches</span>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pt-2">
                  <div className="w-full flex items-center justify-between">
                    <a 
                      href={`https://github.com/${candidate.username}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <GithubIcon className="w-4 h-4" />
                      View Profile
                    </a>
                    <span className="text-xs text-gray-500">Click for details</span>
                  </div>
                </CardFooter>
              </>
            ) : (
              // Back of card - Detailed analysis
              <div className="p-4">
                <div className="text-center mb-4">
                  <h3 className="font-bold text-lg">{candidate.username}</h3>
                  <p className="text-sm text-gray-600">Detailed Match Analysis</p>
                </div>
                
                <div className="space-y-4 text-sm">
                  <div className="bg-white p-3 rounded-lg">
                    <h4 className="font-semibold mb-2">Match Breakdown</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Overall Score:</span>
                        <span className="font-bold" style={{ color: getScoreColor(candidate.match_score) }}>
                          {(candidate.match_score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Experience Match:</span>
                        <span>{getExperienceLevel(candidate.experience_level)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Confidence Level:</span>
                        <span>{(candidate.confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white p-3 rounded-lg">
                    <h4 className="font-semibold mb-2">All Technologies</h4>
                    <div className="flex flex-wrap gap-1">
                      {candidate.top_technologies.map((tech, idx) => (
                        <Badge 
                          key={idx} 
                          variant={candidate.tech_overlap.includes(tech) ? "default" : "outline"}
                          className={`text-xs ${
                            candidate.tech_overlap.includes(tech) 
                              ? 'bg-green-100 text-green-800' 
                              : ''
                          }`}
                        >
                          {tech}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white p-3 rounded-lg">
                    <h4 className="font-semibold mb-2">Profile Stats</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>Repositories: {candidate.repository_count}</div>
                      <div>Collaboration: {candidate.collaboration_score.toFixed(1)}/10</div>
                      <div>Complexity: {candidate.experience_level.toFixed(1)}/10</div>
                      <div>Tech Matches: {candidate.tech_overlap.length}</div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 text-center">
                  <span className="text-xs text-gray-500">Click to flip back</span>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {candidates.length === 0 && (
        <NoDataMessage>
          <h3 className="text-lg font-semibold mb-2">No Candidates Found</h3>
          <p>No suitable candidates were found for this job description.</p>
        </NoDataMessage>
      )}
    </div>
  );
}