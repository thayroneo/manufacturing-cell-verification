// S4 — a committed opening must not occur while any technician remains inside.
spec NoOpeningWhileHumanInside observes eNormCommitted, eHumanEntered, eHumanLeft {
  var humanIn: map[int, int];

  start state Watching {
    on eHumanEntered do (r: int) {
      if (!(r in humanIn)) { humanIn[r] = 0; }
      humanIn[r] = humanIn[r] + 1;
    }
    on eHumanLeft do (r: int) {
      if (r in humanIn && humanIn[r] > 0) { humanIn[r] = humanIn[r] - 1; }
    }
    on eNormCommitted do (n: tNormSet) {
      var rs: seq[int];
      var i: int;
      rs = keys(humanIn);
      i = 0;
      while (i < sizeof(rs)) {
        assert rs[i] in n.closed || humanIn[rs[i]] == 0,
          format("resource {0} reopened while {1} human(s) remain inside", rs[i], humanIn[rs[i]]);
        i = i + 1;
      }
    }
  }
}
