"use client";

import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import { GithubIcon } from "lucide-react";
import Link from "next/link";
import styled, { keyframes } from "styled-components";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

// Function to fetch user data from the Python backend
const fetchMatchingData = async () => {
  const response = await fetch("http://localhost:3000/matching");
  const data = await response.json();
  return data;
};

// Styled components and animations
const FlipCard = styled.div`
  perspective: 1000px;
  width: 100%;
  height: 100%;
`;

const FlipInner = styled.div<{ flipped: boolean }>`
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 1s ease-in-out;
  transform-style: preserve-3d;
  transform: ${(props) => (props.flipped ? "rotateY(180deg)" : "rotateY(0deg)")};
`;

const FlipFront = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
`;

const FlipBack = styled(FlipFront)`
  transform: rotateY(180deg);
  backface-visibility: hidden;
`;

const bubbleRise = keyframes`
  0% {
    bottom: -10px;
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    bottom: 100%;
    opacity: 0;
  }
`;

const LiquidFill = styled.div.attrs((props: { level: number }) => ({
  style: { width: `${props.level * 100}%` }, // Level is expected to be between 0 and 1
}))`
  height: 20px;
  background-color: #fc823e;
  border-radius: 10px;
  position: relative;
  left: 0;
  top: 0;
  transition: width 1s ease-in-out;
  overflow: hidden;

  &:before,
  &:after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    background-color: rgba(255, 255, 255, 0.7);
    border-radius: 50%;
  }

  &:before {
    bottom: 0;
    left: 20%;
    animation: ${bubbleRise} 3s infinite ease-in-out;
    animation-delay: -0.2s;
  }

  &:after {
    bottom: 0;
    left: 60%;
    animation: ${bubbleRise} 4s infinite ease-in-out;
    animation-delay: -0.4s;
  }
`;

// Main MatchingView Component
export default function MatchingView() {
  const [users, setUsers] = useState<any[]>([]);
  const [flippedStates, setFlippedStates] = useState<boolean[]>([]);
  const [allFlipped, setAllFlipped] = useState(false);

  useEffect(() => {
    // Fetch data from the backend
    fetchMatchingData().then((userData) => {
      setUsers(userData);
      setFlippedStates(new Array(userData.length).fill(false));
    });
  }, []);

  const handleFlip = (index: number) => {
    const newFlippedStates = [...flippedStates];
    newFlippedStates[index] = !newFlippedStates[index];
    setFlippedStates(newFlippedStates);
  };

  const handleFlipAll = () => {
    const newFlippedStates = new Array(users.length).fill(!allFlipped);
    setFlippedStates(newFlippedStates);
    setAllFlipped(!allFlipped);
  };

  // Generate pie chart data dynamically for each user
  const getUserPieChartData = (skills: any) => {
    const labels = Object.keys(skills);
    const dataValues = Object.values(skills);

    const backgroundColors = labels.map(
      (_, index) => `hsl(${(index * 360) / labels.length}, 70%, 70%)`
    );
    const borderColors = labels.map(
      (_, index) => `hsl(${(index * 360) / labels.length}, 70%, 50%)`
    );

    return {
      labels: labels,
      datasets: [
        {
          data: dataValues,
          backgroundColor: backgroundColors,
          borderColor: borderColors,
          borderWidth: 1,
        },
      ],
    };
  };

  return (
    <>
      <div className="container mx-auto p-4 space-y-8">
        <Button onClick={handleFlipAll} className="mb-4">
          {allFlipped ? "Undo Flip All" : "Flip All"}
        </Button>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {users.map((user, index) => (
            <FlipCard key={index}>
              <FlipInner flipped={flippedStates[index]}>
                {/* Front of the Card */}
                <FlipFront>
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center space-x-4">
                        <Avatar>
                          <AvatarImage
                            src={user.avatar || "/placeholder.svg"}
                            alt={user.Username}
                          />
                          <AvatarFallback>
                            {user.Username.substring(0, 2)}
                          </AvatarFallback>
                        </Avatar>
                        <CardTitle>{user.Username}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-grow">
                      <p className="text-sm text-muted-foreground mb-4">
                        {user.SkillSummary}
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {Object.keys(user.Skills).map(
                          (skill: string, skillIndex: number) => (
                            <Badge key={skillIndex} variant="secondary">
                              {skill}
                            </Badge>
                          )
                        )}
                      </div>
                      {/* Pie Chart for User Skills */}
                      <Pie data={getUserPieChartData(user.Skills)} />
                    </CardContent>
                    <CardFooter className="flex justify-between">
                      <Button variant="outline" size="sm" asChild>
                        <a
                          href={`https://github.com/${user.Username}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <GithubIcon className="w-4 h-4 mr-2" />
                          GitHub
                        </a>
                      </Button>
                      <Link href={"/product"}>
                        <Button size="sm">Match</Button>
                      </Link>
                    </CardFooter>
                  </Card>
                </FlipFront>

                {/* Back of the Card */}
                <FlipBack>
                  <Card className="flex flex-col">
                    <CardHeader>
                      <CardTitle>{user.Username}'s Aptitude Test</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-grow">
                      <div className="flex flex-col space-y-4">
                        <div>
                          <span>Commitment Level: </span>
                          <LiquidFill level={user.Commitment} />
                        </div>
                        <div>
                          <span>Team Dynamics: </span>
                          <LiquidFill level={user.TeamDynamics} />
                        </div>
                        <div>
                          <span>Work Style: </span>
                          <LiquidFill level={user.WorkStyle} />
                        </div>
                        <div>
                          <span>Skills & Experience: </span>
                          <LiquidFill level={user.SkillsExperience} />
                        </div>
                        <div>
                          <span>Motivation & Goals: </span>
                          <LiquidFill level={user.MotivationGoals} />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </FlipBack>
              </FlipInner>
            </FlipCard>
          ))}
        </div>
      </div>
    </>
  );
}

// LanguageBar component for additional visual representation of skills
const LanguageBar = ({ languages }: { languages: any }) => {
  const totalPercentage = Object.values(languages).reduce(
    (sum: number, value: number) => sum + value,
    0
  );

  return (
    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
      {Object.entries(languages).map(([lang, percentage], index) => (
        <div
          key={lang}
          className="h-full float-left"
          style={{
            width: `${(percentage / totalPercentage) * 100}%`,
            backgroundColor: `hsl(${index * 60}, 70%, 50%)`,
          }}
        />
      ))}
    </div>
  );
};
