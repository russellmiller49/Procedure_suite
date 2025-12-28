import React, { useState, useCallback, useMemo } from 'react';

/**
 * PHI Review Editor Component
 * 
 * Allows physicians to review auto-detected PHI entities,
 * confirm/unflag items, and add missed PHI before submission.
 */

const ENTITY_COLORS = {
  PERSON: { bg: '#FEE2E2', border: '#EF4444', text: '#991B1B' },
  DATE: { bg: '#FEF3C7', border: '#F59E0B', text: '#92400E' },
  MRN: { bg: '#DBEAFE', border: '#3B82F6', text: '#1E40AF' },
  LOCATION: { bg: '#D1FAE5', border: '#10B981', text: '#065F46' },
  PHONE: { bg: '#E0E7FF', border: '#6366F1', text: '#3730A3' },
  EMAIL: { bg: '#FCE7F3', border: '#EC4899', text: '#9D174D' },
  SSN: { bg: '#FEE2E2', border: '#DC2626', text: '#991B1B' },
  PROVIDER: { bg: '#F3E8FF', border: '#9333EA', text: '#581C87' },
  DEFAULT: { bg: '#F3F4F6', border: '#6B7280', text: '#374151' },
};

const ENTITY_TYPES = [
  { value: 'PERSON', label: 'Patient Name' },
  { value: 'PROVIDER', label: 'Provider Name' },
  { value: 'DATE', label: 'Date' },
  { value: 'MRN', label: 'MRN' },
  { value: 'LOCATION', label: 'Location (Address)' },
  { value: 'PHONE', label: 'Phone Number' },
  { value: 'EMAIL', label: 'Email' },
  { value: 'SSN', label: 'SSN' },
];

