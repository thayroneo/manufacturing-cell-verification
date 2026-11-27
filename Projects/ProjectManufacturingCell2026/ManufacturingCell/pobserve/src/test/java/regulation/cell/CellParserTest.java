package regulation.cell;

import org.junit.jupiter.api.Test;
import regulation.cell.parser.CellRegulationParser;
import static org.junit.jupiter.api.Assertions.*;

/** Parser boundary checks: irrelevant records may be skipped; missing payloads fail. */
public class CellParserTest {
    private final CellRegulationParser parser = new CellRegulationParser();
    private final String prefix = "2026-10-19 08:00:00.001000 [cell-A] INFO Regulation - : Site=cell-A, ";

    @Test public void irrelevantLineProducesNoEvents() { assertEquals(0, parser.apply("unrelated log").count()); }
    @Test public void runtimeBoundIsRecognized() { assertEquals(1, parser.apply(prefix + "Event=RUNTIME_CONFIG, MaxAdaptTicks=8").count()); }
    @Test public void missingRequiredFieldIsNotSilentlySkipped() {
        assertThrows(IllegalArgumentException.class, () -> parser.apply(prefix + "Event=ENTER, Agent=1, Res=0").count());
    }
}
