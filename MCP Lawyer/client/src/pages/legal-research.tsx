import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BookOpen, Loader2, Search, ExternalLink, BookMarked, HelpCircle } from 'lucide-react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

import { analyzeLegalIssue } from '@/lib/api'
import { AnalyzeLegalIssueRequest } from '@/types'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/components/ui/use-toast'

const jurisdictions = [
  { value: 'ontario', label: 'Ontario' },
  { value: 'british_columbia', label: 'British Columbia' },
  { value: 'alberta', label: 'Alberta' },
  { value: 'quebec', label: 'Quebec' },
  { value: 'federal', label: 'Federal' },
]

const practiceAreas = [
  { value: 'general', label: 'General' },
  { value: 'family', label: 'Family Law' },
  { value: 'real_estate', label: 'Real Estate' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'litigation', label: 'Litigation' },
  { value: 'estates', label: 'Wills & Estates' },
  { value: 'civil', label: 'Civil Law' },
  { value: 'immigration', label: 'Immigration' },
]

const legalDatabases = [
  {
    name: 'CanLII',
    description: 'Canadian Legal Information Institute',
    url: 'https://www.canlii.org/',
    icon: <BookOpen className="h-5 w-5 text-primary" />,
  },
  {
    name: 'Westlaw Canada',
    description: 'Comprehensive legal research database',
    url: 'https://www.westlaw.com/',
    icon: <BookMarked className="h-5 w-5 text-primary" />,
  },
  {
    name: 'LexisNexis Quicklaw',
    description: 'Comprehensive legal research database',
    url: 'https://www.lexisnexis.ca/',
    icon: <BookMarked className="h-5 w-5 text-primary" />,
  },
]

