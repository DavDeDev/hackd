"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Id } from "@/convex/_generated/dataModel"
import { useMutation } from "convex/react"
import { useEffect, useRef, useState } from "react"
import { api } from "../../../convex/_generated/api"
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

export default function Component({ viewer }: { viewer: Id<"users"> }) {
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const formRef = useRef<HTMLFormElement>(null)
  const submitResponses = useMutation(api.surveyResponse.submitSurveyResponses )
 
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1)
      setCurrentQuestionIndex(0)
    } else {
      const formattedResponses = Object.entries(answers).map(([questionId, value]) => ({
        body: value, 
        author: viewer  // Example author, replace with actual author
      }))
      
      console.log("Submitted answers:", formattedResponses)
      submitResponses({ responses: formattedResponses })
    }
  }

  const handlePrevious = () => {
    setCurrentPage(currentPage - 1)
    setCurrentQuestionIndex(questionsPerPage - 1)
  }

  const handleAnswer = (questionId: number, value: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
    if (currentQuestionIndex < questionsPerPage - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  useEffect(() => {
    const currentQuestionElement = formRef.current?.querySelector(`#question-${currentQuestionIndex}`)
    if (currentQuestionElement) {
      currentQuestionElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [currentQuestionIndex])

  const startIndex = (currentPage - 1) * questionsPerPage
  const endIndex = startIndex + questionsPerPage
  const currentQuestions = questions.slice(startIndex, endIndex)

  return (
    <Card className="w-3/4 mx-auto bg-white shadow-xl rounded-lg transition-all">
      <CardHeader className="text-center">
        <CardTitle className="text-3xl mb-2 font-bold text-gray-700">Hackathon Participant Survey</CardTitle>
        <CardDescription className="text-lg text-gray-600">Please answer the following questions on a scale from strongly disagree to strongly agree.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit} ref={formRef}>
        <CardContent className="space-y-10">
          <Progress value={(currentPage / totalPages) * 100} className="w-full h-2 bg-gray-300 rounded-full" />
          {currentQuestions.map((question, index) => (
            <div key={question.id} id={`question-${index}`} className={`space-y-6 transition-opacity duration-500 ${index === currentQuestionIndex ? 'opacity-100' : 'opacity-50'}`}>
              <Label htmlFor={`question-${question.id}`} className="text-center block text-xl font-medium text-gray-800">{question.text}</Label>
              <div className="flex items-center justify-between px-6">
                <span className="text-lg font-medium text-purple-400">Disagree</span>
                <RadioGroup
                  id={`question-${question.id}`}
                  onValueChange={(value: any) => handleAnswer(question.id, value)}
                  className="flex justify-center items-center space-x-6"
                >
                  {[1, 2, 3, 4, 5].map((value) => (
                    <div 
                      key={value} 
                      className={`flex flex-col items-center space-y-1 transition-transform ${
                        value === 1 || value === 5 ? 'scale-125' : 
                        value === 2 || value === 4 ? 'scale-110' : ''
                      }`}
                    >
                      <RadioGroupItem
                        key={value}
                        value={value.toString()}
                        id={`q${question.id}-${value}`}
                        className={`h-8 w-8 rounded-full transition-colors duration-300 ${
                          answers[question.id] === value.toString() 
                            ? (value <= 2 ? 'bg-[#d393f7] border-[#d393f7]' 
                            : value >= 4 ? 'bg-[#8ee9c2] border-[#8ee9c2]' 
                            : 'bg-gray-400 border-gray-400') 
                            : 'border-4 ' + (value <= 2 ? 'hover:bg-[#e4b4f9] border-[#d393f7]' 
                            : value >= 4 ? 'hover:bg-[#baf2df] border-[#8ee9c2]' 
                            : 'hover:bg-gray-200 border-gray-400')
                        }`}
                        onClick={() => handleAnswer(question.id, value.toString())}
                      />
                    </div>
                  ))}
                </RadioGroup>
                <span className="text-lg font-medium text-green-400">Agree</span>
              </div>
              <p className="text-base text-gray-500 text-center">{question.category}</p>
            </div>
          ))}
        </CardContent>
        <CardFooter className="flex justify-center space-x-4">
          {currentPage > 1 && (
            <Button type="button" variant="outline" onClick={handlePrevious} className="text-lg px-6 py-3 transition-colors duration-200 bg-white hover:bg-gray-100 rounded-lg">
              Previous
            </Button>
          )}
          <Button type="submit" className="text-lg px-6 py-3 transition-colors duration-200 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
            {currentPage < totalPages ? "Next" : "Submit"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}
