(declare-const ExternallyLegal Bool)
(declare-const Universalizable Bool)
(declare-const HarmHumanProb Real)
(declare-const SustainIndex Real)

(assert ExternallyLegal)
(assert Universalizable)
(assert (<= HarmHumanProb 0.001))
(assert (>= SustainIndex 0.85))

(check-sat)
