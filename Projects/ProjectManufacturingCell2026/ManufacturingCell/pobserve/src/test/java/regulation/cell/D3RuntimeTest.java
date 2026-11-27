package regulation.cell;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import pobserve.junit.PObserveJUnitSpecConfig;
import pobserve.junit.PObserveLogFileBaseTest;
import pobserve.runtime.exceptions.PAssertionFailureException;
import regulation.cell.parser.CellRegulationParser;
import regulation.cell.spec.PMachines;
import static org.junit.jupiter.api.Assertions.*;

/** Real Java monitors over the generated D3 corpus, including S4. */
@PObserveJUnitSpecConfig(parser = CellRegulationParser.class, monitors = {
    PMachines.RegimentationSafety.Supplier.class,
    PMachines.NoStaleAdmission.Supplier.class,
    PMachines.NoDoubleOutcome.Supplier.class,
    PMachines.ObligationDeadlineRespected.Supplier.class,
    PMachines.AdaptationBoundedTime.Supplier.class,
    PMachines.LockoutBeforeEntry.Supplier.class,
    PMachines.NoOpeningWhileHumanInside.Supplier.class
})
public class D3RuntimeTest extends PObserveLogFileBaseTest {
    private void check(String name) throws Exception {
        Path directory = Path.of(System.getProperty("d3.evidence.dir", "../../Implementation/evidence/D3"));
        try (InputStream input = Files.newInputStream(directory.resolve("logs/" + name + ".log"))) {
            runPObserveOnLogFile(input);
        }
    }

    private void violation(String name, String message) {
        Exception failure = assertThrows(PAssertionFailureException.class, () -> check(name));
        assertTrue(failure.getMessage().contains(message), failure.getMessage());
    }

    @Test public void twoOverlappingTechniciansStaySafe() { assertDoesNotThrow(() -> check("two_technicians_fixed")); }
    @Test public void reopeningWithSecondTechnicianFailsS4() { violation("two_technicians_prefix", "reopened"); }
    @Test public void calibratedBoundAcceptsSameExecution() { assertDoesNotThrow(() -> check("seed64_calibrated")); }
    @Test public void originalBoundRejectsOverFiveTickExecution() { violation("seed64_default_bound", "not committed"); }
    @Test public void measuredMaximumIsAcceptedAtEightTicks() { assertDoesNotThrow(() -> check("seed299_calibrated")); }
    @Test public void actualSuppressedSanctionFailsR1() { violation("system_sanction_suppressed", "overdue"); }
    @Test public void actualDelayedCommitFailsR2() { violation("system_commit_delayed", "not committed"); }
    @Test public void deletedSanctionAlsoFailsR1() { violation("log_deleted_sanction", "overdue"); }
    @Test public void missingLeaveProducesFalseSafetyAlarm() { violation("log_missing_leave", "resource 0"); }
    @Test public void duplicateCommitProducesFalseVersionAlarm() { violation("log_duplicate_commit", "version order"); }
    @Test public void duplicateOutcomeFailsS3() { violation("log_duplicate_outcome", "resolved twice"); }
    @Test public void entryWithoutLockoutFailsR3() { violation("human_bypasses_lockout", "without a committed lock-out"); }
    @Test public void matchingAbortTerminatesBoundedResponse() { assertDoesNotThrow(() -> check("abort_valid")); }
    @Test public void unrelatedAbortDoesNotHidePendingAdaptation() { violation("abort_wrong_version", "abort does not match"); }
}
