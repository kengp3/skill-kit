"""Pure native-turn attribution for development evaluations; no process execution."""
import math


class TrialControl:
    def __init__(self, *, started_at, wall_seconds):
        if (not isinstance(started_at, (int, float)) or isinstance(started_at, bool)
                or not math.isfinite(started_at) or started_at < 0
                or not isinstance(wall_seconds, (int, float)) or isinstance(wall_seconds, bool)
                or not math.isfinite(wall_seconds) or wall_seconds <= 0
                or not math.isfinite(started_at + wall_seconds)):
            raise ValueError('finite monotonic start and positive wall limit required')
        self._deadline = started_at + wall_seconds
        self._last_now = started_at
        self.thread_id = None
        self.turn_id = None
        self.outcome = 'not_started'
        self.writers_stopped = None
        self._completions = {}
        self._bound_turns = set()
        self._cancel_requested = False

    def bind(self, thread_id, turn_id):
        if self.thread_id is not None:
            raise ValueError('use resume for a continuation; original deadline remains')
        if (not isinstance(thread_id, str) or not thread_id
                or not isinstance(turn_id, str) or not turn_id):
            raise ValueError('nonempty thread and turn IDs required')
        self.thread_id = thread_id
        self.turn_id = turn_id
        self._bound_turns.add(turn_id)
        self.outcome = self._completions.get((thread_id, turn_id), 'running')

    def observe(self, message):
        if not isinstance(message, dict) or message.get('method') != 'turn/completed':
            return
        params = message.get('params')
        if not isinstance(params, dict):
            return
        turn = params.get('turn')
        if not isinstance(turn, dict):
            return
        thread_id, turn_id = params.get('threadId'), turn.get('id')
        status = turn.get('status')
        if (not isinstance(thread_id, str) or not thread_id
                or not isinstance(turn_id, str) or not turn_id
                or status not in ('completed', 'failed', 'interrupted')):
            return
        previous = self._completions.get((thread_id, turn_id))
        if previous is not None and previous != status:
            status = 'unknown'
        self._completions[thread_id, turn_id] = status
        if (thread_id, turn_id) == (self.thread_id, self.turn_id):
            if self.outcome != status:
                self.writers_stopped = None
            self.outcome = status

    @property
    def deadline(self):
        return self._deadline

    def remaining(self, *, now):
        if (not isinstance(now, (int, float)) or isinstance(now, bool)
                or not math.isfinite(now) or now < self._last_now):
            raise ValueError('monotonic finite time required')
        self._last_now = now
        return max(0, self._deadline - now)

    def disconnected(self):
        if self.outcome == 'running':
            self.outcome = 'unknown'
            self.writers_stopped = None

    def request_cancel(self):
        self._cancel_requested = True
        self.disconnected()

    def reconcile_readback(self, readback):
        if not isinstance(readback, dict):
            return False
        thread = readback.get('thread')
        turns = (readback.get('turns', thread.get('turns'))
                 if isinstance(thread, dict) else None)
        if (not isinstance(thread, dict) or thread.get('id') != self.thread_id
                or not isinstance(turns, list)):
            return False
        matching = [turn for turn in turns
                    if isinstance(turn, dict) and turn.get('id') == self.turn_id]
        if len(matching) != 1:
            return False
        status = matching[0].get('status')
        if status not in ('completed', 'failed', 'interrupted', 'inProgress'):
            return False
        self.outcome = 'running' if status == 'inProgress' else status
        self.writers_stopped = None
        if status == 'inProgress':
            self._completions.pop((self.thread_id, self.turn_id), None)
        else:
            self._completions[self.thread_id, self.turn_id] = status
        return True

    def confirm_writers_stopped(self, stopped):
        """Caller supplies a fresh liveness check; a turn status is not that evidence."""
        if type(stopped) is not bool:
            raise ValueError('explicit writer liveness result required')
        self.writers_stopped = stopped

    def resume(self, turn_id, *, now, allow_after_cancel=False):
        if self._cancel_requested and allow_after_cancel is not True:
            raise ValueError('explicit continuation authorization required after cancellation')
        if (self.outcome not in ('failed', 'interrupted')
                or self.writers_stopped is not True):
            raise ValueError('reconcile the prior turn and confirm writers stopped first')
        if (not isinstance(turn_id, str) or not turn_id
                or turn_id in self._bound_turns):
            raise ValueError('a new continuation turn ID is required')
        if self.remaining(now=now) <= 0:
            raise ValueError('original trial deadline expired')
        self.turn_id = turn_id
        self._bound_turns.add(turn_id)
        self._cancel_requested = False
        self.outcome = self._completions.get((self.thread_id, turn_id), 'running')
        self.writers_stopped = None
