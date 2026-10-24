package com.example.concurrentrequestscope.internal;

import com.example.concurrentrequestscope.exception.ConcurrentRequestScopeBackdoorException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ConcurrentRequestScopeStateTest {

    @Test
    void settingsRejectNonPositiveCapacity() {
        assertThrows(IllegalArgumentException.class, () -> new ConcurrentRequestScopeSettings(0, false));
        assertThrows(IllegalArgumentException.class, () -> new ConcurrentRequestScopeSettings(-1, false));
    }

    @Test
    void stateInstancesDoNotShareEntriesCountersOrPermits() {
        ConcurrentRequestScopeState first =
                new ConcurrentRequestScopeState(new ConcurrentRequestScopeSettings(2, true));
        ConcurrentRequestScopeState second =
                new ConcurrentRequestScopeState(new ConcurrentRequestScopeSettings(2, true));

        Object key = new Object();
        ConcurrentRequestScopeEntry entry = new ConcurrentRequestScopeEntry(1);
        assertTrue(first.tryAcquireCapacity());
        assertEquals(null, first.putEntryIfAbsent(key, entry));
        long firstConversationId = first.nextConversationSequence();

        assertEquals(1, first.activeEntryCount());
        assertEquals(1, first.availableCapacity());
        assertEquals(0, second.activeEntryCount());
        assertEquals(2, second.availableCapacity());

        long secondConversationId = second.nextConversationSequence();
        assertEquals(1, firstConversationId);
        assertEquals(1, secondConversationId);
        assertNotEquals(first, second);
    }

    @Test
    void clearForTestingIsUnavailableUnlessEnabled() {
        ConcurrentRequestScopeState state =
                new ConcurrentRequestScopeState(new ConcurrentRequestScopeSettings(1, false));

        assertThrows(ConcurrentRequestScopeBackdoorException.class, state::clearForTesting);
    }

    @Test
    void clearForTestingClearsEntriesCounterAndCapacityWhenEnabled() {
        ConcurrentRequestScopeState state =
                new ConcurrentRequestScopeState(new ConcurrentRequestScopeSettings(2, true));
        Object key = new Object();
        ConcurrentRequestScopeEntry entry = new ConcurrentRequestScopeEntry(1);

        assertTrue(state.tryAcquireCapacity());
        assertEquals(null, state.putEntryIfAbsent(key, entry));
        assertEquals(1, state.nextConversationSequence());
        assertEquals(1, state.activeEntryCount());
        assertEquals(1, state.availableCapacity());

        state.clearForTesting();

        assertEquals(0, state.activeEntryCount());
        assertEquals(2, state.availableCapacity());
        assertEquals(1, state.nextConversationSequence());
        assertTrue(state.capacityInvariantHolds());
    }

    @Test
    void capacityInvariantHelperReflectsActiveEntriesAndPermits() {
        ConcurrentRequestScopeState state =
                new ConcurrentRequestScopeState(new ConcurrentRequestScopeSettings(1, true));
        Object key = new Object();
        ConcurrentRequestScopeEntry entry = new ConcurrentRequestScopeEntry(1);

        assertTrue(state.capacityInvariantHolds());
        assertTrue(state.tryAcquireCapacity());
        assertEquals(null, state.putEntryIfAbsent(key, entry));

        assertTrue(state.capacityInvariantHolds());
        assertTrue(state.removeEntryIfSame(key, entry));
        state.releaseCapacity();
        assertTrue(state.capacityInvariantHolds());
    }
}
