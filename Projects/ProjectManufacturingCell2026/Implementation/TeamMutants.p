// Mutation suite for ET2-T06. Each mutant intentionally rejects a reachable
// antecedent event, so a passing checker result cannot be explained by an
// unreachable monitor state.
spec MutantS1 observes eResourceEntered {
  start state Watching { on eResourceEntered do { assert false, "mutant S1 detected"; } }
}
spec MutantS2 observes eResourceEntered {
  start state Watching { on eResourceEntered do { assert false, "mutant S2 detected"; } }
}
spec MutantS3 observes eObligationFulfilled {
  start state Watching { on eObligationFulfilled do { assert false, "mutant S3 detected"; } }
}
spec MutantL1 observes eObligationCreated {
  start state Watching { on eObligationCreated do { assert false, "mutant L1 detected"; } }
}
spec MutantL2 observes eAdaptationStarted {
  start state Watching { on eAdaptationStarted do { assert false, "mutant L2 detected"; } }
}
spec MutantL3 observes eAdaptationStarted {
  start state Watching { on eAdaptationStarted do { assert false, "mutant L3 detected"; } }
}
spec MutantR3 observes eNormCommitted {
  start state Watching { on eNormCommitted do { assert false, "mutant R3 detected"; } }
}
