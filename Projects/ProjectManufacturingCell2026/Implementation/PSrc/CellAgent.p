// Team copy for ET2. The baseline machine is preserved; ET2 changes the
// ManufacturingSystem wiring to instantiate two human requesters.
fun CELL(): int { return 0; }
type tHumanSync = (resource: int, requester: machine);
event eHumanEnteredSync: tHumanSync;
event eHumanLeftSync: tHumanSync;
event eHumanSyncAck;

machine CellAgent {
  var id: int; var guard: machine; var om: machine; var resource: int; var job: tObligation; var attempts: int;
  start state Init { entry (cfg: (id: int, guard: machine, om: machine, resource: int)) { id = cfg.id; guard = cfg.guard; om = cfg.om; resource = cfg.resource; goto Idle; } }
  state Idle { on eObligationNotice do (o: tObligation) { job = o; attempts = 0; goto Requesting; } ignore eSanction; }
  state Requesting { entry { attempts = attempts + 1; send guard, eAccessRequest, (agent = id, agentRef = this, resource = resource); } on eAccessGranted do (g: tGrant) { goto Working; } on eAccessDenied do (r: int) { if (attempts < 3) { goto Requesting; } else { goto Idle; } } defer eObligationNotice; ignore eSanction; }
  state Working { entry { send this, eContinue; } on eContinue do { send guard, eRelease, (agent = id, agentRef = this, resource = resource); if ($) { send om, eReportFulfilled, (id = job.id, agent = id); } goto Idle; } defer eObligationNotice; ignore eSanction; }
}

machine ManufacturingSystem {
  start state Init {
    entry (cfg: (twoPhase: bool, fixed: bool)) {
      var twoPhase: bool; var fixed: bool; var capacity: map[int, int]; var cell: machine; var guards: seq[machine]; var coord: machine; var om: machine; var arm: machine; var agv: machine; var subscribers: seq[machine];
      twoPhase = cfg.twoPhase; fixed = cfg.fixed;
      capacity[CELL()] = 1; announce eMonitorConfig, capacity;
      cell = new ResourceGuard((resource = CELL(), capacity = 1)); guards += (0, cell);
      if (fixed) { coord = new AdaptationCoordinatorFixed((guards = guards, twoPhase = twoPhase)); }
      else { coord = new AdaptationCoordinator((guards = guards, twoPhase = twoPhase)); }
      om = new ObligationManager();
      arm = new CellAgent((id = 1, guard = cell, om = om, resource = CELL())); agv = new CellAgent((id = 2, guard = cell, om = om, resource = CELL()));
      send om, eAssignTask, (agent = 1, agentRef = arm, task = 100, due = 4); send om, eAssignTask, (agent = 2, agentRef = agv, task = 200, due = 6);
      subscribers += (0, om); new Clock((subscribers = subscribers, maxTicks = 10));
      // ET2: two independent technicians request the same resource.
      if (fixed) {
        new HumanRequesterFixed((coord = coord, resource = CELL()));
        new HumanRequesterFixed((coord = coord, resource = CELL()));
      } else {
        new HumanRequester((coord = coord, resource = CELL()));
        new HumanRequester((coord = coord, resource = CELL()));
      }
    }
  }
}

machine TestCellTwoTechniciansPreFix { start state Init { entry { new ManufacturingSystem((twoPhase = true, fixed = false)); } } }
machine TestCellTwoTechniciansFixed { start state Init { entry { new ManufacturingSystem((twoPhase = true, fixed = true)); } } }
machine TestCellTwoPhase { start state Init { entry { new ManufacturingSystem((twoPhase = true, fixed = false)); } } }
machine TestCellNaive { start state Init { entry { new ManufacturingSystem((twoPhase = false, fixed = false)); } } }

// Fixed variant explicitly forwards occupancy facts to the coordinator while
// retaining the announcements consumed by the monitors.
machine HumanRequesterFixed {
  var coord: machine; var resource: int;
  start state Init {
    entry (cfg: (coord: machine, resource: int)) { coord = cfg.coord; resource = cfg.resource; send this, eContinue; goto Outside; }
  }
  state Outside {
    on eContinue do { send coord, eAdaptationTriggered, (resource = resource, close = true, requester = this); goto WaitingForLock; }
  }
  state WaitingForLock {
    on eAdaptationDone do (n: tNormSet) { announce eHumanEntered, resource; send coord, eHumanEnteredSync, (resource = resource, requester = this); goto WaitingEnteredAck; }
  }
  state WaitingEnteredAck { on eHumanSyncAck do { send this, eContinue; goto Inside; } }
  state Inside {
    on eContinue do { announce eHumanLeft, resource; send coord, eHumanLeftSync, (resource = resource, requester = this); goto WaitingLeaveAck; }
  }
  state WaitingLeaveAck { on eHumanSyncAck do { send coord, eAdaptationTriggered, (resource = resource, close = false, requester = this); goto WaitingForUnlock; } }
  state WaitingForUnlock { on eAdaptationDone do (n: tNormSet) { goto Done; } }
  state Done { }
}

