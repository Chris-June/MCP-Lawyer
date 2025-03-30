import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useMutation } from '@tanstack/react-query'
import { analyzePredictiveOutcome } from '@/lib/legalToolsApi'
import { PredictiveAnalysisRequest, PredictiveAnalysisResponse } from '@/types/legalTools'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/components/ui/use-toast'
import { motion } from 'framer-motion'
import { 
  BarChart, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  Loader2, 
  Scale, 
  TrendingUp, 
  Lightbulb,
  ListChecks,
  Gavel
} from 'lucide-react'

interface PredictiveOutcomeAnalysisProps {}

const predictiveAnalysisSchema = z.object({
  case_facts: z.string().min(10, { message: "Case facts must be at least 10 characters long" }),
  legal_issues: z.array(z.string()).min(1, { message: "At least one legal issue is required" }),
  jurisdiction: z.string().min(1, { message: "Jurisdiction is required" }),
  relevant_statutes: z.array(z.string()).optional(),
  similar_cases: z.array(z.string()).optional(),
  client_position: z.string().optional(),
  opposing_arguments: z.string().optional()
})

const PredictiveOutcomeAnalysis: React.FC<PredictiveOutcomeAnalysisProps> = () => {
  const { toast } = useToast()
  const [showResults, setShowResults] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<PredictiveAnalysisResponse | null>(null)
  const [jurisdictions] = useState([
    'Federal',
    'Alberta',
    'British Columbia',
    'Manitoba',
    'New Brunswick',
    'Newfoundland and Labrador',
    'Nova Scotia',
    'Ontario',
    'Prince Edward Island',
    'Quebec',
    'Saskatchewan',
    'Northwest Territories',
    'Nunavut',
    'Yukon'
  ])

  // Use Zod resolver with react-hook-form
  const { 
    register, 
    handleSubmit, 
    formState: { errors }, 
    watch, 
    setValue 
  } = useForm<PredictiveAnalysisRequest>({
    resolver: zodResolver(predictiveAnalysisSchema),
    defaultValues: {
      legal_issues: [],
      relevant_statutes: [],
      similar_cases: []
    }
  })

  const [legalIssueInput, setLegalIssueInput] = useState('')
  const [statuteInput, setStatuteInput] = useState('')
  const [caseInput, setCaseInput] = useState('')
  
  // Add legal issue to the array
  const addLegalIssue = () => {
    if (legalIssueInput.trim()) {
      const currentIssues = watch('legal_issues') || []
      setValue('legal_issues', [...currentIssues, legalIssueInput.trim()])
      setLegalIssueInput('')
    }
  }
  
  // Add statute to the array
  const addStatute = () => {
    if (statuteInput.trim()) {
      const currentStatutes = watch('relevant_statutes') || []
      setValue('relevant_statutes', [...currentStatutes, statuteInput.trim()])
      setStatuteInput('')
    }
  }
  
  // Add case to the array
  const addCase = () => {
    if (caseInput.trim()) {
      const currentCases = watch('similar_cases') || []
      setValue('similar_cases', [...currentCases, caseInput.trim()])
      setCaseInput('')
    }
  }
  
  // Remove item from an array
  const removeItem = (array: string, index: number) => {
    const currentItems = watch(array as any) || []
    setValue(array as any, currentItems.filter((_: any, i: number) => i !== index))
  }

  const mutation = useMutation({
    mutationFn: (data: PredictiveAnalysisRequest) => {
      console.log('Mutation Data:', data);
      return analyzePredictiveOutcome(data);
    },
    onSuccess: (result: PredictiveAnalysisResponse) => {
      console.log('Full Analysis Result:', JSON.stringify(result, null, 2));
      console.log('Outcome Prediction:', result.outcome_prediction);
      
      toast({
        title: 'Analysis Complete',
        description: 'Predictive case outcome analysis has been generated.',
      })
      setAnalysisResult(result)
      setShowResults(true)
    },
    onError: (error) => {
      console.error('Mutation Error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to analyze case outcome';
      
      toast({
        variant: 'destructive',
        title: 'Error',
        description: errorMessage,
      })
      
      // Create a complete error response that matches PredictiveAnalysisResponse
      setAnalysisResult({
        case_summary: 'Unable to generate case summary due to an error.',
        outcome_prediction: {
          favorable_outcome_percentage: 0,
          confidence_level: 'low',
          prediction_rationale: errorMessage
        },
        similar_precedents: [],
        strength_weakness_analysis: {
          strengths: [],
          weaknesses: [],
          opportunities: [],
          threats: []
        },
        recommended_strategies: [],
        alternative_outcomes: [],
        disclaimer: 'This analysis could not be completed due to an unexpected error.'
      })
    }
  })
  
  // Submit handler
  const onSubmit = (data: PredictiveAnalysisRequest) => {
    console.log('Form Data Submitted:', data);
    mutation.mutate(data)
  }

  useEffect(() => {
    console.log('Analysis Result Updated:', analysisResult);
    console.log('Show Results:', showResults);
  }, [analysisResult, showResults])

  const getConfidenceBadgeVariant = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'default'
      case 'medium':
        return 'secondary'
      case 'low':
        return 'outline'
      default:
        return 'secondary'
    }
  }

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    // Check if the result is an error response
    if (analysisResult.case_summary === 'Unable to generate case summary due to an error.') {
      return (
        <div className="text-red-500 space-y-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Analysis Error</AlertTitle>
            <AlertDescription>
              {analysisResult.outcome_prediction.prediction_rationale}
            </AlertDescription>
          </Alert>

          {analysisResult.disclaimer && (
            <div className="text-sm text-muted-foreground italic">
              {analysisResult.disclaimer}
            </div>
          )}
        </div>
      );
    }

    // Render successful analysis
    return (
      <div className="space-y-4">
        {analysisResult.case_summary && (
          <div>
            <h3 className="font-bold">Case Summary</h3>
            <div>{analysisResult.case_summary}</div>
          </div>
        )}

        {analysisResult.outcome_prediction && (
          <div>
            <h3 className="font-bold">Outcome Prediction</h3>
            <div>Favorable Outcome: {analysisResult.outcome_prediction.favorable_outcome_percentage}%</div>
            <div>
              Confidence Level: 
              <div className="inline-block ml-2">
                <Badge 
                  variant={getConfidenceBadgeVariant(analysisResult.outcome_prediction.confidence_level)}
                >
                  {analysisResult.outcome_prediction.confidence_level}
                </Badge>
              </div>
            </div>
            <div>Rationale: {analysisResult.outcome_prediction.prediction_rationale}</div>
          </div>
        )}

        {analysisResult.similar_precedents && analysisResult.similar_precedents.length > 0 && (
          <div>
            <h3 className="font-bold">Similar Precedents</h3>
            <div className="space-y-2">
              {analysisResult.similar_precedents.map((precedent, index) => (
                <div key={index} className="bg-muted/50 p-3 rounded-md">
                  <div className="flex justify-between items-center">
                    <h4 className="font-medium">{precedent.case_citation}</h4>
                    <Badge variant="outline">
                      {precedent.relevance_score}% relevance
                    </Badge>
                  </div>
                  <div className="text-sm mt-1">
                    Outcome: <div className={
                      precedent.outcome.toLowerCase().includes('favorable') ? 'text-green-600' : 
                      precedent.outcome.toLowerCase().includes('unfavorable') ? 'text-red-600' : 
                      'text-amber-600'
                    }>
                      {precedent.outcome}
                    </div>
                  </div>
                  {precedent.key_factors && precedent.key_factors.length > 0 && (
                    <div className="mt-2">
                      <div className="text-sm font-medium">Key Factors:</div>
                      <ul className="text-sm mt-1 space-y-1 text-muted-foreground">
                        {precedent.key_factors.map((factor, idx) => (
                          <li key={idx}>{factor}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {analysisResult.strength_weakness_analysis && (
          <div>
            <h3 className="font-bold">SWOT Analysis</h3>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <h4 className="font-medium text-green-600 flex items-center gap-1">
                  <CheckCircle className="h-4 w-4" /> Strengths
                </h4>
                <ul className="space-y-1">
                  {analysisResult.strength_weakness_analysis.strengths.map((strength, index) => (
                    <li key={index} className="text-sm">{strength}</li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-red-600 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" /> Weaknesses
                </h4>
                <ul className="space-y-1">
                  {analysisResult.strength_weakness_analysis.weaknesses.map((weakness, index) => (
                    <li key={index} className="text-sm">{weakness}</li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-blue-600 flex items-center gap-1">
                  <Lightbulb className="h-4 w-4" /> Opportunities
                </h4>
                <ul className="space-y-1">
                  {analysisResult.strength_weakness_analysis.opportunities.map((opportunity, index) => (
                    <li key={index} className="text-sm">{opportunity}</li>
                  ))}
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-amber-600 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" /> Threats
                </h4>
                <ul className="space-y-1">
                  {analysisResult.strength_weakness_analysis.threats.map((threat, index) => (
                    <li key={index} className="text-sm">{threat}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {analysisResult.recommended_strategies && analysisResult.recommended_strategies.length > 0 && (
          <div>
            <h3 className="font-bold">Recommended Strategies</h3>
            <div className="space-y-3">
              {analysisResult.recommended_strategies.map((strategy, index) => (
                <div key={index} className="flex items-start gap-2 p-3 rounded-md bg-muted/50">
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                  <div className="text-sm">{strategy}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {analysisResult.alternative_outcomes && analysisResult.alternative_outcomes.length > 0 && (
          <div>
            <h3 className="font-bold">Alternative Outcomes</h3>
            <div className="space-y-3">
              {analysisResult.alternative_outcomes.map((outcome, index) => (
                <div key={index} className="bg-muted/50 p-3 rounded-md">
                  <div className="flex justify-between items-start gap-4">
                    <div className="flex-1">
                      <h4 className="font-medium">{outcome.scenario}</h4>
                      <div className="text-sm text-muted-foreground mt-1">{outcome.impact}</div>
                    </div>
                    <div>
                      <Badge variant="outline" className="text-sm">
                        {outcome.probability}% probability
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {analysisResult.disclaimer && (
          <div className="text-sm text-gray-500 italic">
            {analysisResult.disclaimer}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Predictive Case Outcome Analysis</h1>
          <div className="text-muted-foreground mt-2">
            Analyze potential case outcomes based on similar precedents and legal factors
          </div>
        </div>
        <Scale className="h-12 w-12 text-primary opacity-80" />
      </div>

      <Separator className="my-6" />

      {!showResults ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gavel className="h-5 w-5" />
              <span>Case Details</span>
            </CardTitle>
            <CardDescription>
              Enter the details of your case to generate a predictive outcome analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              {/* Case Facts */}
              <div className="space-y-2">
                <Label htmlFor="case_facts" className="text-base font-medium">
                  Case Facts <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="case_facts"
                  placeholder="Describe the key facts of the case..."
                  className="min-h-[150px]"
                  {...register('case_facts')}
                />
                {errors.case_facts && (
                  <div className="text-sm text-destructive">
                    {errors.case_facts.message}
                  </div>
                )}
              </div>

              {/* Legal Issues */}
              <div className="space-y-2">
                <Label className="text-base font-medium">
                  Legal Issues <span className="text-destructive">*</span>
                </Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter a legal issue..."
                    value={legalIssueInput}
                    onChange={(e) => setLegalIssueInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addLegalIssue())}
                  />
                  <Button type="button" onClick={addLegalIssue} variant="outline">
                    Add
                  </Button>
                </div>
                {/* Render added legal issues */}
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('legal_issues')?.map((issue: string, index: number) => (
                    <div key={index} className="flex items-center">
                      <Badge variant="secondary" className="flex items-center">
                        {issue}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="ml-1 h-4 w-4 p-0"
                          onClick={() => removeItem('legal_issues', index)}
                        >
                          ✕
                        </Button>
                      </Badge>
                    </div>
                  ))}
                </div>
                {errors.legal_issues && (
                  <div className="text-sm text-destructive">
                    {errors.legal_issues.message}
                  </div>
                )}
              </div>

              {/* Jurisdiction */}
              <div className="space-y-2">
                <Label htmlFor="jurisdiction" className="text-base font-medium">
                  Jurisdiction <span className="text-destructive">*</span>
                </Label>
                <select
                  id="jurisdiction"
                  {...register('jurisdiction')}
                  className="w-full p-2 border rounded"
                >
                  {jurisdictions.map((jur) => (
                    <option key={jur} value={jur}>
                      {jur}
                    </option>
                  ))}
                </select>
                {errors.jurisdiction && (
                  <div className="text-sm text-destructive">
                    {errors.jurisdiction.message}
                  </div>
                )}
              </div>

              {/* Relevant Statutes */}
              <div className="space-y-2">
                <Label className="text-base font-medium">Relevant Statutes</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter a relevant statute..."
                    value={statuteInput}
                    onChange={(e) => setStatuteInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addStatute())}
                  />
                  <Button type="button" onClick={addStatute} variant="outline">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('relevant_statutes')?.map((statute: string, index: number) => (
                    <div key={index} className="flex items-center">
                      <Badge variant="secondary" className="flex items-center">
                        {statute}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="ml-1 h-4 w-4 p-0"
                          onClick={() => removeItem('relevant_statutes', index)}
                        >
                          ✕
                        </Button>
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Similar Cases */}
              <div className="space-y-2">
                <Label className="text-base font-medium">Similar Cases</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter a similar case..."
                    value={caseInput}
                    onChange={(e) => setCaseInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCase())}
                  />
                  <Button type="button" onClick={addCase} variant="outline">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('similar_cases')?.map((similarCase: string, index: number) => (
                    <div key={index} className="flex items-center">
                      <Badge variant="secondary" className="flex items-center">
                        {similarCase}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="ml-1 h-4 w-4 p-0"
                          onClick={() => removeItem('similar_cases', index)}
                        >
                          ✕
                        </Button>
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Client Position */}
              <div className="space-y-2">
                <Label htmlFor="client_position" className="text-base font-medium">
                  Client Position
                </Label>
                <Textarea
                  id="client_position"
                  placeholder="Describe the client's position..."
                  {...register('client_position')}
                />
              </div>

              {/* Opposing Arguments */}
              <div className="space-y-2">
                <Label htmlFor="opposing_arguments" className="text-base font-medium">
                  Opposing Arguments
                </Label>
                <Textarea
                  id="opposing_arguments"
                  placeholder="Describe potential opposing arguments..."
                  {...register('opposing_arguments')}
                />
              </div>

              <div className="flex justify-end">
                <Button type="submit" className="w-full" disabled={mutation.isPending}>
                  {mutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing Case...
                    </>
                  ) : (
                    'Analyze Case'
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Case Outcome Analysis</h2>
            <Button variant="outline" onClick={() => setShowResults(false)}>
              Analyze Another Case
            </Button>
          </div>
          
          {renderAnalysisResult()}
        </motion.div>
      )}
    </div>
  )
}

export default PredictiveOutcomeAnalysis
