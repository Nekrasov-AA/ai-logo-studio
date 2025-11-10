import React, { useState, useEffect } from 'react';
import Header from '@/components/Header';
import WelcomeScreen from '@/components/WelcomeScreen';
import LogoForm from '@/components/LogoForm';
import ResultsScreen from '@/components/ResultsScreen';
import { FormData, LogoVariant, JobProgress, JobStatus } from '@/types/logo';
import { useToast } from '@/hooks/use-toast';

type AppState = 'welcome' | 'form' | 'results';

const Index = () => {
  const [state, setState] = useState<AppState>('welcome');
  const [systemStatus, setSystemStatus] = useState<'online' | 'offline' | 'warning'>('online');
  const [progress, setProgress] = useState<JobProgress>({
    status: 'queued',
    progress: 0
  });
  const [variants, setVariants] = useState<LogoVariant[]>([]);
  const { toast } = useToast();

  // Check system status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/health`);
        if (response.ok) {
          setSystemStatus('online');
        } else {
          setSystemStatus('warning');
        }
      } catch {
        setSystemStatus('offline');
      }
    };
    checkStatus();
  }, []);

  const handleGetStarted = () => {
    setState('form');
  };

  const handleFormSubmit = async (formData: FormData) => {
    setState('results');
    setProgress({ status: 'queued', progress: 0 });

    try {
      // Call the real API to generate logos
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          business_type: formData.businessName,
          preferences: {
            industry: formData.industry,
            style: formData.style,
            colors: formData.colors,
            description: formData.description
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create generation job');
      }

      const data = await response.json();
      const jobId = data.job_id;
      
      console.log('Job created successfully:', { jobId, status: data.status });
      console.log('Setting up SSE for:', `${import.meta.env.VITE_API_URL}/api/progress/${jobId}`);

      // Wait a bit before setting up SSE to ensure job is in database
      await new Promise(resolve => setTimeout(resolve, 100));

      // Alternative SSE implementation using fetch
      let sseAbortController: AbortController | null = new AbortController();
      
      const setupSSE = async () => {
        try {
          console.log('Starting SSE with fetch...');
          const response = await fetch(`${import.meta.env.VITE_API_URL}/api/progress/${jobId}`, {
            signal: sseAbortController?.signal,
            headers: {
              'Accept': 'text/event-stream',
              'Cache-Control': 'no-cache',
            }
          });

          if (!response.ok) {
            throw new Error(`SSE request failed: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('No response body reader');
          }

          const decoder = new TextDecoder();
          
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
              console.log('SSE stream ended');
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            console.log('SSE chunk received:', chunk);
            
            // Parse SSE data
            const lines = chunk.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6);
                console.log('SSE data:', data);
                
                try {
                  const payload = JSON.parse(data);
                  console.log('Parsed SSE payload:', payload);
                  
                  if (payload.stage) {
                    const progressMap: Record<string, number> = {
                      'queued': 10,
                      'generating': 40,
                      'vectorizing': 70,
                      'exporting': 90,
                      'done': 100
                    };

                    setProgress({
                      status: payload.stage,
                      progress: progressMap[payload.stage] || 0,
                      message: payload.stage === 'generating' 
                        ? `Creating ${formData.style} logos for ${formData.businessName}...`
                        : undefined
                    });

                    if (payload.stage === 'done') {
                      console.log('Generation completed, fetching results...');
                      // Fetch the results
                      fetch(`${import.meta.env.VITE_API_URL}/api/result/${jobId}`)
                        .then(res => {
                          console.log('Result response status:', res.status);
                          return res.json();
                        })
                        .then(result => {
                          console.log('Results fetched:', result);
                          setVariants(result?.variants || []);
                          
                          toast({
                            title: 'Logos generated!',
                            description: `${result?.variants?.length || 0} unique variations ready to download.`
                          });
                        })
                        .catch((error) => {
                          console.error('Failed to fetch results:', error);
                          setProgress({ 
                            status: 'error', 
                            progress: 0,
                            message: 'Failed to fetch results.' 
                          });
                        });
                      break;
                    } else if (payload.stage === 'error' || payload.stage === 'not_found') {
                      setProgress({ 
                        status: 'error', 
                        progress: 0,
                        message: payload.stage === 'not_found' ? 'Job not found. Please try again.' : 'Generation failed. Please try again.'
                      });
                      
                      toast({
                        title: payload.stage === 'not_found' ? 'Job not found' : 'Generation failed',
                        description: 'Please try again.',
                        variant: 'destructive'
                      });
                      break;
                    }
                  }
                } catch (parseError) {
                  console.error('Error parsing SSE data:', parseError);
                }
              }
            }
          }
        } catch (error) {
          if (error instanceof Error && error.name !== 'AbortError') {
            console.error('SSE error:', error);
            setProgress({ 
              status: 'error', 
              progress: 0,
              message: 'Connection error. Please try again.'
            });
            
            toast({
              title: 'Connection failed',
              description: 'Unable to track progress. Please try again.',
              variant: 'destructive'
            });
          }
        }
      };

      // Try SSE first, fallback to polling if it fails
      setupSSE().catch(async (error) => {
        console.warn('SSE failed, falling back to polling:', error);
        
        // Simple polling fallback
        const pollForResult = async () => {
          for (let i = 0; i < 30; i++) { // Poll for up to 30 seconds
            try {
              await new Promise(resolve => setTimeout(resolve, 1000));
              
              const response = await fetch(`${import.meta.env.VITE_API_URL}/api/result/${jobId}`);
              if (response.ok) {
                const result = await response.json();
                
                if (result.status === 'done') {
                  setProgress({ status: 'done', progress: 100 });
                  setVariants(result?.variants || []);
                  
                  toast({
                    title: 'Logos generated!',
                    description: `${result?.variants?.length || 0} unique variations ready to download.`
                  });
                  return;
                } else if (result.status === 'error') {
                  setProgress({ 
                    status: 'error', 
                    progress: 0,
                    message: 'Generation failed. Please try again.'
                  });
                  
                  toast({
                    title: 'Generation failed',
                    description: 'Please try again.',
                    variant: 'destructive'
                  });
                  return;
                }
                
                // Update progress for intermediate states
                const progressMap: Record<string, number> = {
                  'queued': 10,
                  'generating': 40,
                  'vectorizing': 70,
                  'exporting': 90
                };
                
                setProgress({
                  status: result.status as JobStatus,
                  progress: progressMap[result.status] || 0,
                  message: result.status === 'generating' 
                    ? `Creating ${formData.style} logos for ${formData.businessName}...`
                    : undefined
                });
              }
            } catch (pollError) {
              console.error('Polling error:', pollError);
            }
          }
          
          // Timeout
          setProgress({ 
            status: 'error', 
            progress: 0,
            message: 'Timeout. Please try again.'
          });
        };
        
        pollForResult();
      });

      // Cleanup function for component unmount
      return () => {
        if (sseAbortController) {
          sseAbortController.abort();
          sseAbortController = null;
        }
      };

    } catch (error) {
      console.error('Generation error:', error);
      console.log('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined,
        name: error instanceof Error ? error.name : undefined
      });
      
      setProgress({ 
        status: 'error', 
        progress: 0,
        message: 'Failed to generate logos. Please try again.'
      });
      
      toast({
        title: 'Generation failed',
        description: 'Unable to create logos. Please try again.',
        variant: 'destructive'
      });
    }
  };

  const handleDownload = async (variant: LogoVariant) => {
    try {
      // In production, this would fetch the actual SVG and create a blob
      const response = await fetch(variant.svg.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `logo-variant-${variant.index + 1}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Download started',
        description: `Logo variant ${variant.index + 1} is downloading.`
      });
    } catch (error) {
      toast({
        title: 'Download failed',
        description: 'Unable to download the logo. Please try again.',
        variant: 'destructive'
      });
    }
  };

  const handleBack = () => {
    if (state === 'results') {
      setState('welcome');
      setVariants([]);
      setProgress({ status: 'queued', progress: 0 });
    } else {
      setState('welcome');
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header status={systemStatus} />
      
      {state === 'welcome' && (
        <WelcomeScreen onGetStarted={handleGetStarted} />
      )}
      
      {state === 'form' && (
        <LogoForm onBack={handleBack} onSubmit={handleFormSubmit} />
      )}
      
      {state === 'results' && (
        <ResultsScreen 
          onBack={handleBack}
          progress={progress}
          variants={variants}
          onDownload={handleDownload}
        />
      )}
    </div>
  );
};

export default Index;