export default function LegalResearchPage() {
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  
  // Legal Issue Analysis State
  const [analysisRequest, setAnalysisRequest] = useState<AnalyzeLegalIssueRequest>({
    issue_description: '',
    jurisdiction: '',
    practice_area: '',
  })
  const [analysisResult, setAnalysisResult] = useState<string>('')
  
  // Analyze Legal Issue Mutation
  const analyzeLegalIssueMutation = useMutation({
    mutationFn: analyzeLegalIssue,
    onSuccess: (data) => {
      setAnalysisResult(data.analysis)
      toast({
        title: 'Analysis Complete',
        description: 'Your legal issue has been analyzed successfully.',
      })
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: `Failed to analyze legal issue: ${error.message}`,
        variant: 'destructive',
      })
    },
  })
  
  const handleAnalysisInputChange = (field: keyof AnalyzeLegalIssueRequest, value: string) => {
    setAnalysisRequest(prev => ({
      ...prev,
      [field]: value
    }))
  }
  
  const handleAnalyzeLegalIssue = () => {
    analyzeLegalIssueMutation.mutate(analysisRequest)
  }
  
  const handleSearch = () => {
    // In a real app, this would search legal databases
    toast({
      title: 'Search Initiated',
      description: `Searching Canadian legal databases for "${searchQuery}"`,
    })
  }
  
  return (
    <TooltipProvider>
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2">Canadian Legal Research</h1>
        <p className="text-muted-foreground mb-6">
          Access comprehensive Canadian legal research tools for Pathways Law
        </p>
      </motion.div>
      
      <Tabs defaultValue="search">
        <TabsList className="mb-4">
          <TabsTrigger value="search">Search Legal Databases</TabsTrigger>
          <TabsTrigger value="analysis">Legal Issue Analysis</TabsTrigger>
          <TabsTrigger value="resources">Research Resources</TabsTrigger>
        </TabsList>
        
        <TabsContent value="search">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Canadian Legal Database Search
              </CardTitle>
              <CardDescription>
                Search across Canadian legal databases for cases, statutes, and commentary
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Label htmlFor="search-query">Search Terms</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Enter case names, legal topics, or statute references</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Input
                      id="search-query"
                      placeholder="E.g., R v Smith, limitation periods, Family Law Act"
                      value={searchQuery}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <Button onClick={handleSearch} disabled={!searchQuery.trim()}>
                    Search
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="jurisdiction">Jurisdiction</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Filter results by Canadian province or federal jurisdiction</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Select>
                      <SelectTrigger id="jurisdiction">
                        <SelectValue placeholder="All Jurisdictions" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Jurisdictions</SelectItem>
                        {jurisdictions.map(jurisdiction => (
                          <SelectItem key={jurisdiction.value} value={jurisdiction.value}>
                            {jurisdiction.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label htmlFor="content-type">Content Type</Label>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <HelpCircle className="h-4 w-4 text-muted-foreground" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Filter by type of legal document or resource</p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                    <Select>
                      <SelectTrigger id="content-type">
                        <SelectValue placeholder="All Content Types" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Content Types</SelectItem>
                        <SelectItem value="cases">Cases</SelectItem>
                        <SelectItem value="legislation">Legislation</SelectItem>
                        <SelectItem value="commentary">Commentary</SelectItem>
                        <SelectItem value="forms">Forms & Precedents</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <div className="text-sm text-muted-foreground">
                Searches Canadian legal databases including CanLII, Westlaw, and LexisNexis
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  Advanced Search
                </Button>
                <Button variant="outline" size="sm">
                  Search History
                </Button>
              </div>
            </CardFooter>
          </Card>
          
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-4">Search Results</h3>
            <div className="text-center py-12 text-muted-foreground">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-20" />
              <p>Enter a search query to find relevant Canadian legal resources</p>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="analysis">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  Legal Issue Analysis
                </CardTitle>
                <CardDescription>
                  Get AI-powered analysis of Canadian legal issues
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="issue-description">Issue Description</Label>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <HelpCircle className="h-4 w-4 text-muted-foreground" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Provide a detailed description of your legal issue or question</p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Textarea
                    id="issue-description"
                    placeholder="Describe the legal issue in detail..."
                    value={analysisRequest.issue_description}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleAnalysisInputChange('issue_description', e.target.value)}
                    rows={6}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="analysis-jurisdiction">Jurisdiction</Label>
                  <Select
                    value={analysisRequest.jurisdiction}
                    onValueChange={(value: string) => handleAnalysisInputChange('jurisdiction', value)}
                  >
                    <SelectTrigger id="analysis-jurisdiction">
                      <SelectValue placeholder="Select jurisdiction" />
                    </SelectTrigger>
                    <SelectContent>
                      {jurisdictions.map(jurisdiction => (
                        <SelectItem key={jurisdiction.value} value={jurisdiction.value}>
                          {jurisdiction.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="practice-area">Practice Area</Label>
                  <Select
                    value={analysisRequest.practice_area}
                    onValueChange={(value: string) => handleAnalysisInputChange('practice_area', value)}
                  >
                    <SelectTrigger id="practice-area">
                      <SelectValue placeholder="Select practice area" />
                    </SelectTrigger>
                    <SelectContent>
                      {practiceAreas.map(area => (
                        <SelectItem key={area.value} value={area.value}>
                          {area.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  onClick={handleAnalyzeLegalIssue}
                  disabled={
                    analyzeLegalIssueMutation.isPending || 
                    !analysisRequest.issue_description || 
                    !analysisRequest.jurisdiction || 
                    !analysisRequest.practice_area
                  }
                >
                  {analyzeLegalIssueMutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Analyze Issue
                </Button>
              </CardFooter>
            </Card>
            
            {analysisResult ? (
              <Card>
                <CardHeader>
                  <CardTitle>Legal Analysis</CardTitle>
                  <CardDescription>
                    Analysis for {practiceAreas.find(p => p.value === analysisRequest.practice_area)?.label} issue 
                    in {jurisdictions.find(j => j.value === analysisRequest.jurisdiction)?.label}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <div dangerouslySetInnerHTML={{ __html: analysisResult.replace(/\n/g, '<br>') }} />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button
                    variant="outline"
                    onClick={() => {
                      // In a real app, this would save the analysis
                      toast({
                        title: 'Analysis Saved',
                        description: 'The legal analysis has been saved to your documents.',
                      })
                    }}
                  >
                    Save Analysis
                  </Button>
                </CardFooter>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Analysis Results</CardTitle>
                  <CardDescription>
                    Complete the form to generate a legal analysis
                  </CardDescription>
                </CardHeader>
                <CardContent className="py-12 text-center">
                  <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-20" />
                  <p className="text-muted-foreground">Your legal analysis will appear here</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="resources">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Canadian Legal Research Databases</CardTitle>
                <CardDescription>
                  Access comprehensive Canadian legal research resources
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  {legalDatabases.map((database, index) => (
                    <Card key={index} className="overflow-hidden">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg flex items-center gap-2">
                          {database.icon}
                          {database.name}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pb-2">
                        <p className="text-sm text-muted-foreground">{database.description}</p>
                      </CardContent>
                      <CardFooter className="pt-2">
                        <Button variant="outline" size="sm" className="w-full" asChild>
                          <a href={database.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-1">
                            Access Database <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Canadian Legal Citation Guide</CardTitle>
                <CardDescription>
                  Reference for proper legal citation in Canadian legal documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border rounded-md p-4">
                    <h3 className="text-lg font-medium mb-2">Case Law Citation</h3>
                    <p className="text-sm mb-2">Format: <span className="font-mono bg-muted px-1 rounded">Style of Cause, [Year] Volume Reporter Page (Court)</span></p>
                    <p className="text-sm mb-2">Example: <span className="font-mono bg-muted px-1 rounded">R v Smith, [2020] 1 SCR 123 (SCC)</span></p>
                  </div>
                  
                  <div className="border rounded-md p-4">
                    <h3 className="text-lg font-medium mb-2">Legislation Citation</h3>
                    <p className="text-sm mb-2">Format: <span className="font-mono bg-muted px-1 rounded">Title, Statute Volume (Jurisdiction), Year, Chapter</span></p>
                    <p className="text-sm mb-2">Example: <span className="font-mono bg-muted px-1 rounded">Criminal Code, RSC 1985, c C-46</span></p>
                  </div>
                  
                  <div className="border rounded-md p-4">
                    <h3 className="text-lg font-medium mb-2">Secondary Sources Citation</h3>
                    <p className="text-sm mb-2">Format: <span className="font-mono bg-muted px-1 rounded">Author, Title, (Year) Volume Journal Page</span></p>
                    <p className="text-sm mb-2">Example: <span className="font-mono bg-muted px-1 rounded">John Smith, "Legal Ethics", (2019) 45 Canadian Bar Review 123</span></p>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" size="sm">
                  Download Complete Citation Guide
                </Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
    </TooltipProvider>
  )
}
