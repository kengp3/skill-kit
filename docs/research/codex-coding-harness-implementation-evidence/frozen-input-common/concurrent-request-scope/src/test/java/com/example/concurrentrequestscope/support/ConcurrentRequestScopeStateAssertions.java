package com.example.concurrentrequestscope.support;

import com.example.concurrentrequestscope.internal.ConcurrentRequestScopeState;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public final class ConcurrentRequestScopeStateAssertions {

    private ConcurrentRequestScopeStateAssertions() {
    }

    public static void assertScopeState(ConcurrentRequestScopeState state,
            long expectedActiveEntries,
            int expectedAvailableCapacity) {
        assertEquals(expectedActiveEntries, state.activeEntryCount());
        assertEquals(expectedAvailableCapacity, state.availableCapacity());
        assertTrue(state.capacityInvariantHolds());
    }

    public static void assertBaseline(ConcurrentRequestScopeState state) {
        assertScopeState(state, 0, state.settings().maxActiveRequests());
    }
}
