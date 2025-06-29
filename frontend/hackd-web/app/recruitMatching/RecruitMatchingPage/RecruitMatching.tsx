"use client";
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
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

const peopleData = async () => {
  const response = await fetch("/analyze-sentiment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: "User feedback or description" }), // Example text input
  });
  const data = await response.json();
  return data;
};

export default function MatchingView() {
  const [people, setPeople] = useState<any[]>([]);
  const [flippedStates, setFlippedStates] = useState<boolean[]>(new Array(people.length).fill(false));
  const [allFlipped, setAllFlipped] = useState(false);

  useEffect(() => {
    peopleData().then((data) => setPeople(data)); // Fetch data on mount
  }, []);

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
        <MessageBox>
          These are the results closest to the desired tech stack, as well to help the recruiters, there is an aptitude test for the users for you to look at too.
        </MessageBox>
        <Button onClick={handleFlipAll} className="mb-4">
          {allFlipped ? "Undo Flip All" : "Flip All"}
        </Button>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {people.map((person, index) => (
            <Card key={index} className="flex flex-col">
              {/* Front and back of the card */}
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
