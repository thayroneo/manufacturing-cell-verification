test tcCellTwoTechniciansPreFix [main=TestCellTwoTechniciansPreFix]:
  assert RegimentationSafety, NoStaleAdmission, NoDoubleOutcome,
         EveryObligationResolved, AdaptationCompletes, AdaptationTerminates,
         LockoutBeforeEntry, NoOpeningWhileHumanInside in
  { TestCellTwoTechniciansPreFix, ManufacturingSystem, CellAgent, ResourceGuard,
    AdaptationCoordinator, AdaptationCoordinatorFixed, ObligationManager, Clock, HumanRequester, HumanRequesterFixed };

test tcCellTwoTechniciansFixed [main=TestCellTwoTechniciansFixed]:
  assert RegimentationSafety, NoStaleAdmission, NoDoubleOutcome,
         EveryObligationResolved, AdaptationCompletes, AdaptationTerminates,
         LockoutBeforeEntry, NoOpeningWhileHumanInside in
  { TestCellTwoTechniciansFixed, ManufacturingSystem, CellAgent, ResourceGuard,
    AdaptationCoordinator, AdaptationCoordinatorFixed, ObligationManager, Clock, HumanRequester, HumanRequesterFixed };
