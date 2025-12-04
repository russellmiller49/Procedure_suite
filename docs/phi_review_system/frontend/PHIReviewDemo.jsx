import React, { useState, useCallback } from 'react';
import PHIReviewEditor from './PHIReviewEditor';

/**
 * Demo Page: Complete PHI Review Workflow
 * 
 * This demonstrates the full physician workflow:
 * 1. Enter/paste clinical note
 * 2. Click "Analyze" to detect PHI
 * 3. Review and modify PHI flags
 * 4. Submit for coding
 * 5. View results
 */

const API_BASE = 'http://localhost:8000/v1/coder';

function PHIReviewDemo() {
  // Workflow state
  const [step, setStep] = useState('input'); // 'input' | 'review' | 'processing' | 'complete'
  
  // Data state
  const [rawText, setRawText] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Loading states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Sample text for demo
  const sampleText = `Patient John Smith (MRN: 12345678) is a 67-year-old male who presented for bronchoscopy on 03/15/2024.

PROCEDURE: Flexible bronchoscopy with EBUS-TBNA

INDICATION: Mediastinal lymphadenopathy noted on CT chest. R/O malignancy.

FINDINGS:
The patient was brought to the bronchoscopy suite and placed in the supine position. Dr. Jane Doe performed the procedure. Moderate sedation was achieved with Versed and Fentanyl.

Airways: Normal tracheobronchial anatomy. No endobronchial lesions identified. The carina was sharp.

EBUS Examination:
- Station 7 (subcarinal): 2.1 cm lymph node identified. TBNA performed x3.
- Station 4R (right paratracheal): 1.5 cm lymph node identified. TBNA performed x2.
- Station 11R (right interlobar): 0.8 cm lymph node, not sampled.

LEFT UPPER LOBE: Normal airways to subsegmental level.
RIGHT UPPER LOBE: Normal airways to subsegmental level.

Procedure duration: 45 minutes of critical care time.

IMPRESSION: Successful EBUS-TBNA of stations 7 and 4R. Specimens sent for cytology and flow cytometry.

PLAN: Follow up in clinic in 1 week for results. Contact: 619-555-1234.

Attending: Dr. Jane Doe, MD
Fellow: Dr. Bob Johnson, MD`;

  /**
   * Step 1: Analyze text for PHI
   */
  const handleAnalyze = useCallback(async () => {
    if (!rawText.trim()) {
      setError('Please enter clinical text to analyze');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/scrub/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: rawText,
          document_type: 'procedure_note',
          specialty: 'interventional_pulmonology',
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform entities to include IDs for the editor
      const entitiesWithIds = data.entities.map((entity, idx) => ({
        ...entity,
        id: `auto-${idx}`,
      }));

      setPreviewData({
        ...data,
        entities: entitiesWithIds,
      });
      setStep('review');

    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  }, [rawText]);

  /**
   * Step 2: Submit confirmed PHI
   */
  const handleSubmit = useCallback(async (submitData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: submitData.raw_text,
          confirmed_phi: submitData.confirmed_phi,
          preview_id: previewData?.preview_id,
          document_type: 'procedure_note',
          specialty: 'interventional_pulmonology',
        }),
      });

      if (!response.ok) {
        throw new Error(`Submission failed: ${response.statusText}`);
      }

      const data = await response.json();
      setJobId(data.job_id);
      setStep('processing');

      // Start polling for results
      pollForResults(data.job_id);

    } catch (err) {
      setError(err.message);
      setIsSubmitting(false);
    }
  }, [previewData]);

  /**
   * Poll for job completion
   */
  const pollForResults = useCallback(async (id) => {
    const maxAttempts = 30;
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE}/status/${id}`);
        const data = await response.json();

        if (data.status === 'completed') {
          setResults(data.coding_results);
          setStep('complete');
          setIsSubmitting(false);
        } else if (data.status === 'failed') {
          setError('Processing failed. Please try again.');
          setStep('review');
          setIsSubmitting(false);
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 2000);
        } else {
          setError('Processing timeout. Please check status manually.');
          setIsSubmitting(false);
        }
      } catch (err) {
        setError(err.message);
        setIsSubmitting(false);
      }
    };

    poll();
  }, []);

  /**
   * Reset workflow
   */
  const handleReset = useCallback(() => {
    setStep('input');
    setRawText('');
    setPreviewData(null);
    setJobId(null);
    setResults(null);
    setError(null);
  }, []);

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif",
      minHeight: '100vh',
      backgroundColor: '#F9FAFB',
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#1E40AF',
        color: '#FFFFFF',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
            IP Coding Assistant
          </h1>
          <p style={{ margin: '4px 0 0', fontSize: '13px', opacity: 0.8 }}>
            HIPAA-Compliant Medical Coding with AI
          </p>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '13px',
        }}>
          <span style={{
            width: '8px',
            height: '8px',
            backgroundColor: '#34D399',
            borderRadius: '50%',
          }} />
          PHI Protection Active
        </div>
      </header>

      {/* Progress indicator */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E5E7EB',
        padding: '16px 24px',
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '48px',
        }}>
          {['Input', 'Review PHI', 'Processing', 'Complete'].map((label, idx) => {
            const stepNames = ['input', 'review', 'processing', 'complete'];
            const currentIdx = stepNames.indexOf(step);
            const isActive = idx === currentIdx;
            const isComplete = idx < currentIdx;

            return (
              <div key={label} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  backgroundColor: isComplete ? '#10B981' : isActive ? '#2563EB' : '#E5E7EB',
                  color: isComplete || isActive ? '#FFFFFF' : '#6B7280',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: '600',
                }}>
                  {isComplete ? '✓' : idx + 1}
                </div>
                <span style={{
                  fontSize: '13px',
                  fontWeight: isActive ? '600' : '400',
                  color: isActive ? '#1F2937' : '#6B7280',
                }}>
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main content */}
      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Error display */}
        {error && (
          <div style={{
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '24px',
            color: '#DC2626',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              style={{
                background: 'none',
                border: 'none',
                color: '#DC2626',
                cursor: 'pointer',
                fontSize: '18px',
              }}
            >
              ×
            </button>
          </div>
        )}

        {/* Step 1: Input */}
        {step === 'input' && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px',
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 8px 0',
            }}>
              Enter Clinical Note
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6B7280',
              margin: '0 0 16px 0',
            }}>
              Paste or type your procedure note below. The system will automatically
              detect Protected Health Information for your review.
            </p>

            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste clinical note here..."
              style={{
                width: '100%',
                minHeight: '400px',
                padding: '16px',
                fontSize: '14px',
                lineHeight: '1.6',
                border: '1px solid #D1D5DB',
                borderRadius: '8px',
                resize: 'vertical',
                fontFamily: "'IBM Plex Mono', monospace",
              }}
            />

            <div style={{
              marginTop: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <button
                onClick={() => setRawText(sampleText)}
                style={{
                  padding: '8px 16px',
                  fontSize: '13px',
                  backgroundColor: '#F3F4F6',
                  color: '#374151',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                Load Sample Note
              </button>

              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !rawText.trim()}
                style={{
                  padding: '12px 24px',
                  fontSize: '14px',
                  fontWeight: '600',
                  backgroundColor: isAnalyzing || !rawText.trim() ? '#9CA3AF' : '#2563EB',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isAnalyzing || !rawText.trim() ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                {isAnalyzing ? (
                  <>
                    <span style={{
                      width: '16px',
                      height: '16px',
                      border: '2px solid #FFFFFF',
                      borderTopColor: 'transparent',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite',
                    }} />
                    Analyzing...
                  </>
                ) : (
                  'Analyze for PHI →'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Review */}
        {step === 'review' && previewData && (
          <PHIReviewEditor
            initialText={previewData.raw_text}
            initialEntities={previewData.entities}
            onSubmit={handleSubmit}
            onCancel={() => setStep('input')}
            isLoading={isSubmitting}
          />
        )}

        {/* Step 3: Processing */}
        {step === 'processing' && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '48px',
            textAlign: 'center',
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              border: '4px solid #E5E7EB',
              borderTopColor: '#2563EB',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 24px',
            }} />
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 8px 0',
            }}>
              Processing Your Request
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6B7280',
              margin: '0 0 16px 0',
            }}>
              PHI has been secured. AI is analyzing the de-identified text...
            </p>
            <p style={{
              fontSize: '12px',
              color: '#9CA3AF',
            }}>
              Job ID: {jobId}
            </p>
          </div>
        )}

        {/* Step 4: Complete */}
        {step === 'complete' && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            padding: '24px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '24px',
            }}>
              <div style={{
                width: '48px',
                height: '48px',
                backgroundColor: '#D1FAE5',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '24px',
              }}>
                ✓
              </div>
              <div>
                <h2 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: 0,
                }}>
                  Coding Complete
                </h2>
                <p style={{
                  fontSize: '14px',
                  color: '#6B7280',
                  margin: '4px 0 0',
                }}>
                  Results are ready for review
                </p>
              </div>
            </div>

            <div style={{
              backgroundColor: '#F9FAFB',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '24px',
            }}>
              <h3 style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#374151',
                margin: '0 0 12px 0',
              }}>
                Suggested Codes
              </h3>
              <pre style={{
                margin: 0,
                fontSize: '13px',
                fontFamily: "'IBM Plex Mono', monospace",
                whiteSpace: 'pre-wrap',
              }}>
                {JSON.stringify(results || { note: "Demo mode - no actual LLM processing" }, null, 2)}
              </pre>
            </div>

            <button
              onClick={handleReset}
              style={{
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: '500',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              Start New Coding Request
            </button>
          </div>
        )}
      </main>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default PHIReviewDemo;
