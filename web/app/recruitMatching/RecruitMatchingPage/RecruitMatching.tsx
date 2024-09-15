"use client";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { GithubIcon } from "lucide-react";
import Link from "next/link";
import styled, { keyframes } from "styled-components";

// Message box for the text
const MessageBox = styled.div`
  background-color: #f0f4f8;
  border: 1px solid #d1dce5;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
`;

const LanguageBar = ({ languages }: { languages: any }) => {
  const totalPercentage = Object.values(languages).reduce((sum, value) => sum + value, 0);

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

// Define smooth flip behavior
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
  style: { width: `${props.level}%` },
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
    content: "";
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

const people = [
  // Backend Developer 1: Focus on AI and Machine Learning
  {
    name: "Charlie Brown",
    description: "Data scientist specializing in machine learning and AI.",
    skills: ["Python", "TensorFlow", "SQL", "Machine Learning", "AI"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "charlie-brown",
    languages: { Python: 70, R: 20, SQL: 10 },
    commitment: 88,
    teamDynamics: 55,
    workStyle: 62,
    skillsExperience: 95,
    motivationGoals: 77,
  },
  // Backend Developer 2: Focus on Cloud and AI
  {
    name: "Diana Martinez",
    description: "DevOps engineer with cloud and AI expertise.",
    skills: ["AWS", "Docker", "Kubernetes", "AI"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "diana-martinez",
    languages: { Shell: 40, Python: 30, YAML: 30 },
    commitment: 80,
    teamDynamics: 85,
    workStyle: 78,
    skillsExperience: 91,
    motivationGoals: 92,
  },
  // Frontend Developer 1
  {
    name: "Alice Johnson",
    description: "Full-stack developer with 5 years of experience, frontend expert.",
    skills: ["React", "Node.js", "HTML", "CSS"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "alice-johnson",
    languages: { JavaScript: 50, Python: 30, HTML: 20 },
    commitment: 92,
    teamDynamics: 87,
    workStyle: 45,
    skillsExperience: 93,
    motivationGoals: 89,
  },
  // Frontend Developer 2
  {
    name: "Bob Smith",
    description: "UX/UI designer passionate about user-centered design.",
    skills: ["Figma", "Adobe XD", "Sketch", "React"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "bob-smith",
    languages: { JavaScript: 20, CSS: 60, HTML: 20 },
    commitment: 72,
    teamDynamics: 50,
    workStyle: 40,
    skillsExperience: 82,
    motivationGoals: 68,
  },
  // Frontend Developer 3
  {
    name: "Ethan Williams",
    description: "Mobile app developer focused on cross-platform solutions.",
    skills: ["React Native", "Flutter", "Swift", "Figma"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "ethan-williams",
    languages: { JavaScript: 40, Dart: 30, Swift: 30 },
    commitment: 95,
    teamDynamics: 92,
    workStyle: 88,
    skillsExperience: 90,
    motivationGoals: 100,
  },
];

export default function MatchingView() {
  const [flippedStates, setFlippedStates] = useState<boolean[]>(new Array(people.length).fill(false));
  const [allFlipped, setAllFlipped] = useState(false);

  const handleFlip = (index: number) => {
    const newFlippedStates = [...flippedStates];
    newFlippedStates[index] = !newFlippedStates[index];
    setFlippedStates(newFlippedStates);
  };

  const handleFlipAll = () => {
    const newFlippedStates = new Array(people.length).fill(!allFlipped);
    setFlippedStates(newFlippedStates);
    setAllFlipped(!allFlipped);
  };

  return (
    <>
      <div className="container mx-auto p-4 space-y-8">
        {/* Text box added above results */}
        <MessageBox>
          These are the results closest to the desired tech stack, as well to help the recruiters, there is an aptitude test for the users for you to look at too.
        </MessageBox>

        {/* Existing Flip Card Section */}
        <Button onClick={handleFlipAll} className="mb-4">
          {allFlipped ? "Undo Flip All" : "Flip All"}
        </Button>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {people.map((person, index) => (
            <FlipCard key={index}>
              <FlipInner flipped={flippedStates[index]}>
                {/* Front of the Card */}
                <FlipFront>
                  <Card className="flex flex-col">
                    <CardHeader>
                      <div className="flex items-center space-x-4">
                        <Avatar>
                          <AvatarImage src={person.avatar} alt={person.name} />
                          <AvatarFallback>
                            {person.name.split(" ").map((n) => n[0]).join("")}
                          </AvatarFallback>
                        </Avatar>
                        <CardTitle>{person.name}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-grow">
                      <p className="text-sm text-muted-foreground mb-4">
                        {person.description}
                      </p>
                      <div className="flex flex-wrap gap-2 mb-4">
                        {person.skills.map((skill, skillIndex) => (
                          <Badge key={skillIndex} variant="secondary">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                      <LanguageBar languages={person.languages} />
                      <div className="text-xs text-muted-foreground mt-2">
                        {Object.entries(person.languages).map(
                          ([lang, percentage], index) => (
                            <span key={lang}>
                              {lang} {percentage}%
                              {index <
                              Object.entries(person.languages).length - 1
                                ? " · "
                                : ""}
                            </span>
                          )
                        )}
                      </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                      <Button variant="outline" size="sm" asChild>
                        <a
                          href={`https://github.com/${person.github}`}
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
                      <CardTitle>{person.name}'s Aptitude Test</CardTitle>
                    </CardHeader>
                    <CardContent className="flex-grow">
                      <div className="flex flex-col space-y-4">
                        <div>
                          <span>Commitment Level: </span>
                          <LiquidFill level={person.commitment} />
                        </div>
                        <div>
                          <span>Team Dynamics: </span>
                          <LiquidFill level={person.teamDynamics} />
                        </div>
                        <div>
                          <span>Work Style: </span>
                          <LiquidFill level={person.workStyle} />
                        </div>
                        <div>
                          <span>Skills & Experience: </span>
                          <LiquidFill level={person.skillsExperience} />
                        </div>
                        <div>
                          <span>Motivation & Goals: </span>
                          <LiquidFill level={person.motivationGoals} />
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