// ET2 corrected coordinator: an opening request is ignored while another
// technician remains inside the resource.
machine AdaptationCoordinatorFixed {
  var guards: seq[machine]; var current: tNormSet; var pending: tNormSet;
  var requester: machine; var acks: set[machine]; var twoPhase: bool;
  var humans: map[int, int]; var awaiting: map[int, int];
  var pendingClose: bool; var pendingResource: int;
  start state Init {
    entry (cfg: (guards: seq[machine], twoPhase: bool)) {
      guards = cfg.guards; twoPhase = cfg.twoPhase;
      current = (ver = 0, closed = default(set[int])); goto Stable;
    }
  }
  state Stable {
    on eHumanEnteredSync do (s: tHumanSync) { Inc(s.resource); DecAwaiting(s.resource); send s.requester, eHumanSyncAck; }
    on eHumanLeftSync do (s: tHumanSync) { Dec(s.resource); send s.requester, eHumanSyncAck; }
    on eHumanEntered do (r: int) { Inc(r); }
    on eHumanLeft do (r: int) { Dec(r); }
    on eAdaptationTriggered do (t: tTrigger) {
      var closed: set[int];
      if (!t.close && (Count(t.resource) > 0 || Awaiting(t.resource) > 0)) {
        // Keep the resource closed. The last technician's leave generates
        // another opening trigger, which is processed after the count reaches 0.
        closed = current.closed;
      } else {
        closed = current.closed;
        if (t.close) { closed += (t.resource); }
        else if (t.resource in closed) { closed -= (t.resource); }
        pending = (ver = current.ver + 1, closed = closed);
        pendingClose = t.close; pendingResource = t.resource;
        requester = t.requester; announce eAdaptationStarted, pending.ver;
        if (twoPhase) { goto Preparing; } else { goto Committing; }
      }
    }
    ignore eNormPrepareAck;
  }
  state Preparing {
    entry { var i: int; acks = default(set[machine]); i = 0; while (i < sizeof(guards)) { send guards[i], eNormPrepare, (normSet = pending, coord = this); i = i + 1; } }
    on eHumanEnteredSync do (s: tHumanSync) { Inc(s.resource); DecAwaiting(s.resource); send s.requester, eHumanSyncAck; }
    on eHumanLeftSync do (s: tHumanSync) { Dec(s.resource); send s.requester, eHumanSyncAck; }
    on eNormPrepareAck do (a: tAck) { if (a.version == pending.ver) { acks += (a.guard); } if (sizeof(acks) == sizeof(guards)) { goto Committing; } }
    defer eAdaptationTriggered;
  }
  state Committing {
    entry { var i: int; current = pending; if (pendingClose) { IncAwaiting(pendingResource); } announce eNormCommitted, current; i = 0; while (i < sizeof(guards)) { send guards[i], eNormCommit, current; i = i + 1; } send requester, eAdaptationDone, current; goto Stable; }
    on eHumanEnteredSync do (s: tHumanSync) { Inc(s.resource); DecAwaiting(s.resource); send s.requester, eHumanSyncAck; }
    on eHumanLeftSync do (s: tHumanSync) { Dec(s.resource); send s.requester, eHumanSyncAck; }
    defer eAdaptationTriggered;
  }
  fun Inc(r: int) { if (!(r in humans)) { humans[r] = 0; } humans[r] = humans[r] + 1; }
  fun Dec(r: int) { if (r in humans && humans[r] > 0) { humans[r] = humans[r] - 1; } }
  fun Count(r: int): int { if (r in humans) { return humans[r]; } return 0; }
  fun Awaiting(r: int): int { if (r in awaiting) { return awaiting[r]; } return 0; }
  fun IncAwaiting(r: int) { if (!(r in awaiting)) { awaiting[r] = 0; } awaiting[r] = awaiting[r] + 1; }
  fun DecAwaiting(r: int) { if (r in awaiting && awaiting[r] > 0) { awaiting[r] = awaiting[r] - 1; } }
}
