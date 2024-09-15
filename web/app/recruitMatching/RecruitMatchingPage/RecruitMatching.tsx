import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { GithubIcon } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

const people = [
  {
    name: "Alice Johnson",
    description: "Full-stack developer with 5 years of experience",
    skills: ["React", "Node.js", "Python"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "alice-johnson",
    languages: { JavaScript: 50, Python: 30, HTML: 20 }
  },
  {
    name: "Bob Smith",
    description: "UX/UI designer passionate about user-centered design",
    skills: ["Figma", "Adobe XD", "Sketch"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "bob-smith",
    languages: { JavaScript: 20, CSS: 60, HTML: 20 }
  },
  {
    name: "Charlie Brown",
    description: "Data scientist specializing in machine learning",
    skills: ["Python", "TensorFlow", "SQL"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "charlie-brown",
    languages: { Python: 70, R: 20, SQL: 10 }
  },
  {
    name: "Diana Martinez",
    description: "DevOps engineer with cloud expertise",
    skills: ["AWS", "Docker", "Kubernetes"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "diana-martinez",
    languages: { Shell: 40, Python: 30, YAML: 30 }
  },
  {
    name: "Ethan Williams",
    description: "Mobile app developer focused on cross-platform solutions",
    skills: ["React Native", "Flutter", "Swift"],
    avatar: "/placeholder.svg?height=40&width=40",
    github: "ethan-williams",
    languages: { JavaScript: 40, Dart: 30, Swift: 30 }
  }
]

const LanguageBar = ({ languages }: {languages: any}) => {
  const totalPercentage = Object.values(languages).reduce((sum, value) => sum + value, 0)
  return (
    <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
      {Object.entries(languages).map(([lang, percentage], index) => (
        <div
          key={lang}
          className="h-full float-left"
          style={{
            width: `${(percentage / totalPercentage) * 100}%`,
            backgroundColor: `hsl(${index * 60}, 70%, 50%)`
          }}
        />
      ))}
    </div>
  )
}

export default function MatchingView() {
  return (
    <div className="container mx-auto p-4 space-y-8">
      <div className="flex flex-col md:flex-row gap-4">
        {/* <div className="flex-1 bg-muted rounded-lg p-4">
          <svg className="w-full h-full" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="currentColor" strokeWidth="4" fill="none" />
            <path d="M20 50 L80 50 M50 20 L50 80" stroke="currentColor" strokeWidth="4" />
          </svg>
        </div> */}
        {/* <div className="flex-1">
          <Image
            width={25}
            height={25}
            src="/placeholder.svg?height=300&width=400"
            alt="Matching illustration"
            className="w-full h-full object-cover rounded-lg"
          />
        </div> */}
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {people.map((person, index) => (
          <Card key={index} className="flex flex-col">
            <CardHeader>
              <div className="flex items-center space-x-4">
                <Avatar>
                  <AvatarImage src={person.avatar} alt={person.name} />
                  <AvatarFallback>{person.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <CardTitle>{person.name}</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="flex-grow">
              <p className="text-sm text-muted-foreground mb-4">{person.description}</p>
              <div className="flex flex-wrap gap-2 mb-4">
                {person.skills.map((skill, skillIndex) => (
                  <Badge key={skillIndex} variant="secondary">{skill}</Badge>
                ))}
              </div>
              <LanguageBar languages={person.languages} />
              <div className="text-xs text-muted-foreground mt-2">
                {Object.entries(person.languages).map(([lang, percentage], index) => (
                  <span key={lang}>
                    {lang} {percentage}%{index < Object.entries(person.languages).length - 1 ? ' · ' : ''}
                  </span>
                ))}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button variant="outline" size="sm" asChild>
                <a href={`https://github.com/${person.github}`} target="_blank" rel="noopener noreferrer">
                  <GithubIcon className="w-4 h-4 mr-2" />
                  GitHub
                </a>
              </Button>
              <Link href={'/product'}>
              <Button size="sm" >Match</Button>
              </Link>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  )
}