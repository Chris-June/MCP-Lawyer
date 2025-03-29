import React, { useState } from 'react'

// Use a CommonJS require for react-hook-form to avoid TypeScript issues
const reactHookForm = require('react-hook-form')
import { useMutation } from '@tanstack/react-query'
import { analyzePredictiveOutcome } from '@/lib/legalToolsApi'
import { PredictiveAnalysisRequest } from '@/types'
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

const PredictiveOutcomeAnalysis: React.FC<PredictiveOutcomeAnalysisProps> = () => {
  const { toast } = useToast()
  const [showResults, setShowResults] = useState(false)
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

  // Define the type for useForm to avoid TypeScript errors
  type UseFormType = any
  // Cast useForm to any to avoid TypeScript errors with generic parameters
  const { register, handleSubmit, formState: { errors }, watch, setValue } = (reactHookForm.useForm as UseFormType)({
    defaultValues: {
      case_facts: '',
      legal_issues: [],
      jurisdiction: 'Ontario',
      relevant_statutes: [],
      similar_cases: [],
      client_position: '',
      opposing_arguments: ''
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
    mutationFn: (data: PredictiveAnalysisRequest) => analyzePredictiveOutcome(data),
    onSuccess: () => {
      toast({
        title: 'Analysis Complete',
        description: 'Predictive case outcome analysis has been generated.',
      })
      setShowResults(true)
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to analyze case outcome',
      })
    }
  })

  const onSubmit = (data: PredictiveAnalysisRequest) => {
    mutation.mutate(data)
  }

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

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Predictive Case Outcome Analysis</h1>
          <p className="text-muted-foreground mt-2">
            Analyze potential case outcomes based on similar precedents and legal factors
          </p>
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
                  {...register('case_facts', { required: 'Case facts are required' })}
                />
                {errors.case_facts && (
                  <p className="text-sm text-destructive">{errors.case_facts.message}</p>
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
                {errors.legal_issues && (
                  <p className="text-sm text-destructive">{errors.legal_issues.message}</p>
                )}
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('legal_issues')?.map((issue: any, index: number) => (
                    <Badge key={index} variant="secondary" className="flex items-center gap-1 py-1.5">
                      {issue}
                      <button
                        type="button"
                        onClick={() => removeItem('legal_issues', index)}
                        className="ml-1 text-muted-foreground hover:text-foreground"
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
                {watch('legal_issues')?.length === 0 && (
                  <p className="text-sm text-muted-foreground">At least one legal issue is required</p>
                )}
              </div>

              {/* Jurisdiction */}
              <div className="space-y-2">
                <Label htmlFor="jurisdiction" className="text-base font-medium">
                  Jurisdiction <span className="text-destructive">*</span>
                </Label>
                <select
                  id="jurisdiction"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  {...register('jurisdiction', { required: 'Jurisdiction is required' })}
                >
                  {jurisdictions.map((jurisdiction) => (
                    <option key={jurisdiction} value={jurisdiction}>
                      {jurisdiction}
                    </option>
                  ))}
                </select>
                {errors.jurisdiction && (
                  <p className="text-sm text-destructive">{errors.jurisdiction.message}</p>
                )}
              </div>

              {/* Client Position */}
              <div className="space-y-2">
                <Label htmlFor="client_position" className="text-base font-medium">
                  Client's Position <span className="text-destructive">*</span>
                </Label>
                <Textarea
                  id="client_position"
                  placeholder="Describe your client's position or arguments..."
                  className="min-h-[100px]"
                  {...register('client_position', { required: "Client's position is required" })}
                />
                {errors.client_position && (
                  <p className="text-sm text-destructive">{errors.client_position.message}</p>
                )}
              </div>

              {/* Opposing Arguments */}
              <div className="space-y-2">
                <Label htmlFor="opposing_arguments" className="text-base font-medium">
                  Opposing Arguments
                </Label>
                <Textarea
                  id="opposing_arguments"
                  placeholder="Describe the opposing party's arguments (if known)..."
                  className="min-h-[100px]"
                  {...register('opposing_arguments')}
                />
              </div>

              {/* Relevant Statutes */}
              <div className="space-y-2">
                <Label className="text-base font-medium">Relevant Statutes</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter a statute..."
                    value={statuteInput}
                    onChange={(e) => setStatuteInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addStatute())}
                  />
                  <Button type="button" onClick={addStatute} variant="outline">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('relevant_statutes')?.map((statute: any, index: number) => (
                    <Badge key={index} variant="outline" className="flex items-center gap-1 py-1.5">
                      {statute}
                      <button
                        type="button"
                        onClick={() => removeItem('relevant_statutes', index)}
                        className="ml-1 text-muted-foreground hover:text-foreground"
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Similar Cases */}
              <div className="space-y-2">
                <Label className="text-base font-medium">Similar Cases</Label>
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter a case citation..."
                    value={caseInput}
                    onChange={(e) => setCaseInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCase())}
                  />
                  <Button type="button" onClick={addCase} variant="outline">
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {watch('similar_cases')?.map((caseItem: any, index: number) => (
                    <Badge key={index} variant="outline" className="flex items-center gap-1 py-1.5">
                      {caseItem}
                      <button
                        type="button"
                        onClick={() => removeItem('similar_cases', index)}
                        className="ml-1 text-muted-foreground hover:text-foreground"
                      >
                        ×
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <Button
                  type="submit"
                  disabled={mutation.isPending}
                  className="min-w-[150px]"
                >
                  {mutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <BarChart className="mr-2 h-4 w-4" />
                      Analyze Case
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Results Section */}
          {mutation.data && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="overflow-hidden">
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-center">
                    <CardTitle className="text-xl font-bold flex items-center gap-2">
                      <Scale className="h-5 w-5 text-primary" />
                      <span>Outcome Analysis</span>
                    </CardTitle>
                    <Button variant="outline" size="sm" onClick={() => setShowResults(false)}>
                      New Analysis
                    </Button>
                  </div>
                  <CardDescription>
                    Based on {watch('jurisdiction')} jurisdiction and similar precedents
                  </CardDescription>
                </CardHeader>

                <CardContent className="pb-8">
                  <Tabs defaultValue="summary" className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="summary">Summary</TabsTrigger>
                      <TabsTrigger value="prediction">Prediction</TabsTrigger>
                      <TabsTrigger value="precedents">Precedents</TabsTrigger>
                      <TabsTrigger value="strategies">Strategies</TabsTrigger>
                    </TabsList>

                    {/* Summary Tab */}
                    <TabsContent value="summary" className="space-y-6 pt-4">
                      <div className="prose prose-sm max-w-none">
                        <h3 className="text-lg font-medium">Case Summary</h3>
                        <p>{mutation.data.case_summary}</p>
                      </div>

                      <div className="grid gap-6 md:grid-cols-2">
                        <Card className="overflow-hidden">
                          <CardHeader className="pb-2 pt-4">
                            <CardTitle className="text-base font-medium flex items-center gap-2">
                              <TrendingUp className="h-4 w-4 text-amber-500" />
                              <span>Outcome Prediction</span>
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="flex items-center justify-between">
                              <div>
                                <span className="text-3xl font-bold">
                                  {mutation.data.outcome_prediction.favorable_outcome_percentage}%
                                </span>
                                <span className="text-sm text-muted-foreground ml-2">
                                  favorable outcome
                                </span>
                              </div>
                              <Badge variant={getConfidenceBadgeVariant(mutation.data.outcome_prediction.confidence_level)}>
                                {mutation.data.outcome_prediction.confidence_level} confidence
                              </Badge>
                            </div>
                            <Progress 
                              value={mutation.data.outcome_prediction.favorable_outcome_percentage} 
                              className="h-2 mt-2" 
                            />
                          </CardContent>
                        </Card>

                        <Card className="overflow-hidden">
                          <CardHeader className="pb-2 pt-4">
                            <CardTitle className="text-base font-medium flex items-center gap-2">
                              <ListChecks className="h-4 w-4 text-green-500" />
                              <span>SWOT Analysis</span>
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="grid grid-cols-2 gap-3 text-sm">
                              <div>
                                <p className="font-medium text-green-600">Strengths</p>
                                <p className="text-muted-foreground">
                                  {mutation.data.strength_weakness_analysis.strengths.length} identified
                                </p>
                              </div>
                              <div>
                                <p className="font-medium text-red-600">Weaknesses</p>
                                <p className="text-muted-foreground">
                                  {mutation.data.strength_weakness_analysis.weaknesses.length} identified
                                </p>
                              </div>
                              <div>
                                <p className="font-medium text-blue-600">Opportunities</p>
                                <p className="text-muted-foreground">
                                  {mutation.data.strength_weakness_analysis.opportunities.length} identified
                                </p>
                              </div>
                              <div>
                                <p className="font-medium text-amber-600">Threats</p>
                                <p className="text-muted-foreground">
                                  {mutation.data.strength_weakness_analysis.threats.length} identified
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>

                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertTitle>Disclaimer</AlertTitle>
                        <AlertDescription className="text-sm">
                          {mutation.data.disclaimer}
                        </AlertDescription>
                      </Alert>
                    </TabsContent>

                    {/* Prediction Tab */}
                    <TabsContent value="prediction" className="space-y-6 pt-4">
                      <div className="prose prose-sm max-w-none">
                        <h3 className="text-lg font-medium">Prediction Rationale</h3>
                        <p>{mutation.data.outcome_prediction.prediction_rationale}</p>
                      </div>

                      <div className="space-y-4">
                        <h3 className="text-lg font-medium">Alternative Outcomes</h3>
                        {mutation.data.alternative_outcomes.map((outcome, index) => (
                          <Card key={index} className="overflow-hidden">
                            <CardContent className="pt-4">
                              <div className="flex justify-between items-start gap-4">
                                <div className="flex-1">
                                  <h4 className="font-medium">{outcome.scenario}</h4>
                                  <p className="text-sm text-muted-foreground mt-1">{outcome.impact}</p>
                                </div>
                                <Badge variant="outline" className="text-sm">
                                  {outcome.probability}% probability
                                </Badge>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>

                      <div className="space-y-4">
                        <h3 className="text-lg font-medium">SWOT Analysis</h3>
                        <div className="grid gap-4 sm:grid-cols-2">
                          <div className="space-y-2">
                            <h4 className="font-medium text-green-600 flex items-center gap-1">
                              <CheckCircle className="h-4 w-4" /> Strengths
                            </h4>
                            <ul className="space-y-1">
                              {mutation.data.strength_weakness_analysis.strengths.map((strength, index) => (
                                <li key={index} className="text-sm">{strength}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="space-y-2">
                            <h4 className="font-medium text-red-600 flex items-center gap-1">
                              <AlertCircle className="h-4 w-4" /> Weaknesses
                            </h4>
                            <ul className="space-y-1">
                              {mutation.data.strength_weakness_analysis.weaknesses.map((weakness, index) => (
                                <li key={index} className="text-sm">{weakness}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="space-y-2">
                            <h4 className="font-medium text-blue-600 flex items-center gap-1">
                              <Lightbulb className="h-4 w-4" /> Opportunities
                            </h4>
                            <ul className="space-y-1">
                              {mutation.data.strength_weakness_analysis.opportunities.map((opportunity, index) => (
                                <li key={index} className="text-sm">{opportunity}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="space-y-2">
                            <h4 className="font-medium text-amber-600 flex items-center gap-1">
                              <AlertCircle className="h-4 w-4" /> Threats
                            </h4>
                            <ul className="space-y-1">
                              {mutation.data.strength_weakness_analysis.threats.map((threat, index) => (
                                <li key={index} className="text-sm">{threat}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    </TabsContent>

                    {/* Precedents Tab */}
                    <TabsContent value="precedents" className="space-y-6 pt-4">
                      <div className="space-y-4">
                        <h3 className="text-lg font-medium">Similar Precedents</h3>
                        {mutation.data.similar_precedents.map((precedent, index) => (
                          <Card key={index} className="overflow-hidden">
                            <CardContent className="pt-4">
                              <div className="flex justify-between items-start">
                                <h4 className="font-medium">{precedent.case_citation}</h4>
                                <Badge variant="outline">
                                  {precedent.relevance_score}% relevance
                                </Badge>
                              </div>
                              <p className="text-sm font-medium mt-2">
                                Outcome: <span className={precedent.outcome.toLowerCase().includes('favorable') ? 'text-green-600' : precedent.outcome.toLowerCase().includes('unfavorable') ? 'text-red-600' : 'text-amber-600'}>{precedent.outcome}</span>
                              </p>
                              <div className="mt-2">
                                <p className="text-sm font-medium">Key Factors:</p>
                                <ul className="text-sm mt-1 space-y-1">
                                  {precedent.key_factors.map((factor, idx) => (
                                    <li key={idx} className="text-muted-foreground">{factor}</li>
                                  ))}
                                </ul>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </TabsContent>

                    {/* Strategies Tab */}
                    <TabsContent value="strategies" className="space-y-6 pt-4">
                      <div className="space-y-4">
                        <h3 className="text-lg font-medium">Recommended Strategies</h3>
                        <div className="space-y-3">
                          {mutation.data.recommended_strategies.map((strategy, index) => (
                            <div key={index} className="flex items-start gap-2 p-3 rounded-md bg-muted/50">
                              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                              <div className="text-sm">{strategy}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}

export default PredictiveOutcomeAnalysis
