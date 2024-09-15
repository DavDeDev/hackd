"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Progress } from "@/components/ui/progress"

const questions = [
  {
    "id": 1,
    "text": "I prefer to lead team projects.",
    "category": "Motivation and Goals"
  },
  {
    "id": 2,
    "text": "I am excited about attending multiple workshops and events at the hackathon.",
    "category": "Commitment Level"
  },
  {
    "id": 3,
    "text": "I enjoy brainstorming and collaborating on ideas with others.",
    "category": "Team Dynamics"
  },
  {
    "id": 4,
    "text": "I like when my teammates have skills that complement mine.",
    "category": "Team Dynamics"
  },
  {
    "id": 5,
    "text": "Winning the hackathon is my top priority.",
    "category": "Commitment Level"
  },
  {
    "id": 6,
    "text": "I am open to learning new technologies during the event.",
    "category": "Skills and Experience"
  },
  {
    "id": 7,
    "text": "I work best under tight deadlines.",
    "category": "Work Style"
  },
  {
    "id": 8,
    "text": "I prefer working with teammates who share similar strengths.",
    "category": "Team Dynamics"
  },
  {
    "id": 9,
    "text": "I appreciate constructive feedback on my work.",
    "category": "Skills and Experience"
  },
  {
    "id": 10,
    "text": "I am confident in my coding abilities.",
    "category": "Skills and Experience"
  },
  {
    "id": 11,
    "text": "I enjoy taking on challenging problems.",
    "category": "Skills and Experience"
  },
  {
    "id": 12,
    "text": "I prefer a well-structured plan before starting a project.",
    "category": "Work Style"
  },
  {
    "id": 13,
    "text": "I am comfortable adapting to changes during the project.",
    "category": "Work Style"
  },
  {
    "id": 14,
    "text": "I like to focus on one task at a time.",
    "category": "Work Style"
  },
  {
    "id": 15,
    "text": "I am eager to help teammates who are struggling.",
    "category": "Team Dynamics"
  },
  {
    "id": 16,
    "text": "I value creativity over functionality in projects.",
    "category": "Motivation and Goals"
  },
  {
    "id": 17,
    "text": "I believe communication is key to a successful team.",
    "category": "Team Dynamics"
  },
  {
    "id": 18,
    "text": "I am motivated by learning rather than winning.",
    "category": "Motivation and Goals"
  },
  {
    "id": 19,
    "text": "I have experience with version control systems like GitHub.",
    "category": "Skills and Experience"
  },
  {
    "id": 20,
    "text": "I enjoy working late hours to meet project goals.",
    "category": "Commitment Level"
  }
]

const questionsPerPage = 5
const totalPages = Math.ceil(questions.length / questionsPerPage)

export default function Component() {
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [currentPage, setCurrentPage] = useState(1)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
    } else {
      console.log("Submitted answers:", answers)
      // Here you would typically send the answers to your backend
    }
  }

  const handlePrevious = () => {
    setCurrentPage(currentPage - 1)
  }

  const startIndex = (currentPage - 1) * questionsPerPage
  const endIndex = startIndex + questionsPerPage
  const currentQuestions = questions.slice(startIndex, endIndex)

  return (
    <Card className="w-full border-none shadow-none text-center mx-auto bg-transparent">
      <CardHeader>
        <CardTitle>Hackathon Participant Survey</CardTitle>
        <CardDescription>Please answer the following questions on a scale of 1 to 5, where 1 is strongly disagree and 5 is strongly agree.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <Progress value={(currentPage / totalPages) * 100} className="w-full" />
          {currentQuestions.map((question) => (
            <div key={question.id} className="space-y-2">
              <Label htmlFor={`question-${question.id}`}>{question.text}</Label>
              <RadioGroup
                id={`question-${question.id}`}
                onValueChange={(value) => setAnswers(prev => ({ ...prev, [question.id]: value }))}
                className="flex space-x-2 justify-center"
              >
                {[1, 2, 3, 4, 5].map((value) => (
                  <div key={value} className="flex items-center space-x-1">
                    <RadioGroupItem value={value.toString()} id={`q${question.id}-${value}`} />
                    <Label htmlFor={`q${question.id}-${value}`}>{value}</Label>
                  </div>
                ))}
              </RadioGroup>
              <p className="text-sm text-muted-foreground">{question.category}</p>
            </div>
          ))}
        </CardContent>
        <CardFooter className="flex justify-between">
          {currentPage > 1 && (
            <Button type="button" variant="outline" onClick={handlePrevious}>Previous</Button>
          )}
          <Button type="submit">
            {currentPage < totalPages ? "Next" : "Submit"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}