function PHIReviewEditor({ 
  initialText = '', 
  initialEntities = [], 
  onSubmit,
  onCancel,
  isLoading = false 
}) {
  const [entities, setEntities] = useState(initialEntities);
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [newEntityType, setNewEntityType] = useState('PERSON');
  const [selectionRange, setSelectionRange] = useState(null);

  // Sort entities by start position for rendering
  const sortedEntities = useMemo(() => 
    [...entities].sort((a, b) => a.start - b.start),
    [entities]
  );

  // Build the highlighted text with PHI markers
  const renderHighlightedText = useCallback(() => {
    if (!initialText) return null;
    
    const segments = [];
    let lastEnd = 0;

    sortedEntities.forEach((entity, idx) => {
      // Add plain text before this entity
      if (entity.start > lastEnd) {
        segments.push(
          <span key={`text-${idx}`}>
            {initialText.slice(lastEnd, entity.start)}
          </span>
        );
      }

      const colors = ENTITY_COLORS[entity.entity_type] || ENTITY_COLORS.DEFAULT;
      const isSelected = selectedEntityId === entity.id;

      segments.push(
        <span
          key={`entity-${entity.id}`}
          onClick={() => setSelectedEntityId(entity.id)}
          style={{
            backgroundColor: colors.bg,
            border: `2px solid ${isSelected ? colors.text : colors.border}`,
            color: colors.text,
            padding: '2px 6px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: isSelected ? '600' : '500',
            boxShadow: isSelected ? `0 0 0 2px ${colors.border}` : 'none',
            transition: 'all 0.15s ease',
          }}
          title={`${entity.entity_type} (${Math.round(entity.confidence * 100)}% confidence)`}
        >
          {entity.text}
        </span>
      );

      lastEnd = entity.end;
    });

    // Add remaining text
    if (lastEnd < initialText.length) {
      segments.push(
        <span key="text-final">
          {initialText.slice(lastEnd)}
        </span>
      );
    }

    return segments;
  }, [initialText, sortedEntities, selectedEntityId]);

  // Handle text selection for adding new PHI
  const handleTextSelection = useCallback(() => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      const range = selection.getRangeAt(0);
      const textContent = selection.toString();
      
      // Find the actual position in the original text
      const fullText = initialText;
      const selectedText = textContent.trim();
      const startIndex = fullText.indexOf(selectedText);
      
      if (startIndex !== -1) {
        setSelectionRange({
          text: selectedText,
          start: startIndex,
          end: startIndex + selectedText.length,
        });
        setIsAddingNew(true);
      }
    }
  }, [initialText]);

  // Add a new PHI entity from selection
  const handleAddEntity = useCallback(() => {
    if (!selectionRange) return;

    const newEntity = {
      id: `manual-${Date.now()}`,
      text: selectionRange.text,
      start: selectionRange.start,
      end: selectionRange.end,
      entity_type: newEntityType,
      confidence: 1.0, // Human-added = 100% confidence
      source: 'manual',
    };

    setEntities(prev => [...prev, newEntity]);
    setIsAddingNew(false);
    setSelectionRange(null);
    window.getSelection()?.removeAllRanges();
  }, [selectionRange, newEntityType]);

  // Remove/unflag an entity
  const handleRemoveEntity = useCallback((entityId) => {
    setEntities(prev => prev.filter(e => e.id !== entityId));
    setSelectedEntityId(null);
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(() => {
    if (onSubmit) {
      onSubmit({
        raw_text: initialText,
        confirmed_phi: entities.map(e => ({
          text: e.text,
          start: e.start,
          end: e.end,
          entity_type: e.entity_type,
          confidence: e.confidence,
          source: e.source || 'auto',
        })),
      });
    }
  }, [initialText, entities, onSubmit]);

  const selectedEntity = entities.find(e => e.id === selectedEntityId);

  return (
    <div style={{
      fontFamily: "'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif",
      maxWidth: '900px',
      margin: '0 auto',
      padding: '24px',
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '24px',
        paddingBottom: '16px',
        borderBottom: '1px solid #E5E7EB',
      }}>
        <h2 style={{
          fontSize: '20px',
          fontWeight: '600',
          color: '#111827',
          margin: '0 0 8px 0',
        }}>
          Review Protected Health Information
        </h2>
        <p style={{
          fontSize: '14px',
          color: '#6B7280',
          margin: 0,
        }}>
          Highlighted items will be secured before processing. Click to select, 
          or highlight text to flag additional PHI.
        </p>
      </div>

      {/* Main content area */}
      <div style={{ display: 'flex', gap: '24px' }}>
        {/* Text editor panel */}
        <div style={{ flex: 1 }}>
          <div
            onMouseUp={handleTextSelection}
            style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #D1D5DB',
              borderRadius: '8px',
              padding: '20px',
              fontSize: '15px',
              lineHeight: '1.8',
              color: '#1F2937',
              minHeight: '300px',
              cursor: 'text',
              whiteSpace: 'pre-wrap',
            }}
          >
            {renderHighlightedText()}
          </div>

          {/* Legend */}
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            backgroundColor: '#F9FAFB',
            borderRadius: '6px',
            display: 'flex',
            flexWrap: 'wrap',
            gap: '12px',
          }}>
            {Object.entries(ENTITY_COLORS).filter(([key]) => key !== 'DEFAULT').map(([type, colors]) => (
              <div key={type} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '12px',
              }}>
                <span style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: colors.bg,
                  border: `1px solid ${colors.border}`,
                  borderRadius: '2px',
                }} />
                <span style={{ color: '#6B7280' }}>{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar panel */}
        <div style={{ width: '280px', flexShrink: 0 }}>
          {/* Entity details / Add new panel */}
          {isAddingNew && selectionRange ? (
            <div style={{
              backgroundColor: '#F0FDF4',
              border: '1px solid #86EFAC',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
            }}>
              <h4 style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#166534',
                margin: '0 0 12px 0',
              }}>
                Flag as PHI
              </h4>
              <p style={{
                fontSize: '13px',
                color: '#15803D',
                margin: '0 0 12px 0',
                padding: '8px',
                backgroundColor: '#DCFCE7',
                borderRadius: '4px',
                wordBreak: 'break-word',
              }}>
                "{selectionRange.text}"
              </p>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '6px',
              }}>
                PHI Type
              </label>
              <select
                value={newEntityType}
                onChange={(e) => setNewEntityType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  fontSize: '14px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '6px',
                  marginBottom: '12px',
                  backgroundColor: '#FFFFFF',
                }}
              >
                {ENTITY_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={handleAddEntity}
                  style={{
                    flex: 1,
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: '500',
                    backgroundColor: '#16A34A',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                  }}
                >
                  Add
                </button>
                <button
                  onClick={() => {
                    setIsAddingNew(false);
                    setSelectionRange(null);
                  }}
                  style={{
                    flex: 1,
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: '500',
                    backgroundColor: '#FFFFFF',
                    color: '#374151',
                    border: '1px solid #D1D5DB',
                    borderRadius: '6px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : selectedEntity ? (
            <div style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #D1D5DB',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
            }}>
              <h4 style={{
                fontSize: '14px',
                fontWeight: '600',
                color: '#111827',
                margin: '0 0 12px 0',
              }}>
                Selected Item
              </h4>
              <div style={{ marginBottom: '12px' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '4px 8px',
                  fontSize: '12px',
                  fontWeight: '500',
                  backgroundColor: ENTITY_COLORS[selectedEntity.entity_type]?.bg || '#F3F4F6',
                  color: ENTITY_COLORS[selectedEntity.entity_type]?.text || '#374151',
                  borderRadius: '4px',
                }}>
                  {selectedEntity.entity_type}
                </span>
              </div>
              <p style={{
                fontSize: '14px',
                color: '#1F2937',
                margin: '0 0 8px 0',
                fontWeight: '500',
              }}>
                "{selectedEntity.text}"
              </p>
              <p style={{
                fontSize: '12px',
                color: '#6B7280',
                margin: '0 0 16px 0',
              }}>
                Confidence: {Math.round(selectedEntity.confidence * 100)}%
                {selectedEntity.source === 'manual' && ' (manually added)'}
              </p>
              <button
                onClick={() => handleRemoveEntity(selectedEntity.id)}
                style={{
                  width: '100%',
                  padding: '8px 16px',
                  fontSize: '13px',
                  fontWeight: '500',
                  backgroundColor: '#FEF2F2',
                  color: '#DC2626',
                  border: '1px solid #FECACA',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                Unflag (Not PHI)
              </button>
            </div>
          ) : (
            <div style={{
              backgroundColor: '#F9FAFB',
              border: '1px dashed #D1D5DB',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
              textAlign: 'center',
            }}>
              <p style={{
                fontSize: '13px',
                color: '#6B7280',
                margin: 0,
              }}>
                Click a highlighted item to review, or select text to flag additional PHI.
              </p>
            </div>
          )}

          {/* Entity summary */}
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #D1D5DB',
            borderRadius: '8px',
            padding: '16px',
            marginBottom: '16px',
          }}>
            <h4 style={{
              fontSize: '14px',
              fontWeight: '600',
              color: '#111827',
              margin: '0 0 12px 0',
            }}>
              PHI Summary ({entities.length} items)
            </h4>
            {entities.length === 0 ? (
              <p style={{
                fontSize: '13px',
                color: '#6B7280',
                margin: 0,
              }}>
                No PHI flagged. The entire note will be sent for processing.
              </p>
            ) : (
              <ul style={{
                margin: 0,
                padding: 0,
                listStyle: 'none',
              }}>
                {sortedEntities.map(entity => (
                  <li
                    key={entity.id}
                    onClick={() => setSelectedEntityId(entity.id)}
                    style={{
                      padding: '8px',
                      marginBottom: '4px',
                      fontSize: '13px',
                      backgroundColor: selectedEntityId === entity.id ? '#F3F4F6' : 'transparent',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span style={{
                      color: '#374151',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      maxWidth: '150px',
                    }}>
                      {entity.text}
                    </span>
                    <span style={{
                      fontSize: '11px',
                      color: '#9CA3AF',
                      flexShrink: 0,
                    }}>
                      {entity.entity_type}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Action buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '14px',
                fontWeight: '600',
                backgroundColor: isLoading ? '#9CA3AF' : '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {isLoading ? (
                <>
                  <span style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid #FFFFFF',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                  }} />
                  Processing...
                </>
              ) : (
                <>
                  <span>✓</span>
                  Confirm &amp; Submit
                </>
              )}
            </button>
            {onCancel && (
              <button
                onClick={onCancel}
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  fontSize: '14px',
                  fontWeight: '500',
                  backgroundColor: '#FFFFFF',
                  color: '#374151',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                }}
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div style={{
        marginTop: '24px',
        padding: '12px 16px',
        backgroundColor: '#FFFBEB',
        border: '1px solid #FDE68A',
        borderRadius: '6px',
        fontSize: '12px',
        color: '#92400E',
      }}>
        <strong>HIPAA Notice:</strong> By clicking "Confirm &amp; Submit," you attest that the 
        highlighted items correctly identify all Protected Health Information in this note. 
        Only de-identified text will be sent for AI processing.
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default PHIReviewEditor;
