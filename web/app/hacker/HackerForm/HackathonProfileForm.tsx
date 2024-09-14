"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

const questions = [
  "How satisfied are you with our product?",
  "How likely are you to recommend our product to others?",
  "How would you rate the ease of use of our product?",
  "How would you rate our customer support?",
  "How well does our product meet your needs?"
]

export default function Component() {
  const [answers, setAnswers] = useState<Record<number, string>>({})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Submitted answers:", answers)
    // Here you would typically send the answers to your backend
  }

  return (
    <Card className="w-full h-full mx-auto mt-5 text-center bg-transparent border-0 shadow-none">
      <CardHeader>
        <CardTitle >Personality Form</CardTitle>
        <CardDescription>Please answer the following questions on a scale of 1 to 5, where 1 is the lowest and 5 is the highest.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {questions.map((question, index) => (
            <div key={index} className="space-y-2">
              <Label htmlFor={`question-${index}`}>{question}</Label>
              <RadioGroup
                id={`question-${index}`}
                onValueChange={(value) => setAnswers(prev => ({ ...prev, [index]: value }))}
                className="flex space-x-4 justify-center"
              >
                {[1, 2, 3, 4, 5].map((value) => (
                  <div key={value} className="flex items-center space-x-1">
                    <RadioGroupItem value={value.toString()} id={`q${index}-${value}`} />
                    <Label htmlFor={`q${index}-${value}`}>{value}</Label>
                  </div>
                ))}
              </RadioGroup>
            </div>
          ))}
        </CardContent>
        <CardFooter className="justify-center mt-5">
          <Button type="submit" className="">Submit Feedback</Button>
        </CardFooter>
      </form>
    </Card>
  )
}