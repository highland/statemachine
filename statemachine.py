"""
    A full-featured framework for a Finite State Machine written in python.
    Inspired by "A Crash Course in UML State Machines" by Miro Samek, Quantum Leaps, LLC.
    https://classes.soe.ucsc.edu/cmpe013/Spring11/LectureNotes/A_Crash_Course_in_UML_State_Machines.pdf
"""
from typing import Iterable, Callable, Dict, Set, NamedTuple


# noinspection PyCallingNonCallable
class State:
    """
    A State (an extended state) captures an aspect of the system's history
    and provides a context for the response of the system to events.
    """

    def __init__(self,
                 name: str,
                 entry_action: Callable = None,
                 exit_action: Callable = None,
                 end_state: bool = False,
                 ):
        super().__init__()
        self.name = name
        self._entry_action = entry_action
        self._exit_action = exit_action
        self.is_end_state = end_state

    def do_entry(self):
        if self._entry_action:
            self._entry_action()

    def do_exit(self):
        if self._exit_action:
            self._exit_action()

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return 'State object named {0}.'.format(self.name)


Event = str
""" type alias:  Event is represented by a string """

Response = NamedTuple('Response',
                      [('next_state', State), ('action', Callable[..., None]),
                       ('guard_condition', Callable[..., bool])])
"""
    action may optionally take parameters supplied with the event
    guard_condition should return False if the transition is to be disabled
"""


# noinspection PyCallingNonCallable
class StateMachine(State):
    """
    An implementation of a FSM (Finite State Machine).
    """

    def __init__(self,
                 name: str,
                 event_source: Iterable[Event],
                 initial_state: State = State('initial'),
                 initial_action: Callable = None,
                 end_action: Callable = None
                 ):
        super().__init__(name)
        self._event_source = event_source
        self._current_state = initial_state
        self._initial_action = initial_action
        self._end_action = end_action
        self._states = {initial_state}  # type: Set[State]
        self._state_table = {}  # type: Dict[Event, Dict[State, Response]]
        self._machine_data = {}  # data used by actions and event ignore functions

    def add_state(self, state: State):
        self._states.add(state)

    def add_event(self, event: Event):
        if event not in self._state_table:
            self._state_table[event] = {}  # Dict[State, Response]

    def add_table_entry(self, event: Event, state: State, response: Response):
        self.add_event(event)
        self.add_state(state)
        self._state_table[event][state] = response

    def run(self):
        if self._initial_action:
            self._initial_action()
        for event, parameters in self._event_source:
            required_response = self._state_table.get(event).get(self._current_state)
            if required_response:
                next_state, action, guard_condition = required_response
                if guard_condition and not guard_condition():  # guard_condition function supplied which returns False
                    continue
                self._current_state.do_exit()
                self._current_state = next_state
                if action:
                    action(parameters)
                self._current_state.do_entry()
            if self._current_state.is_end_state:
                break
        if self._end_action:
            self._end_action()

    def __repr__(self):
        return 'Finite State Machine object named {0}.'.format(self.name)

