"""Synthetic two-technician extension of the original simulator.

Messages are serialized by a request queue. A holder is reserved from the
request through HUMAN_LEAVE, covering authorized entries not yet recorded.
Unlike the P model, guard installation here is synchronous: this is a
log-producing simulation, not a replay or refinement proof of the P model.
"""
import random

from simulate_logs import CellAgent, Guard, Log, Organization


class Technician:
    def __init__(self, identity, rng):
        self.identity = identity
        self.rng = rng
        self.state = "outside"
        self.timer = rng.randint(1, 3)
        self.authorized = False

    def step(self, log, org):
        if self.state == "outside":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "waiting"
                org.request(self, True)
        if self.state == "waiting" and self.authorized:
            log.emit("HUMAN_ENTER", Res=0)
            self.state = "inside"
            self.timer = self.rng.randint(4, 7)
        elif self.state == "inside":
            self.timer -= 1
            if self.timer <= 0:
                log.emit("HUMAN_LEAVE", Res=0)
                self.state = "done"
                org.request(self, False)


class TwoTechnicianOrganization(Organization):
    def __init__(self, log, guards, rng, fixed):
        super().__init__(log, guards, "twophase", rng)
        self.fixed = fixed
        self.holders = set()
        self.queue = []
        self.active = None

    def request(self, technician, close):
        if close:
            self.holders.add(technician.identity)
        else:
            self.holders.discard(technician.identity)
        self.queue.append((technician, close))
        self.pump()

    def pump(self):
        while True:
            if self.active is not None:
                if not self.try_finish():
                    return
                technician, close = self.active
                if close:
                    technician.authorized = True
                self.active = None
            if not self.queue:
                return
            technician, close = self.queue.pop(0)
            if not close and self.fixed and self.holders:
                continue
            self.active = (technician, close)
            self.start_adaptation(0, close)


def simulate_two(seed, ticks=60, fixed=True):
    rng = random.Random(seed)
    log = Log("cell-A")
    guards = {0: Guard(0, 1)}
    agents = [CellAgent(1, rng, .9), CellAgent(2, rng, .9)]
    technicians = [Technician(1, rng), Technician(2, rng)]
    org = TwoTechnicianOrganization(log, guards, rng, fixed)
    log.emit("CONFIG", Capacity="0:1")
    for now in range(1, ticks + 1):
        log.now = now
        log.micro = 0
        log.emit("TICK", Now=now)
        org.on_tick(now)
        actors = agents + technicians
        rng.shuffle(actors)
        for actor in actors:
            if isinstance(actor, Technician):
                actor.step(log, org)
            else:
                actor.step(log, org, guards[0], now)
            org.pump()
            for guard in guards.values():
                guard.step_install()
    return log


def inspect_adaptations(log):
    """Measure logged START -> COMMIT/ABORT durations, including protocol delay."""
    now = 0
    pending = {}
    completed = []
    people = 0
    maximum_people = 0
    unsafe_reopenings = []
    for event, fields in log.events:
        if event == "TICK":
            now = fields["Now"]
        elif event == "ADAPT_START":
            version = fields["Ver"]
            if version in pending:
                raise ValueError("duplicate adaptation start")
            pending[version] = now
        elif event in ("COMMIT", "ADAPT_ABORT"):
            version = fields["Ver"]
            if version in pending:
                start = pending.pop(version)
                completed.append({"version": version, "start": start,
                                  "end": now, "duration": now - start,
                                  "outcome": event})
            if event == "COMMIT" and str(fields["Closed"]) == "-" and people:
                unsafe_reopenings.append({"version": version, "tick": now, "people": people})
        elif event == "HUMAN_ENTER":
            people += 1
            maximum_people = max(maximum_people, people)
        elif event == "HUMAN_LEAVE":
            people -= 1
    return {"completed": completed, "pending_at_eof": pending,
            "max_people": maximum_people, "unsafe_reopenings": unsafe_reopenings}
