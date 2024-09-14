"use client"; 
import { Button } from '@/components/ui/button';
import { Form, FormItem } from '@/components/ui/form';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { useState } from 'react';

const SurveyForm = () => {
  const [formData, setFormData] = useState(Array(20).fill(3)); // Default score is 3 for each question

  const questions = [
    "I prefer to lead team projects.",
    "I am excited about attending multiple workshops and events at the hackathon.",
    "I enjoy brainstorming and collaborating on ideas with others.",
    "I like when my teammates have skills that complement mine.",
    "Winning the hackathon is my top priority.",
    "I am open to learning new technologies during the event.",
    "I work best under tight deadlines.",
    "I prefer working with teammates who share similar strengths.",
    "I appreciate constructive feedback on my work.",
    "I am confident in my coding abilities.",
    "I enjoy taking on challenging problems.",
    "I prefer a well-structured plan before starting a project.",
    "I am comfortable adapting to changes during the project.",
    "I like to focus on one task at a time.",
    "I am eager to help teammates who are struggling.",
    "I value creativity over functionality in projects.",
    "I believe communication is key to a successful team.",
    "I am motivated by learning rather than winning.",
    "I have experience with version control systems like GitHub.",
    "I enjoy working late hours to meet project goals."
  ];

  const handleInputChange = (index: number, value: number) => {
    const newFormData = [...formData];
    newFormData[index] = value;
    setFormData(newFormData);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(formData); // Submit logic here
  };

  return (
    <Form onSubmit={handleSubmit} className="survey-form">
      <h1>Survey</h1>
      {questions.map((question, index) => (
        <FormItem key={index} className="survey-question">
          <label>{question}</label>
          <RadioGroup
            value={formData[index]}
            onChange={(e) => handleInputChange(index, parseInt(e.target.value))}
          >
            {[1, 2, 3, 4, 5].map((value) => (
              <RadioGroupItem key={value} value={value}/>
             
            ))}
          </RadioGroup>
        </FormItem>
      ))}
      <Button type="submit">Find your match</Button>
    </Form>
  );
};

export default SurveyForm;