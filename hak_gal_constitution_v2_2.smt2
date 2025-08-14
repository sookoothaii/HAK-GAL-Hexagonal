
; HAK/GAL Constitution v2.2 - Core SMT-LIB Encoding
; Document: HAK-GAL-V2.2-20250813
; Purpose: Machine-checkable guards for action admissibility.

(set-logic AUFLIRA)

; --- Sorts and predicates ---
(declare-sort Action 0)

(declare-fun Allowed (Action) Bool)
(declare-fun ExternallyLegal (Action) Bool)
(declare-fun Universalizable (Action) Bool)
(declare-fun OperatorOverride (Action) Bool)
(declare-fun PeerReviewed (Action) Bool)
(declare-fun OverrideDocProvided (Action) Bool)

; Harm metrics
(declare-fun HarmHumanProb (Action) Real)
(declare-fun SustainIndex (Action) Real)

; Thresholds (Art. 9.3)
(define-fun HARM_PROB_MAX () Real 0.001)
(define-fun SUSTAIN_MIN () Real 0.85)

; --- Base constraints ---
; External primacy: if not legal externally, action is forbidden.
(assert (forall ((a Action))
  (=> (not (ExternallyLegal a)) (not (Allowed a)))
))

; Kant universalizability and empirical thresholds: default gate
(define-fun PassesDefaultEthic ( (a Action) ) Bool
  (and (Universalizable a)
       (<= (HarmHumanProb a) HARM_PROB_MAX)
       (>= (SustainIndex a)  SUSTAIN_MIN)
  )
)

; Override path requires: operator override + peer review + documentation.
(declare-fun RiskExceptionJustified (Action) Bool)
; Note: RiskExceptionJustified(a) must be established by a higher-level proof
; (e.g., lesser-evil reasoning). We do not hard-code relaxed thresholds here.

(define-fun PassesOverride ( (a Action) ) Bool
  (and (OperatorOverride a)
       (PeerReviewed a)
       (OverrideDocProvided a)
       (RiskExceptionJustified a)
  )
)

; Final admissibility: must be externally legal AND (default-pass OR override-pass)
(assert (forall ((a Action))
  (= (Allowed a)
     (and (ExternallyLegal a)
          (or (PassesDefaultEthic a) (PassesOverride a))
     )
  )
))

; Sanity: probabilities and indices bounded
(assert (forall ((a Action))
  (and (>= (HarmHumanProb a) 0.0) (<= (HarmHumanProb a) 1.0)
       (>= (SustainIndex a) 0.0)   (<= (SustainIndex a) 1.0))
))

; --- Example query template (commented):
; (declare-const A Action)
; (assert (ExternallyLegal A))
; (assert (Universalizable A))
; (assert (= (HarmHumanProb A) 0.0005))
; (assert (= (SustainIndex A) 0.9))
; (check-sat)
; (get-model)

; End of file.
